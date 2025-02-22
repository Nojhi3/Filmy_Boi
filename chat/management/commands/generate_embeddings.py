import chromadb
from sentence_transformers import SentenceTransformer
from django.core.management.base import BaseCommand
from chat.models import MovieDialogue
from tqdm import tqdm

# Load BGE model for embeddings
embedding_model = SentenceTransformer("BAAI/bge-small-en")

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection in ChromaDB
collection = chroma_client.get_or_create_collection("movie_dialogues")

class Command(BaseCommand):
    help = "Generate embeddings for movie dialogues and store them in ChromaDB."

    def handle(self, *args, **kwargs):
        dialogues = MovieDialogue.objects.all()
        if not dialogues.exists():
            self.stdout.write("❌ No dialogues found in the database.")
            return

        self.stdout.write(f"Generating embeddings for {dialogues.count()} dialogues...")

        for dialogue in tqdm(dialogues):
            dialogue_text = dialogue.dialogue.strip()
            character = dialogue.character.lower()
            movie = dialogue.movie

            embedding = self.get_embedding(dialogue_text)

            # Store in ChromaDB
            collection.add(
                ids=[str(dialogue.id)],
                embeddings=[embedding.tolist()],
                metadatas=[{"character": character, "movie": movie, "dialogue": dialogue_text}]
            )

        self.stdout.write("✅ Embeddings stored successfully in ChromaDB!")

    def get_embedding(self, text):
        """Generate text embedding using BGE"""
        return embedding_model.encode(text, convert_to_numpy=True)

import requests
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from chat.models import MovieDialogue
from django_ratelimit.decorators import ratelimit
from chat.tasks import generate_response
import redis
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0

# Initialize Redis Client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
# Load BGE model for embeddings
embedding_model = SentenceTransformer("BAAI/bge-small-en")

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("movie_dialogues")

TOGETHER_AI_API_KEY = "8b283a377efef633e1ca5ab57de868d6ac25b1af08c8ecd7a2b41a79ede116ef"
TOGETHER_AI_ENDPOINT = "https://api.together.xyz/v1/chat/completions"

def get_embedding(text):
    """Generate text embedding using BGE"""
    return embedding_model.encode(text, convert_to_numpy=True)

def retrieve_similar_dialogue(user_message, top_k=1):
    """Retrieve the most relevant movie dialogue from ChromaDB with caching"""
    
    cache_key = f"dialogue:{user_message.lower()}"
    
    # Check if response is cached
    cached_response = redis_client.get(cache_key)
    if cached_response:
        print("✅ Cache Hit!")
        return cached_response.decode("utf-8")
    
    print("❌ Cache Miss! Performing ChromaDB Search...")
    
    query_embedding = get_embedding(user_message).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if results["ids"][0]:
        best_match = results["metadatas"][0][0]["dialogue"]
        
        # Store in Redis for faster retrieval
        redis_client.setex(cache_key, 3600, best_match)  # Cache for 1 hour
        return best_match

    return None  # No relevant match found


@csrf_exempt
@api_view(['POST'])
@ratelimit(key="ip", method="POST", block=True)
def chat_with_character(request):
    data = request.data
    character = data.get("character", "").strip().lower()
    user_message = data.get("user_message", "").strip()

    if not character or not user_message:
        return Response({"error": "Character and user_message are required."}, status=400)

    retrieved_dialogue = retrieve_similar_dialogue(user_message)

    task = generate_response.delay(character, user_message, retrieved_dialogue)
    return Response({"task_id": task.id, "status": "processing"})
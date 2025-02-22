from django.core.management.base import BaseCommand
from chat.models import MovieDialogue
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
from fuzzywuzzy import fuzz

BASE_URL = "https://www.imsdb.com/scripts/"
MOVIES = ["Corpse-Bride", "Pulp-Fiction", "Hangover,-The"]  # Add more movies

class Command(BaseCommand):
    help = "Scrape IMSDb for movie scripts and populate the database."

    def handle(self, *args, **kwargs):
        for movie in MOVIES:
            # ✅ Check if the movie already exists in the database
            if MovieDialogue.objects.filter(movie=movie).exists():
                self.stdout.write(f"Skipping {movie}: Already in database ✅")
                continue  # Skip this movie

            self.stdout.write(f"Scraping {movie}... ⏳")
            script = self.get_script(movie)

            if script:
                dialogues = self.extract_dialogues(script, movie)
                self.stdout.write(f"Extracted {len(dialogues)} dialogues from {movie} 🎬")
                self.save_to_database(dialogues)
                time.sleep(3)  # Respect rate limits

    def get_script(self, movie_name):
        """Fetch and parse movie script from IMSDb."""
        url = f"{BASE_URL}{movie_name}.html"
        response = requests.get(url)

        if response.status_code != 200:
            self.stdout.write(f"❌ Failed to fetch {movie_name}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        pre_tags = soup.find_all("pre")

        if not pre_tags:
            self.stdout.write(f"⚠️ Script format not found for {movie_name}")
            return None

        return pre_tags[0].get_text()

    def extract_dialogues(self, script, movie_name):
        """Extract character dialogues from script text."""
        dialogues = []
        current_character = None

        lines = script.split("\n")
        for line in lines:
            line = line.strip()

            # ✅ Detect character names (typically UPPERCASE)
            if re.match(r"^[A-Z ]+$", line) and 1 < len(line) < 25:
                current_character = line.strip().lower()  # Store in lowercase

            elif current_character and line:
                clean_dialogue = line.strip().replace("\n", " ").replace("  ", " ")
                dialogues.append((current_character, movie_name, clean_dialogue))

        return dialogues

    def save_to_database(self, dialogues):
        """Save extracted dialogues to PostgreSQL if they do not exist."""
        for character, movie, dialogue in tqdm(dialogues, desc="Saving to DB"):
            character = character.strip().lower()  # Ensure lowercase consistency
            dialogue = dialogue.strip()

            # ✅ Check for duplicates using fuzzy matching
            existing_dialogues = MovieDialogue.objects.filter(character=character, movie=movie)
            if any(fuzz.ratio(d.dialogue, dialogue) > 90 for d in existing_dialogues):
                continue  # Skip similar dialogue

            MovieDialogue.objects.create(character=character, movie=movie, dialogue=dialogue)

        self.stdout.write(f"✅ Database Updated with {len(dialogues)} dialogues!")

from django.db import models

class MovieDialogue(models.Model):
    character = models.CharField(max_length=100)
    movie = models.CharField(max_length=200)
    dialogue = models.TextField()

    def __str__(self):
        return f"{self.character} - {self.movie}: {self.dialogue[:50]}..."


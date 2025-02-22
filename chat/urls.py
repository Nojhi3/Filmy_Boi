from django.urls import path
from .views import chat_with_character

urlpatterns = [
    path("chat/", chat_with_character, name="chat_with_character"),
]

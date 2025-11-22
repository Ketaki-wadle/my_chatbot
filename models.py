from django.db import models

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_reply = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class KnowledgeEntry(models.Model):
    title = models.CharField(max_length=255)
    problem_description = models.TextField()
    solution_text = models.TextField()
    tags = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=50, default='manual')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Conversation(models.Model):
    session_id = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def last_messages(self, n=10):
        return self.messages.order_by('-created_at')[:n]

    def __str__(self):
        return f"Conversation {self.session_id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=50)
    text = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_read(self):
        # placeholder
        return True

    def __str__(self):
        return f"Message {self.id} ({'bot' if self.is_bot else 'user'})"

class Feedback(models.Model):
    message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.SET_NULL)
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.SET_NULL)
    rating = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - {self.rating}"

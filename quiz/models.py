from django.db import models

class QuizAttempt(models.Model):
    score = models.IntegerField(default=0)
    current_index = models.IntegerField(default=0)
    questions_data = models.JSONField(default=list)
    user_answers = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.id} - Score: {self.score}"

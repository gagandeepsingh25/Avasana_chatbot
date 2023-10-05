from django.db import models

# Create your models here.

from django.db import models

class QuestionAnswer(models.Model):
    question = models.TextField(null=True)
    answer = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)



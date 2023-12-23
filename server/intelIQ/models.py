from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    likes = models.ManyToManyField(User, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    
    def __str__(self):
        return str(self.title)
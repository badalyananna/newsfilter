from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length = 30)
    key_words = models.TextField()
    ignor_words = models.TextField(default="", blank = True)
    unread_pieces = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, * args, ** kwargs):
        super().__init__(*args,**kwargs)
        self.unread_pieces = len(NewsPiece.objects.filter(topics_assigned = self, unread = True))

    def __str__(self):
        return self.name

class Website(models.Model):
    name = models.CharField(max_length = 30)
    rss = models.CharField(max_length = 255)
    unread_pieces = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, * args, ** kwargs):
        super().__init__(*args,**kwargs)
        self.unread_pieces = len(NewsPiece.objects.filter(website = self, unread = True))

    def __str__(self):
        return self.name

class NewsPiece(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255)
    published = models.DateTimeField()
    description = models.TextField()
    link = models.TextField()
    chosen = models.BooleanField(default = False)
    topics_filtered = models.ManyToManyField(Topic, related_name='filtered') # the topic assigned when filtering
    filtered = models.BooleanField(default = False)
    important = models.BooleanField(default = False)
    unread = models.BooleanField(default = True)
    displayed = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topics_assigned = models.ManyToManyField(Topic, related_name='assigned') # the topics modified later by the user

    def __str__(self):
        return self.title

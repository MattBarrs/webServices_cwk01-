from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Authors(models.Model):
    author_username = models.ForeignKey(User, on_delete = models.CASCADE)
    author_name = models.CharField (max_length=100)

    def __str__(self):
        return self.author_username.username 

class NewsStories(models.Model):
    story_id = models.AutoField(primary_key=True)
        
    story_headline = models.CharField(max_length=64)

    story_author = models.ForeignKey(Authors, on_delete = models.CASCADE)

    # story_date = models.DateField(max_length=100, format='%d/%m/%Y')
    story_date = models.DateField(max_length=100, blank=True,null=True)

    
    categoryChoices =[
        ('pol', 'Politics'),
        ('art','Art News'),
        ('tech','Technology News'),
        ('trivia','Trivial News')
    ]
    story_cat = models.CharField(max_length=10, choices = categoryChoices)


    regionChoices =[
        ('uk','UK'),
        ('eu','European News'),
        ('w','World News'), 
        ]
    story_region = models.CharField(max_length=10,choices = regionChoices)

    story_details = models.CharField(max_length=512)    
    
    		

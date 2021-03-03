from django.contrib import admin

# Register your models here.
from .models import Authors, NewsStories

admin.site.register(Authors)
admin.site.register(NewsStories)
 

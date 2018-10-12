from django.contrib import admin
from .models import ParsingData, UploadData, ImgData, VideoData, Comment

# Register your models here.
admin.register(ParsingData, UploadData, ImgData, VideoData, Comment)(admin.ModelAdmin)
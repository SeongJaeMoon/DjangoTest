from django.contrib import admin
from .models import ParsingData, UploadData, ImgData, VideoData, Comment, BasicStatistic, WordStatistic, Bayesian, ChatBotData

# Register your models here.
admin.register(ParsingData, UploadData, ImgData, VideoData, Comment, BasicStatistic, WordStatistic, Bayesian, ChatBotData)(admin.ModelAdmin)
from django.db import models
from django.utils import timezone
from django import forms
from django.forms import ModelForm
from django.forms import modelform_factory
from django.urls import reverse
from django.shortcuts import redirect

# 유저 정보
class ParsingData(models.Model):
    ids = models.TextField() # 아이디
    total = models.IntegerField(blank=True, null=True) # 총 게시물 수
    profile_img = models.TextField(blank=True, null=True) # 프로필 이미지
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
    	return self.ids

    class Meta:
        verbose_name_plural = 'people'

# 각각의 업로드 링크 정보
class UploadData(models.Model):
    user = models.ForeignKey(ParsingData, on_delete = models.CASCADE)
    link = models.URLField() # 원본 주소 링크
    place = models.TextField(blank=True, null=True) # 장소
    time = models.TextField() # 시간
    like = models.TextField(blank=True, null=True) # 좋아요 
    content = models.TextField(blank=True, null = True) # 사용자 글
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
    	return self.link

# 업로드 데이터 이미지 정보
class ImgData(models.Model):
    list_img = models.ForeignKey(UploadData, on_delete = models.CASCADE) # 업로드 링크
    imgs = models.TextField(blank=True, null=True) # 이미지 목록
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.imgs

# 업로드 비디오 정보
class VideoData(models.Model):
    list_video = models.ForeignKey(UploadData, on_delete = models.CASCADE) # 업로드 링크
    vidoes = models.TextField(blank=True, null=True) # 비디오 목록
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vidoes

# 업로드 코멘트 정보
class Comment(models.Model):
    comm = models.ForeignKey(UploadData, on_delete = models.CASCADE) # 업로드 링크
    com_user = models.TextField(blank=True, null=True) # 코멘트 유저
    comment = models.TextField(blank=True, null=True) # 코멘트
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "({}){}".format(self.com_user, self.comment)

# 기본 통계 저장할 모델
class BasicStatistic(models.Model):
    ids = models.TextField() # 유저 아이디
    place = models.TextField(blank=True, null=True) # 장소
    users = models.TextField(blank=True, null=True) # 많이 댓글단 유저
    hashtag = models.TextField(blank=True, null=True) # 많이 나온 해시태그
    wording = models.TextField(blank=True, null=True) # 많이 나온 단어
    time_days = models.TextField(blank=True, null=True) # 월당 포스팅 수
    time_hours = models.TextField(blank=True, null=True) # 시간당 포스팅 수
    likes = models.TextField(blank=True, null=True) # 좋아요 수
    moving_avg = models.TextField(blank=True, null=True) # 좋아요 이동 평균
    replies = models.IntegerField(blank=True, null=True) # 총 댓글 수
    reply_user = models.IntegerField(blank=True, null=True) # 댓글단 사용자 총합

    def __str__(self):
        return self.ids

    def get_absolute_url(self): # redirect 시 활용
        return reverse('parsed_data:ids', args=[self.ids])



        
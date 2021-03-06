from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ParsingData, UploadData, ImgData, VideoData, Comment, BasicStatistic
from django.template import loader
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from analysis import times_hours_key, times_hours_val, times_value, times_date 
# Class View 변경 필요

# Main
def index(request):
    auto_id = [u.ids for u in ParsingData.objects.all()]
    parsing = ParsingData.objects.get(ids = 'tw.momoring') # 사용자 정보
    basicstat = BasicStatistic.objects.get(ids = 'tw.momoring')    
    return render(request, 'parsed_data/index.html', {'parsing': parsing, 
                                                      'basicstat': basicstat,
                                                      'users':auto_id})                                 
# User Search
def search_user(request):
    ids = request.POST.get('ids', None)
    auto_id = [u.ids for u in ParsingData.objects.all()]
    parsing = ParsingData.objects.get(ids = ids.strip()) # 사용자 정보
    basicstat = BasicStatistic.objects.get(ids = ids.strip())
    t = loader.get_template('parsed_data/index.html')
    c = {'parsing': parsing, 'basicstat': basicstat, 'users':auto_id}
    return HttpResponse(t.render(c, request))

# ajax -> data reloading (게시물 월, 시간)
@require_POST # 해당 뷰는 POST method 만 받는다.
def change_line(request):
    # ajax 통신을 통해서 template에서 POST 
    ids = request.POST.get('ids', None)
    val = request.POST.get('val', None)
    hour_day = get_object_or_404(BasicStatistic, ids=ids)
    if val == '2':
        # 시간 기준으로 변경
        context = hour_day.time_hours
        key = times_hours_key(context)
        value = times_hours_val(context)
    else:
        # 날짜 기준으로 변경
        context = hour_day.time_days
        key = times_date(context)
        value = times_value(context)
    data = {'key': key, 'value': value}
    return JsonResponse(data)

# More Analysistic
def analysis(request, ids):
    parsing = ParsingData.objects.get(ids = ids.strip()) # 사용자 정보
    return render(request, 'parsed_data/analysis.html', {'parsing':parsing})

# Gallery
def gallery(request, ids):
    auto_id = [u.ids for u in ParsingData.objects.all()] # 전체 유저 정보
    uid = ParsingData.objects.get(ids = ids) # id에 해당하는 유저 정보
    result = [] # 결과
    for up in UploadData.objects.filter(user = uid).order_by('-created_at'): # 유저 정보에 해당하는 포스팅 목록
        for i in ImgData.objects.filter(list_img = up).order_by('-created_at'): # 실제 이미지 연결 주소
            result.append(i)

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 35)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    return render(request, 'parsed_data/gallery.html', {'users':auto_id, 'parsing':uid, 'images':images})

# Video
def video(request, ids):
    auto_id = [u.ids for u in ParsingData.objects.all()]
    uid = ParsingData.objects.get(ids = ids) # id에 해당하는 유저 정보
    result = [] # 결과
    for up in UploadData.objects.filter(user = uid): # 유저 정보에 해당하는 포스팅 목록
        for i in VideoData.objects.filter(list_video = up): # 실제 비디오 연결 주소
            result.append(i)
    page = request.GET.get('page', 1)
    paginator = Paginator(result, 35)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)
    return render(request, 'parsed_data/video.html', {'users':auto_id, 'parsing':uid, 'videos':videos})



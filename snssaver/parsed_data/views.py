from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ParsingData, UploadData, ImgData, VideoData, Comment, BasicStatistic, ChatBotData
from django.template import loader
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from analysis import times_hours_key, times_hours_val, times_value, times_date, get_model, get_bayese
from firebase import Firebase
from chatbot import make_replies
import json
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
    is_none = 1
    if not (ids.strip() in auto_id):
        ids = 'tw.momoring'
        is_none = 0
    parsing = ParsingData.objects.get(ids = ids.strip()) # 사용자 정보        
    basicstat = BasicStatistic.objects.get(ids = ids.strip())
    t = loader.get_template('parsed_data/index.html')
    c = {'parsing': parsing, 'basicstat': basicstat, 'users':auto_id, 'is_none':is_none}

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
    firebase = Firebase()
    map_ret = firebase.get_geocoding(ids)
    return render(request, 'parsed_data/analysis.html', {'parsing':parsing, "map_ret":map_ret})

# Gallery
def gallery(request, ids):
    uid = ParsingData.objects.get(ids = ids) # id에 해당하는 유저 정보
    result = [] # 결과
    for up in UploadData.objects.filter(user = uid).order_by('-time'): # 유저 정보에 해당하는 포스팅 목록
        link = str(up.link).split('?')[0]
        if not link in [str(r[2]) for r in result]:
            for i in ImgData.objects.filter(list_img = up).order_by('-created_at'): # 실제 이미지 연결 주소
                result.append([i.imgs, up.time, link])

    page = request.GET.get('page', 1)
    paginator = Paginator(result, 36)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    return render(request, 'parsed_data/gallery.html', {'parsing':uid, 
                                                        'images':images, 
                                                        'length':len(result)})

# Video
def video(request, ids):
    uid = ParsingData.objects.get(ids = ids) # id에 해당하는 유저 정보
    result = [] # 결과
    for up in UploadData.objects.filter(user = uid).order_by('-time'): # 유저 정보에 해당하는 포스팅 목록
        for i in VideoData.objects.filter(list_video = up).order_by('-updated_at'): # 실제 비디오 연결 주소
            result.append(i)
    page = request.GET.get('page', 1)
    paginator = Paginator(result, 36)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    return render(request, 'parsed_data/video.html', {'parsing':uid, 
                                                      'videos':videos, 
                                                      'length':len(result)})

# Comment
def comment(request, ids):
    parsing = ParsingData.objects.get(ids = ids.strip()) # 사용자 정보
    
    user_ret = []
    data_key = []
    data_val = []

    for r in get_model(ids, file_name=''):
        user_ret.append(r[0])
        for v in r[1]:
            data_key.append(str(v[0]).replace('"', '').replace("'", ''))
            data_val.append(v[1])

    re_user_ret = []
    re_data_key = []
    re_data_val = []

    for r in get_model(ids, file_name='re_'):
        re_user_ret.append(r[0])
        for v in r[1]:
            re_data_key.append(str(v[0]).replace('"', '').replace("'", ''))
            re_data_val.append(v[1])

    pn_data = get_bayese(ids)
    pn_times = [p[0] for p in pn_data]
    positive = [p[1]['pos'] for p in pn_data]
    negative = [p[1]['neg'] for p in pn_data]

    return render(request, 'parsed_data/comment.html', {'parsing': parsing,
                                                        'user_ret':user_ret,
                                                        'data_key':data_key,
                                                        'data_val':data_val,
                                                        're_user_ret':re_user_ret,
                                                        're_data_key':re_data_key,
                                                        're_data_val':re_data_val,
                                                        'pn_times':pn_times,
                                                        'positive':positive,
                                                        'negative':negative})


def make_reply(request):
    txt = request.GET.get('txt', None)
    chatdata = get_object_or_404(ChatBotData, name="data01")
    ret = make_replies(txt, chatdata.chat_data)
    data = {'ret': ret}
    return JsonResponse(data)

# Chatbot
def chatbot(request):
    return render(request, 'parsed_data/chatbot.html')
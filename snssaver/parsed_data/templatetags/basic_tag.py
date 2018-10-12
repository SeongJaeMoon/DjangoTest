# basicstat template
from django import template
import re
from django.utils.safestring import mark_safe
from datetime import datetime
import dateutil.parser

register = template.Library()

@register.filter # 많이 나온 단어 리스트
def wording_data(data):
    result = data.replace('[', '').replace(']','')
    return result

@register.filter 
def hash_tag(data): # 사용자, 해시태그
    result = ''
    m = re.findall('#([0-9a-zA-Z가-힣]*)', data)
    key = str(m[:]).replace('[', '').replace(']', '')
    value = ''
    for m in re.findall('\d', data):
        value = value + m 

    result += '<span><b class="value">' + value + '</b>Most HashTag</span>'
    result += '<em>#' + key + '</em>'
    return mark_safe(result)

@register.filter
def users_data(data): # 많이 댓글단 유저 정보
    result = ''
    words = re.findall('[a-zA-Z0-9._]+', data)
    digit = [words[w] for w in range(len(words)) if w % 2 == 0]
    words = [words[w] for w in range(len(words)) if w % 2 != 0]
    for i in range(len(words)):
        key, value = words[i], digit[i]
        result += "<tr><td><a href='https://www.instagram.com/"+ value + "' target='_blank'>"+ value +"</a></td><td><span class='label label-info'>"+key+"</span></td></tr>"
    return mark_safe(result)

@register.filter # 총 좋아요 갯수
def likes_data(data):
    print(type(data))
    result = 0
    for m in re.findall('\d', data):
        result += int(m)
    return mark_safe(result)

@register.filter
def mv_data(data): # 좋아요 이동평균 10개 반환
    result = []
    for m in re.findall('([0-9]*\.[0-9]+)', data): 
        result.append(float(m))
    return mark_safe(result[len(result) - 10:])

@register.filter
def times_date(data): # 날짜 반환 -> 10개
    result = []
    dates = re.findall('(\d*\-\d*\-\d*)', data)
    return mark_safe(dates[len(dates)-10:])

@register.filter
def times_value(data): # 날짜에 따른 게시물 수 반환 -> 10개
    digits = [str(d).replace(')','') for d in re.findall('\d*\)', data)]
    digits = [int(d) for d in digits]
    return mark_safe(digits[len(digits)-10:])

@register.filter 
def times_hours_key(data): # 시간 반환
    key_value = re.findall('\d+', data)
    key = [key_value[k] for k in range(0, len(key_value), 2)]
    # key = sorted(key)
    return mark_safe(key)

@register.filter
def times_hours_val(data): # 시간에 따른 게시물 수 반환
    key_value = re.findall('\d+', data)
    val = [int(key_value[k]) for k in range(1, len(key_value), 2)]
    # val = sorted(val)
    return mark_safe(val)

@register.filter
def get_users(data):
    result = str(data).replace('[','').replace(']','').replace("'",'')
    return mark_safe(result)

@register.filter
def get_images(data):
    # result = '<ul class="gallery">'
    # result += '<li class="item"><img src='+ d +'><div class="details"><a href="#myModal" class="action" data-toggle="modal"><i class="fa fa-pencil-square-o"></i></a></div></li>'
    # result += '</ul>'
    result = ''
    for d in [str(i).split("imgs':")[1].replace("}]>", '').replace("'", '').replace('},','').strip() for i in data if i]:
        result += '<a href="#myModal" class="action" data-toggle="modal"><img src='+ d +' style="width: 300px; height:300px;"></a>'
    return mark_safe(result)

@register.filter
def get_videos(data):
    result = ''
    for d in [str(i).split("vidoes':")[1].replace("}]>", '').replace("'", '').replace('},','').strip() for i in data if i]:
        result += '<video preload="none" poster=http://localhost:8000/static/img/loading.jpg width="300" height="300" controls="controls"><source src="' + d + '" type="video/mp4"></video>'
    return mark_safe(result)
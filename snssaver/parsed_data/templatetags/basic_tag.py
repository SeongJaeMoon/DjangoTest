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
    result = 0
    for m in re.findall('\d+', data):
        result += int(m)
    return mark_safe(result)

@register.filter
def mv_data(data): # 좋아요 이동평균 10개 반환
    result = []
    for m in re.findall('([0-9]*\.[0-9]+)', data): 
        result.append(float(m))
    return mark_safe(result[len(result) - 10:])

@register.filter 
def times_hours_key(data): # 시간 반환
    key_value = re.findall('\d+', data)
    key = [key_value[k] for k in range(0, len(key_value), 2)]
    return mark_safe(key)

@register.filter
def times_hours_val(data): # 시간에 따른 게시물 수 반환
    key_value = re.findall('\d+', data)
    val = [int(key_value[k]) for k in range(1, len(key_value), 2)]
    return mark_safe(val)

@register.filter
def get_users(data): # 사용자 정보
    result = str(data).replace('[','').replace(']','').replace("'",'')
    return mark_safe(result)

@register.filter
def get_images(data): # 이미지 정보
    result = ''
    for d in data:
        time = str(dateutil.parser.parse(d[1]))
        result += '<a href="#myModal" class="action" data-toggle="modal"><img alt='+ time +' src='+ d[0] +' style="width: 600px; height:700px;"></a>'
    return mark_safe(result)


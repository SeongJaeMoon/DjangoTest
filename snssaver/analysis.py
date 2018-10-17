import re
from collections import Counter
from datetime import datetime
from konlpy.tag import Okt
from gensim import models, corpora
from gensim.models import word2vec
from collections import Counter
import os
import time
import json
import codecs
import numpy as np 
import pandas as pd
import dateutil.parser
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py 파일 경로를 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snssaver.settings")
# 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만들기
import django
django.setup()
from multiprocessing import cpu_count
from parsed_data.models import ParsingData, UploadData, ImgData, VideoData, Comment, BasicStatistic 

FACTORY = '/Users/moonseongjae/Project_sns/factory/'

# 사용자 기본 통계값
def get_rank(user_id, defualt = 'tw.momoring'):
    result = {}
    if not user_id:
        user_id = defualt
    result['ids'] = user_id
    parsing = ParsingData.objects.get(ids = user_id) # 사용자 정보
    upload = UploadData.objects.all().filter(user = parsing) # 게시물 정보
    comments = [Comment.objects.all().filter(comm = up) for up in upload] # 댓글 정보
    
    place = {}
    content = {}
    like_list = []
    time_list = []
    mth = re.compile('\d')
    # links = [up for up in upload]
    ok = Okt()
    for up in upload:
        p = up.place 
        if p:
            if not (p in place): # 장소 걸러내기
                place[p] = 0
            place[p] += 1
        con = up.content
        if con:
            for noun in ok.pos(con): # 해시태그 걸러내기
                if noun[1] == 'Hashtag':
                    if not (noun[0] in content):
                        content[noun[0]] = 0
                    content[noun[0]] += 1
        likes = ''
        if up.like:
            for m in mth.findall(up.like):
                likes = likes + m
            like_list.append(int(likes)) # 좋아요(좋아요는 정규표현식으로 숫자만 걸러내기)
        time_list.append(dateutil.parser.parse(up.time)) # 시간

    most_hashtag = sorted(content.items(), key=lambda x:x[1], reverse = True) # 가장 많이 나온 글쓴이 해시태그
    most_place = sorted(place.items(), key=lambda x:x[1], reverse = True) # 가장 많이 나온 장소
    
    users = {}
    comment_list = []
    # 가장 많이 쓴 사람의 글도 함께 가져와야 된다!!
    for com in comments:
        for c in com:
            user = c.com_user
            if not (user in users):
                users[user] = 0
            users[user] += 1 # 가장 많이 글 쓴 사용자
    users = sorted(users.items(), key=lambda x:x[1], reverse=True)             
    
    wording = {}
    for most in comments: 
        for m in most:
            for noun in ok.pos(m.comment):
                if noun[1] == 'Noun': # and len(noun[0]) > 1
                    if not (noun[0] in wording):
                        wording[noun[0]] = 0
                    wording[noun[0]] += 1
    wording = sorted(wording.items(), key=lambda x:x[1], reverse=True)

    if most_place: # 장소는 없을 수도 있음!
            result['place'] = str(most_place)
    else:
        result['place'] = ''
    
    result['hash'] = most_hashtag[:1]
    result['wording'] = str(wording[:5]) # 코멘트에서 가장 많이 나온 단어
    high_users = ["{}:{}".format(k, v) for k, v in users[:5]] # 상위 5명 가져오기
    result['users'] = str(high_users)
    result['likes'] = str(like_list)
    result['mv'] = get_mv(like_list, 10) # 구간 변경!
    time_avg = get_time(time_list)
    days = time_avg[0]
    days = sorted(days.items(), key=lambda  x: x[1], reverse=True)
    hours = time_avg[1]
    hours = sorted(hours.items(), key=lambda  x: x[1], reverse=True)
    result['time_days'] = str(days) 
    result['time_hours'] = str(hours)
    replies = 0
    for v in users:
        replies += v[1]
    result['replies'] = replies # 총 댓글 수
    result['reply_user'] = len(users) # 댓글 단 사용자 
    return result

# [[{월:값, 월:값, ...}, {시간:값, 시간:값, ...}]]
# 2018-10-05 11:26:25+00:00
def get_time(time_list):
    result = []
    days = {}
    hours = {}
    for time in time_list:    
        tday = time.strftime('%Y-%m-%d')
        th = time.strftime('%H')
        if not (tday in days):
            days[tday] = 0
        days[tday] += 1
        if not (th in hours):
            hours[th] = 0
        hours[th] += 1
    result.append(days)
    result.append(hours)
    return result

# 이동 평균 구하기 (data 리스트 값을 받아와서, M구간 당 이동평균을 구함)
def get_mv(data, m):
    result = []
    #이동 평균을 구할 값들의 총 수
    n = len(data)
    # 이동 평균을 구하기 위해 각 구간당 합계
    part_sum = 0
    # 0번째 인덱스(값)부터 M-1인덱스(값)까지의 값을 합함
    for i in range(m-1):
        # 0~3번 째의 값들에 합을 구함
        part_sum += data[i]
    # 4번째 인덱스(값)부터 시작해서 전체 배열(값)의 크기까지 반복
    for i in range(m-1, n):
        # 각 구간당 합계 구하기
        part_sum += data[i]
        # 합계를 M으로 나눠서(평균) 결과 값에 순서대로 할당
        result.append(part_sum/m)
        # 합계에서 기존의 첫 번째 빼주기
        part_sum -= data[i-m+1]
    return result

# 사용자 기본 통계값 저장 -> isUpdate: 사용자 통계 값 변경 되었을 경우 사용
def save_rank(data, is_update = False):
    try:
        if not is_update:
            BasicStatistic.objects.create(ids=data['ids'], 
                                          hashtag=data['hash'],
                                          wording=data['wording'],
                                          users=data['users'],
                                          place=data['place'],
                                          time_days=data['time_days'],
                                          time_hours=data['time_hours'],
                                          likes=data['likes'],
                                          moving_avg=data['mv'],
                                          replies=data['replies'],
                                          reply_user=data['reply_user'])
        else:
            # 업데이트 -> 사용자 게시물 수 비교 후 추가 데이터 가져와서 update   
            statistic = BasicStatistic.objects.get(ids=data['ids'])
            statistic.hashtag = data['hash']
            statistic.wording = data['wording']
            statistic.users = data['users']
            statistic.place = data['place']
            statistic.time_days = data['time_days']
            statistic.time_hours = data['time_hours']
            statistic.likes = data['likes']
            statistic.moving_avg = data['mv']
            statistic.replies = data['replies']
            statistic.reply_user = data['reply_user']
            statistic.save()
    except Exception as e:
        print(e)
    finally:
        print('analysis done-> ', data['ids'])

# 날짜 반환 -> 10개
def times_date(data): 
    result = []
    dates = re.findall('(\d*\-\d*\-\d*)', data)
    return dates[:10]
# 날짜에 따른 게시물 수 반환 -> 10개
def times_value(data):
    digits = [str(d).replace(')','') for d in re.findall('\d*\)', data)]
    digits = [int(d) for d in digits]
    return digits[:10]
# 시간 반환
def times_hours_key(data):
    key_value = re.findall('\d+', data)
    key = [key_value[k] for k in range(0, len(key_value), 2)]
    return key
# 시간에 따른 게시물 수 반환
def times_hours_val(data):
    key_value = re.findall('\d+', data)
    val = [int(key_value[k]) for k in range(1, len(key_value), 2)]
    return val

# 사용자가 자주 태그한 장소 Top10 장소 반환
def get_places(data):
    keys = [str(d).replace("('", '').replace("',", '').strip() for d in re.findall("\('[0-9a-zA-Z가-힣\!@#$%^&\* ]+',", data)]    
    return keys[:10] # 장소 1~10

# 사용자가 자주 태그한 장소 Top10 값 반환
def get_places_value(data):
    values = [str(d).replace('),','') for d in re.findall('\d*\),', data)]    
    return values[:10] # 값 1~10

# 코멘트 Word Embedding 
''' 
keyword: User ID
Update: Train Data 추가
init: 초기화 여부
is_comment: 사용자 전용 코멘트 <-> 댓글 구분
file_name: 사용자 전용 코멘트 <-> 댓글 구분 파일 이름
'''
def word_embedding(keyword, init=True, is_comment=False, file_name=''):
    result = [] # Word2Vec 저장 결과 리스트 선언
    queries = {} # 시용자의 코멘트 내용 중 많이 나온 단어를 계산할 딕셔너리 선언
    t = Okt()
    uid = ParsingData.objects.get(ids=keyword) # id 가져오기
    upload = UploadData.objects.filter(user=uid) # upload 정보 가져오기
    
    # 불 필요한 단어는 제거하고 리스트 생성
    if is_comment:
        content = []
        for up in upload: # upload 정보 가져오기
            temp = [str(co.comment).replace("'"+ keyword +"',", '').replace(' ', '') for co in Comment.objects.filter(comm=up)]
            for c in temp:
                content.append(c)
    else:
        content = [str(up.content).replace("'"+ keyword +"',", '').replace(' ', '') for up in upload]
          
    for con in content:
        words = t.pos(con, stem=True, norm=True)
        r = []
        for word in words:
            if not (word[1] in ["Josa", "Eomi", "Punctuation"]) and len(word[0]) > 1:
                r.append(word[0])
                if not (word[0] in queries):
                    queries[word[0]] = 0
                queries[word[0]] += 1

        rtemp = (" ".join(r)).strip()
        result.append(rtemp)
    
    temp_file = FACTORY + file_name + keyword+'.wakati' # LineSentence로 읽어들일 데이터 저장
    model_file = FACTORY + file_name + keyword+'.model' # 실제 학습에 사용되는 모델 파일 
    
    if init: # 모델 초기화(저장)
        with open(temp_file, 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(result))
        data = word2vec.LineSentence(temp_file)
        model = word2vec.Word2Vec(data, size=200, window=10, workers=cpu_count(), min_count=2, iter=100, sg=1)
        model.save(model_file)
        print('init done')
    else:
        # 모델 트레이닝 업데이트
        print('update done')

    print('temp size: ', os.path.getsize(temp_file)/1024, 'kb')
    print('model size: ', os.path.getsize(model_file)/1024, 'kb')

    model = word2vec.Word2Vec.load(model_file)
    queries = sorted(queries.items(), key=lambda x:x[1], reverse=True)
    ret = []
    try:
        for q in queries[:5]:
            print('-----'+q[0]+'-----')
            print(model.wv.most_similar(positive=[str(q[0])]))
            print('----------')
            ret.append({q[0]:model.wv.most_similar(positive=[str(q[0])])})
    except KeyError as e:
        print(e)
    return ret

if __name__ == "__main__":
    start_time = time.time()
    # 주기적으로 재분석 필요(DB 업데이트) -> DB 업데이트 파악
    auto_id = [str(user.ids).strip() for user in ParsingData.objects.all()]
    for i in auto_id:
        if not (i == 'ji_na9'):
            word_embedding(i, init=True, is_comment=False)
            word_embedding(i, init=True, is_comment=True, file_name='re_')
    
    # result1 = word_embedding('ji_na9', init=False, is_comment=False)
    # result2 = word_embedding('ji_na9', init=False, is_comment=True, file_name='re_')
    # print(result1)
    # print(result2)
    print("--- %s seconds ---" % (time.time() - start_time))



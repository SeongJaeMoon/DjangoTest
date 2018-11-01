import os, re, json, random
import time
from konlpy.tag import Okt
from bs4 import BeautifulSoup
import urllib.request
import requests
import codecs
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py 파일 경로를 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snssaver.settings")
# 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만들기
import django
django.setup()
from parsed_data.models import ParsingData, UploadData, Comment, ChatBotData

content_dict_file = "c-chatbot-data.json"
reply_dict_file = "r-chatbot-data.json"
# dic = {}
# ok = Okt()

# 학습을 위한 문자열 DB에서 추출(초기화)
def get_train_from_db():
    print('코멘트 읽어들이기 시작!')
    start_time = time.time()
    ret = []
    for p in ParsingData.objects.all():
        for u in UploadData.objects.filter(user=p):
            txt = str(u.content)
            if not txt == '':
                ret.append(txt)
    print("--- %s seconds ---" % (time.time() - start_time))
    return ret

# 저장되어 있지 않은 문자열 저장
def register_dic(words, dic):
    if len(words) == 0:return
    tmp = ["@"]
    for i in words:
        word = i[0]
        if word == "" or word == "\r\n" or word == "\n": continue
        tmp.append(word)
        if len(tmp) < 3: continue
        if len(tmp) > 3: tmp = tmp[1:]
        set_word3(dic, tmp)
        if word == "." or word == "?":
            tmp = ["@"]
            continue
    # 딕셔너리가 변경될 때마다 저장하기
    # json.dump(dic, open(content_dict_file, 'w', encoding="utf-8"))
    
    # DB가 존재한다면
    if ChatBotData.objects.filter(name="data01").exists():
        bot = ChatBotData.objects.get(name="data01")
        bot.chat_data = json.dump(dic)
        bot.save()
    else:
        ChatBotData.objects.create(name=content_dict_file, data_list=json.dump(dic))

# 저장 형식 만들기(데이터 가공)
def set_word3(dic, s3):
    w1, w2, w3 = s3
    if not w1 in dic: dic[w1] = {} # 값 초기화
    if not w2 in dic[w1]: dic[w1][w2] = {} # 값 초기화
    if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0 # 가중치 초기화
    dic[w1][w2][w3] += 1 # 가중치 + 1

# 문장 만들기
def make_sentence(head, dic):
    if not head in dic: return ""
    ret = []
    if head != "@": ret.append(head)
    top = dic[head]
    w1 = word_choice(top)
    w2 = word_choice(top[w1])
    ret.append(w1)
    ret.append(w2)
    while True:
        if w1 in dic and w2 in dic[w1]:
            w3 = word_choice(dic[w1][w2])
        else:
            w3 = ''
        ret.append(w3)
        if w3 == "." or w3 == "?" or w3 == "": break
        w1, w2 = w2, w3
    ret = "".join(ret)
    # 띄어쓰기
    # headers = {
    #     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    # }
    # datas = {
    #     'text1':ret
    # }
    # # 부산 맞춤법 검사기를 사용
    # data = requests.post("http://speller.cs.pusan.ac.kr/PnuWebSpeller/lib/check.asp", data=datas, headers=headers)
    # code = data.status_code
    # if code == 200:
    #     data.encoding = 'utf-8'
    #     soup = BeautifulSoup(data.text, "html.parser")
    #     replace_text = soup.find(attrs={'id':'tdReplaceWord_0'})
    #     if replace_text is not None:
    #         ret = replace_text.get_text()    
    # else:
    #     print('error: ', code)
    print(ret)
    # 리턴
    return ret

# 문장 선택
def word_choice(sel):
    keys = sel.keys()
    return random.choice(list(keys))

# 실제 결과 값 되돌려주기
def make_replies(text, dic):
    ok = Okt()
    # 단어 학습시키기
    if not text[-1] in [".", "?"]: text += "."
    words = ok.pos(text)
    # register_dic(words, dic)
    # 사전에 단어가 있다면 그것을 기반으로 문장 만들기
    for word in words:
        face = word[0]
        if face in dic: return make_sentence(face, dic)
    return make_sentence("@", dic)

if __name__ == "__main__":
    start_time = time.time()
    if os.path.exists(content_dict_file):
        with open(content_dict_file, 'r') as fp:
            dic = json.load(fp)
    if dic:
        print('start')
        ChatBotData.objects.create(name="data01", chat_data=dic)
        print('done')
    print("--- %s seconds ---" % (time.time() - start_time))
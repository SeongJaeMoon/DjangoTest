import requests
from bs4 import BeautifulSoup as bs
import time
from time import sleep
from time import strftime as strf
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from os.path import curdir, pardir
from os import chdir, mkdir
from multiprocessing import Pool
import re

# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py 파일 경로를 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snssaver.settings")
# 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만들기
import django
django.setup()
# 모델 가져오기
from parsed_data.models import ParsingData, UploadData, ImgData, VideoData, Comment

# python 파일의 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = 'https://www.instagram.com/'
DRIVER_DIR = '/Users/moonseongjae/chromedriver'
FILE_DIR = '/Users/moonseongjae/Proejct_intercept/factory/{}/' # 경로 문자열 포맷팅하기

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}
# 인스타그램 메인 -> id의 변화에 따른 update 결과 추가 하기! 추가, 삭제
def instagram(loop: "user id"):
    try:
        keyword = str(loop)
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        
        driver = webdriver.Chrome(DRIVER_DIR, chrome_options=options) # 브라우저 띄우기 
        driver.implicitly_wait(10)
        driver.get(URL + keyword) # URL 주소 가져오기
        sleep(5)
        result = [] # 결과 저장 리스트
        result.append(keyword) # 사용자 아이디, index 0
        total = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[1]/a/span') # 총 게시물 수
        total_len = int(str(total.text).replace(',', '')) # 게시물 수
        result.append(total_len) # 게시물 총 수, index 1
        print(keyword + ' 총 게시물:', total_len) 

        pro_img = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/div/div/span/img')
        result.append(pro_img.get_attribute('src')) # 프로필 이미지, index: 2
          
        new_links = []
        break_point = 0
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)') # 자동 스크롤 내리기
            time.sleep(4)
            links = [i.get_attribute('href') for i in driver.find_elements_by_css_selector('div.v1Nh3 > a')] # 연결 주소 리스트
            for i in links:
                if not (i in new_links):
                    new_links.append(i)
            print(keyword + ': ', len(new_links)) # 현재 찾은 주소의 수
            if (total_len - len(new_links)) < 12:
                if len(new_links) == total_len or break_point >= 5:
                    break
                else: 
                    break_point += 1

        print(keyword + '-new_links: ', len(new_links)) # 새로운 링크 주소

        data_list = []       
        for idx, link in enumerate(new_links):
            print(keyword + ': ', idx)
            driver.get(link)
            datas = {} # index3 ~
            datas['link'] = link # 게시물 페이지 주소
            sleep(1)        

            # datetime.datetime.strptime(time, '%Y-%m-%d')
            try:
                datas['time'] = ''
                datas['time'] = driver.find_element_by_css_selector('time.Nzb55').get_attribute('datetime') # 시간
            except:
                pass
            try:
                datas['place'] = ''
                place = driver.find_element_by_class_name('O4GlU')
                datas['place'] = place.text # 게시물 장소
            except:
                pass
            try:
                user_reply = [] 
                isMore = True            
                while isMore:
                    try:
                        more_btn = driver.find_element_by_class_name('Z4IfV') # 댓글 더보기 버튼 클릭
                        more_btn.click()
                        time.sleep(1)
                    except Exception as e: 
                        isMore = False
                        break
                li = driver.find_elements_by_class_name('C4VMK')
                user_reply = [[l.find_element_by_tag_name('a').text, l.find_element_by_tag_name('span').text] for l in li] # [[사용자, 글과 태그], [유저, 댓글], [유저, 댓글]]...   
                datas['content'] = user_reply[0]
                datas['reply'] = user_reply[1:]
            except:
                pass
            try:
                datas['like'] = ''
                like = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "zV_Nj")))
                datas['like'] = like.text # 게시물 좋아요
            except:
                pass
            try:
                img = driver.find_elements_by_css_selector('div.KL4Bh > img')
                imgs = [im.get_attribute('src') for im in img] # 게시물 사진
                datas['imgs'] = imgs # [주소, 주소, ...]
            except:
                pass
            try:
                video = driver.find_elements_by_css_selector('div._5wCQW > video')
                videos = [v.get_attribute('src') for v in video] # 동영상 주소 
                datas['videos'] = videos # [주소, 주소, ...]
            except:
                pass
            data_list.append(datas)
        result.append(data_list) # index 4 ~
        save_db(result)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
# DB 값 저장
def save_db(data: "user data-list"):
    # ParsingData, UploadData, ImgData, VideoData, Comment
    try:
        parsing = ParsingData.objects.create(ids = data[0], total = data[1], profile_img = data[2])
        # [[k:v, k:v, k:v,...], [k:v, k:v, k:v,...], [k:v, k:v, k:v,...]]
        for d in data[3]:
            # [k:v, k:v, k:v,...]
            content = ''
            if d['content']:
                content = str(d['content']).replace('[', '').replace(']', '')
            upload = UploadData.objects.create(user = parsing, 
                                               link = d['link'], 
                                               place = d['place'], 
                                               time = d['time'], 
                                               like = d['like'], 
                                               content = content)
            if d['imgs']:
                for img in d['imgs']: 
                    ImgData.objects.create(list_img = upload, 
                                           imgs = img)
            if d['videos']:
                for video in d['videos']:
                    VideoData.objects.create(list_video = upload, 
                                             vidoes = video)
            for idx in d['reply']:
                user, comment = idx[0], idx[1]
                Comment.objects.create(comm = upload, 
                                       com_user = user, 
                                       comment = comment)
    except Exception as e:
        print(e)
    finally:
        print('save done')
# 이미지 저장 -> 보류
def save_img(path_title, link):
    try:
        if link is not None and link != 'None':
            req = requests.get(link, headers = HEADER, verify = False)
            if req.status_code == 200:
                with open(path_title + '.jpg', 'wb') as f:
                    f.write(req.content)
    except Exception as e:
        print(e)
        pass
# 동영상 저장 -> 보류
def save_mp4(path_title, link):
    try:
        if link is not None and link != 'None':
            req = requests.get(link, headers = HEADER, verify = False)
            if req.status_code == 200:
                with open(path_title + '.mp4', 'wb') as f:
                    f.write(req.content)
    except Exception as e:
        print(e)
        pass
# 데이터가 추가되면 필요한 값 추출
def more_data():
    pass

if __name__ == "__main__":
    # 주기적으로 데이터 크롤링 필요(cron|nano)
    start_time = time.time()
    try:
        auto_id = [str(u.ids).strip() for u in ParsingData.objects.all()] # 사용자 모음
        with Pool(processes = 2) as p:
            p.map(instagram, datas)
    except Exception as e:
        print(e)
    print("--- %s seconds ---" % (time.time() - start_time))

    
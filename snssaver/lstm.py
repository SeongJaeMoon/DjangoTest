import codecs
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random, sys
import time, os
import tensorflow as tf
tf.python.control_flow_ops = tf
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py 파일 경로를 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snssaver.settings")
# 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만들기
import django
django.setup()
from multiprocessing import cpu_count
from parsed_data.models import ParsingData, UploadData, Comment 

def get_text_from_db():
    start_time = time.time()
    ret = ""
    for p in ParsingData.objects.all():
        for u in UploadData.objects.filter(user=p):
            for c in Comment.objects.filter(comm=u):
                ret += str(c.comment) + " "
    print("---문장 가져오기 완료 %s seconds ---" % (time.time() - start_time))
    return sorted(list(set(ret))), ret

def lstm():
    chars, text = get_text_from_db()
    print('사용되고 있는 문자 수', len(chars))
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    # 텍스트를 maxlen 개의 문자로 자르고 다음에 오는 문자 등록하기
    maxlen = 20
    step = 3
    senetences = []
    next_chars = []
    for i in range(0, len(chars) - maxlen, step):
        senetences.append(text[i: i + maxlen])
        next_chars.append(text[i + maxlen])
    print('학습할 구문의 수: ', len(senetences))
    print('텍스트를 ID 벡터로 변환...')
    x = np.zeros((len(senetences), maxlen, len(chars)), dtype=np.bool)
    y = np.zeros((len(senetences), len(chars)), dtype=np.bool)
    for i, senetence in enumerate(senetences):
        for t, char in enumerate(senetence):
            x[i, t, char_indices[char]] = 1
        y[i, char_indices[next_chars[i]]] = 1
    
    # 모델 구축하기
    print('모델 구축중...')
    model = Sequential()
    model.add(LSTM(128, input_shape=(maxlen, len(chars))))
    model.add(Dense(len(chars)))
    model.add(Activation('softmax'))
    optimizer = RMSprop(lr=0.01)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)
    # 학습시키고 텍스트를 생성하기 반복
    for iteration in range(2): # 텍스트 생성 범위
        print('-' * 50)
        model.fit(x, y, batch_size=128, np_epoch=1)
        # 임의의 시작 텍스트 선택하기
        start_index = random.randint(0, len(text) - maxlen - 1)
        # 다양한 다양성의 문장 생성
        for diversity in [0.2, 0.5, 1.0, 1.2]:
            print()
            generated = ''
            senetece = text[start_idex: start_index + maxlen]
            generated += senetece
            print('--- 시드 = ', diversity)
            # 시드를 기반으로 텍스트 자동 생성
            for i in range(400):
                x = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(senetece):
                    x[0, t, char_indices[char]] = 1. # 오탈자 의심...
                # 다음에 올 문자를 예측하기
                preds = model.predict(x, verbos=0)[0]
                next_index = sample(preds, diversity)
                next_char = indices_char[next_index]
                # 출력하기
                generated += next_char
                senetece = senetece[1:] + next_char
                print(next_char)
                # sys.stdout.write(next_char)
                # sys.stdout.flush()
            print()

# 후보를 배열에서 꺼내기
def sample(preds, temperature = 1.0):
    preds = np.asarray(preds).astype('float64')     
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

if __name__ == "__main__":
    start_time = time.time()
    lstm()
    print("--- %s seconds ---" % (time.time() - start_time))
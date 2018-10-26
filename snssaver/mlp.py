from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from sklearn import model_selection, metrics
import json

FACTORY = '/Users/moonseongjae/Project_sns/factory/'

max_words = 0 # 첨부 데이터 -> Test Case 추가
nb_classes = 0 # 카테고리 -> Test Case 추가

batch_size = 65
nb_epoch = 20

# MLP 모델 생성
def build_model():
    model = Sequential()
    model.add(Dense(512, input_shape(max_words,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model

# 데이터 읽어 들이기
data = json.load(open(FACTORY+/'{}-data-mini.json'))
# data = json.load(open(FACTORY+/'{}-data.json'))

x = data['x'] # 텍스트를 나타내는 데이터
y = data['y'] # 카테고리 데이터

# 학습하기
x_train, x_test, y_train, y_test = train_test_split(x, y)
y_train = np_utils.to_categorical(y_train, nb_classes)
print(len(x_train), len(y_train))

model = KerasClassifier(build_fn=build_model,
                        nb_epoch=nb_epoch,
                        batch_size=batch_size)
model.fit(x_train, y_train)

# 예측하기
y = model.predict(x_test)
ac_score = metrics.accuracy_score(y_test, y)
cl_report = metrics.classification_report(y_test, y)
print('정답률 =', ac_score)
print('리포트 =\n', cl_report)
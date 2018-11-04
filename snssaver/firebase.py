import re
import json
import pyrebase
import requests

class Firebase():

    def __init__(self):
         # Initialize Firebase
        config = {
            "apiKey": "AIzaSyBa8bOUanX_snqF_KKI2VAhhRO_VjDS8Rk",
            "authDomain": "intercepted-84b0b.firebaseapp.com",
            "databaseURL": "https://intercepted-84b0b.firebaseio.com/",
            "storageBucket": "intercepted-84b0b.appspot.com",
        }
        app = pyrebase.initialize_app(config)
        self.db = app.database()
        self.ret = {}
        
    def get_geocoding(self, ids):
        data = self.db.get()
        if data is not None:
            for d in data.each():
                t = d.val()
                if isinstance(t, dict):
                    for v in t.values():
                        if v.get('id') == ids:
                            self.ret = v
                            break
            if self.ret:
                print(self.ret['id'])
                for d in self.ret['total']:
                    result = d['results'][0]
                    print(result['formatted_address'])
                    print(result['geometry']['location']['lat'], result['geometry']['location']['lng'])
                    print(result['place_id'])
                    print(str(result['types']).replace('[', '').replace(']','')) 
    
    def save_geocoding(self, stat_list, id_list):
        for i, ids in enumerate(id_list):
            keys = self.get_places(stat_list[i])
            values = self.get_places_value(stat_list[i])
            if keys and keys is not None:
                print('start: ', ids, len(keys))
                ret = '{"id": "'+ids+'", "total": ['
                for idx, k in enumerate(keys):
                    try:
                        request = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address="+k+"&key=AIzaSyDa1-OAbKJx0mf-kq2DN3tQArOfj2o36GE")
                        code = request.status_code
                        if code == 200:
                            if idx == len(keys) - 1:
                                ret += str(request.text) + '], "values": ' + str(values) +'}'
                            else:
                                ret += str(request.text)+','
                        else:
                            print('error code: ', ids, idx, k, code)
                    except Exception as e:
                        pass
                dic = json.loads(ret)
                self.db.child(str(i)).push(dic)
            print(ids, ' done')
        print('firebase geocoding-all done')
    
    # 사용자가 자주 태그한 장소 Top10 장소 반환
    def get_places(self, data):
        keys = [str(d).replace("('", '').replace("',", '').strip() for d in re.findall("\('[\w+\!,\.・`\-_=\/?<>~@#$%^&;:\[\]\+\*\(\)\" ]+',", data, re.UNICODE)]    
        return keys

    # 사용자가 자주 태그한 장소 Top10 값 반환
    def get_places_value(self, data):
        values = [int(str(d).replace('),','')) for d in re.findall('\d*\)+?,', data)]
        values.append(1) # 마지막 값 정규표현식 불가
        return values

    def remove(self, ids):
        self.data = self.db.child(ids).remove()
        print('remove done')

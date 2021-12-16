import RPi.GPIO as GPIO
from time import sleep
from DHT11_Python import dht11 # 温湿度センサーモジュール
import requests
import json
import time
import slackweb

TEMP_SENSOR_PIN = 4 # 温湿度センサーのピンの番号
INTERVAL = 5 # 監視間隔（秒）
RETRY_TIME = 2 # dht11から値が取得できなかった時のリトライまので秒数
MAX_RETRY = 20 # dht11から温湿度が取得できなかった時の最大リトライ回数

city_name = "Osaka" # 主要な都市名はいけるっぽい。
API_KEY = "5a661e21de6d2577f161eb580bc77d4f" # xxxに自分のAPI Keyを入力。
api = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}"

slackurl = "https://hooks.slack.com/services/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" 
slack = slackweb.Slack(url = slackurl)
# headers = {"Authorization" : "Bearer "+ token} 


class EnvSensorClass: # 温湿度センサークラス
    def GetTemp(self): # 温湿度を取得
        instance = dht11.DHT11(pin=TEMP_SENSOR_PIN)
        retry_count = 0
        while True: # MAX_RETRY回まで繰り返す
            retry_count += 1
            result = instance.read()
            if result.is_valid(): # 取得できたら温度と湿度を返す
                return result.temperature, result.humidity
            elif retry_count >= MAX_RETRY:
                return 99.9, 99.9 # MAX_RETRYを過ぎても取得できなかった時に温湿度99.9を返す
            sleep(RETRY_TIME)

GPIO.setwarnings(False) # GPIO.cleanup()をしなかった時のメッセージを非表示にする
GPIO.setmode(GPIO.BCM) # ピンをGPIOの番号で指定

#main
try:
    if __name__ == "__main__":
        env = EnvSensorClass()
        while True:
            
            url = api.format(city = city_name, key = API_KEY)
            response = requests.get(url)
            data = response.json()
            
            temp, hum = env.GetTemp() # 温湿度を取得
            print("温度 = ", temp, " 湿度 = ", hum, "％")
            print("温度 = " , data["main"]["temp"] ," 湿度 = ",data["main"]["humidity"])
            
            if str(data["weather"][0]["main"]) == "Clouds":
                weather = "曇り"
            
            if str(data["weather"][0]["main"]) == "Clear":
                weather = "晴れ"
                
            if str(data["weather"][0]["main"]) == "Rain":
                weather = "雨"
            
            print(weather)
            
            message = "天候:" + weather + '\n外の温度:' +  str(data["main"]["temp"]) + "℃\n" + "外の湿度:"+ str(data["main"]["humidity"]) + "%" + "\n外の体感温度:" + str(data["main"]["feels_like"]) + "℃" + "\n室内の温度:" + str(temp) + "℃\n" + "室内の湿度:" + str(hum) + "%"
            
            slack.notify(text=message)
            
            sleep(INTERVAL)
except KeyboardInterrupt:
    pass
GPIO.cleanup()
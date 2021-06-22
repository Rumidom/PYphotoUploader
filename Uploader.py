import pyrebase
import cv2
import datetime
import time
from gpiozero import LED
from gpiozero import Button
import board
import busio
import adafruit_vl53l0x
import urllib.request as urllib2
#!/usr/bin/env python
import signal
import sys


    
config = {
'apiKey': "AIzaSyAKOB4wJmHgMWEC6DxYbjkWMCaAHKgKTkw",
'authDomain': "imageset-ds-upe.firebaseapp.com",
"databaseURL": "https://imageset-ds-upe.firebaseio.com",
'projectId': "imageset-ds-upe",
'storageBucket': "imageset-ds-upe.appspot.com",
'messagingSenderId': "965093506402",
'appId': "1:965093506402:web:bc3f21b8b980e26f66c03b",
'measurementId': "G-J6H57Y366K"
}

def internet_on():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False
#Teste

Intervalo = 600
DistMin = 700
picdelay = 0
frame = None
path_local = "Imagem.png"
modo = 'LIDARPress'
#modo = ''
Cap0Res = (1280,720)#(1920,1080)
Cap1Res = (1920,1080)
# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

print('Inicializando')
STRDateTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
STRDate = datetime.datetime.now().strftime("%m_%d_%Y")
STRTime = datetime.datetime.now().strftime("%H.%M.%S")

print(STRDateTime)

Sensor = Button(14)
led = LED(16)
    
print('...........')

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
Cap = cv2.VideoCapture(0)
Cap.set(cv2.CAP_PROP_FRAME_WIDTH, Cap0Res[0])
Cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Cap0Res[1])

def TakePic(CamN,CamRes):
    Online = True
    ret = False
    #time.sleep(picdelay)
    led.on()
    #Online = internet_on()
    try:
        STRDate = datetime.datetime.now().strftime("%m_%d_%Y")
        STRTime = datetime.datetime.now().strftime("%H.%M.%S")
  
        for N in range(20):
            ret, frame = Cap.read()

        cv2.imwrite(path_local, frame)
    except:
        print("Captura da imagem falhou")
       
    if (ret):
        print(' Imagem - ',STRTime,"Cam"+str(CamN)+": ",Cap.isOpened())
        try:
            storage.child(STRDate+'/Cam'+str(CamN)+"/"+STRTime+".png").put(path_local)
        except:
            Online = False
            print("Conexão com o servidor falhou")
        
    # Close device
    if (Online):
        led.off()
    else:
        led.off()
        time.sleep(1)
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)
        led.on()
        time.sleep(1)
        led.off()

def signal_handler(sig, frame):
    Cap.release()
    print('Encerrando.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

LastState = False
while (True):
    Dist = 0
    for i in range(5):
        if (vl53.range > Dist):
            Dist = vl53.range
    if (modo=="Tempo"):
        TakePic(0,Cap0Res)
        #TakePic(1,Cap1Res)
        time.sleep(Intervalo)
    elif (modo=="SensorPress"):
        if ((not Sensor.is_pressed) and (not LastState)):
            TakePic(0,Cap0Res)
            #TakePic(1,Cap1Res)
            LastState = True
        if ((Sensor.is_pressed) and (LastState)):
            LastState = False
    elif (modo=="SensorRelease"):
        if ((not Sensor.is_pressed) and (not LastState)):
            LastState = True
        if ((Sensor.is_pressed) and (LastState)):
            LastState = False
            TakePic(0,Cap0Res)
            #TakePic(1,Cap1Res)
    elif (modo=="LIDARPress"):
        if ((Dist < DistMin) and (not LastState)):
            TakePic(0,Cap0Res)
            #TakePic(1,Cap1Res)
            LastState = True
        if ((Dist > DistMin) and (LastState)):
            LastState = False
    elif (modo=="LIDARRelease"):
        if ((Dist < DistMin) and (not LastState)):
            LastState = True
        if ((Dist > DistMin) and (LastState)):
            LastState = False
            TakePic(0,Cap0Res)
            #TakePic(1,Cap1Res)


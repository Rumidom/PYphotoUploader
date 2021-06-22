import pyrebase
import cv2
import datetime
import time
from gpiozero import LED
from gpiozero import Button
import RPi.GPIO as GPIO
import board
import busio
import adafruit_vl53l0x
import os
from imutils.video import VideoStream
import signal

Intervalo = 600
DistMin = 1000
Cam = 0
modo = 'LIDARPress'
Cap0Res = (1280,720)#(1920,1080)

if os.path.isfile("Conf.txt"):
    with open("Conf.txt") as f:
        lines = f.readlines()
        f.close()
        Cam = int(lines[0].replace("\n",""))
        modo = lines[1].replace("\n","")
        DistMin = int(lines[2].replace("\n",""))

if (modo == 'LIDARPress'):
    # Initialize I2C bus and sensor.
    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)

if (modo == 'Ultrasonico'):
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    #set GPIO Pins
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24

    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def Ultrasonicodistance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

print('Inicializando')
print('Modo: ',modo)
print('Cam: ',Cam)
STRDateTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
STRDate = datetime.datetime.now().strftime("%m_%d_%Y")
STRTime = datetime.datetime.now().strftime("%H.%M.%S")

print(STRDateTime)

led = LED(16)
    
print('...........')

Cap = cv2.VideoCapture(0)
Cap.set(cv2.CAP_PROP_FRAME_WIDTH, Cap0Res[0])
Cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Cap0Res[1])

def TakePic(CamN,CamRes):
    led.on()
    #Cap = VideoStream(src=CamN,resolution=CamRes,framerate=15).start()
    #time.sleep(2.0)
    #Cap = cv2.VideoCapture(CamN)
    #Cap.set(cv2.CAP_PROP_FRAME_WIDTH, CamRes[0])
    #Cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CamRes[1])
    #Cap.set(cv2.CAP_PROP_FPS, 15.0)
    
    STRDate = datetime.datetime.now().strftime("%m_%d_%Y")
    STRTime = datetime.datetime.now().strftime("%H.%M.%S")
    print(' Imagem - ',STRTime,"Cam"+str(CamN))
    
    for N in range(20):
        ret, frame = Cap.read()
        
    #Cap.release()
    #Cap.stop()
    path = '/USBDRIVE/'+STRDate+'/Cam'+str(CamN)+'/'
    if (os.path.ismount('/USBDRIVE/')):
      if (not os.path.exists('/USBDRIVE/'+STRDate)):
        os.mkdir('/USBDRIVE/'+STRDate)
      if (not os.path.exists('/USBDRIVE/'+STRDate+'/Cam'+str(CamN))):
        os.mkdir('/USBDRIVE/'+STRDate+'/Cam'+str(CamN))
      #print("Frame Size: ",frame.shape)
      cv2.imwrite(os.path.join(path, STRTime+".png"), frame)
      #print(os.listdir(path))
      led.off()
    else:
      print('PenDrive não foi encontrado')
    # Close device
    
def signal_handler(sig, frame):
    Cap.release()
    print('Encerrando.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)    
  
LastState = False
StartTime = time.time()

while (True):
    Dist = 0
    t = time.localtime()
    current_time = time.strftime("%H:%M", t)

    if ((current_time == "11:00") or (current_time == "20:00")):
        os.system('sudo reboot')
                     
    if (modo=="Tempo"):
        TakePic(Cam,Cap0Res)
        #TakePic(1,Cap1Res)
        StartTime = time.time()
        time.sleep(Intervalo)
    elif (modo=="LIDARPress"):
        for i in range(5):
            if (vl53.range > Dist):
                Dist = vl53.range
        if ((Dist < DistMin) and (not LastState)):
            TakePic(Cam,Cap0Res)
            #TakePic(1,Cap1Res)
            LastState = True
            StartTime = time.time()
        if ((Dist > DistMin) and (LastState)):
            LastState = False
    elif (modo=="Ultrasonico"):
        for i in range(5):
            d = Ultrasonicodistance()
            if (d > Dist):
                Dist = d
                time.sleep(1)
        if ((Dist < DistMin) and (not LastState)):
            TakePic(Cam,Cap0Res)
            #TakePic(1,Cap1Res)
            LastState = True
            StartTime = time.time()
        if ((Dist > DistMin) and (LastState)):
            LastState = False
    

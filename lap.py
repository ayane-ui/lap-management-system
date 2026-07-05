import RPi.GPIO as GPIO
import LCD1602
import time
import subprocess
import cv2
import numpy as np
PIR_PIN = 17
BUZZER_PIN = 18
SERVO_PIN = 13# ← 追加：旗用サーボ
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)  # ← 追加
# サーボPWM設定（50Hz）
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)
def raise_flag():
    servo.ChangeDutyCycle(7.5)  # 90度（旗が上がる）
    time.sleep(1)
    servo.ChangeDutyCycle(0)    # サーボの震え防止
LCD1602.init(0x3f, 1)
lap = 0
prev = 0
total_laps = 5
def detect_blue(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 120, 70])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_pixels = cv2.countNonZero(mask)
    print("blue_pixels =", blue_pixels)
    return blue_pixels > 5000
while True:
    now = GPIO.input(PIR_PIN)
    if now == 1 and prev == 0:
        # USBカメラで撮影 
        filename = f"lap_{lap+1}.jpg"
        subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", filename])
        #  青色検出 
        if detect_blue(filename):
            lap += 1
            remain = total_laps - lap
            # 最終周回開始（残り1周） 
            if remain == 1:
                GPIO.output(BUZZER_PIN, 1)
                time.sleep(0.3)
                GPIO.output(BUZZER_PIN, 0)
            # LCD 表示
            LCD1602.write(0, 0, f"Lap:{lap}")
            LCD1602.write(1, 1, f"Remain:{remain}")
            print("Blue detected → Lap:", lap)
            #  ゴール 
            if lap == total_laps:
                raise_flag()  # ← 追加：ゴールしたら旗を上げる
                GPIO.output(BUZZER_PIN, 1)
                time.sleep(1)
                GPIO.output(BUZZER_PIN, 0)
                LCD1602.write(0, 0, "Finish!       ")
                LCD1602.write(1, 1, "Good job!     ")
                break
        else:
            print("Blue NOT detected → カウントしない")
        time.sleep(1.0)
    prev = now
    time.sleep(0.1)

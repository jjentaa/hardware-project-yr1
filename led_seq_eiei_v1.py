from machine import Pin, I2C, PWM, ADC
import ssd1306
import random
import time

from esp32_s3 import ESP32_S3
from joystick_jane import Joystick
from fourbutton import FourButton

s_time = time.ticks_ms()
check_ans_time = time.ticks_ms()

joy = Joystick()

esp = ESP32_S3()

fbutton = FourButton()

sw_state = [False, False, False, False]


esp.oled.fill(0)
esp.oled.text("LED SEQUENCING EIEI", 0, 0, 1)
esp.oled.show()

pattern = {
    1:["R", "Y", "G", "P"],
    2:["Y", "G", "P", "R"],
    3:["R", "G", "Y", "P"],
    4:["Y", "R", "G", "P"],
    5:["G", "R", "P", "Y"],
    6:["G", "Y", "R", "P"]
}

ans = {
    1:[2,2,1,1],
    2:[2,1,2,1],
    3:[1,2,2,1],
    4:[2,1,1,2],
    5:[1,2,1,2],
    6:[1,1,1,3]
}

state = 'light-1'
pat = random.randint(1, 6)
print(ans[pat])

counter = [0, 0, 0, 0]

while True:
    if(time.ticks_ms()-s_time>10):
        esp.oled.fill(0)
        esp.oled.text("LED SEQUENCING EIEI", 0, 0, 1)
        esp.oled.text("red button "+str(counter[0]-1)+"time(s)", 0, 10, 1)
        esp.oled.text("yellow button "+str(counter[1]-1)+"time(s)", 0, 20, 1)
        esp.oled.text("green button "+str(counter[2]-1)+"time(s)", 0, 30, 1)
        esp.oled.text("yellow button "+str(counter[3]-1)+"time(s)", 0, 40, 1)
        esp.oled.show()
    if(state == 'light-1'):
        now = time.ticks_ms()
        if(now-s_time >= 2000):
            state = 'light-2'
            s_time = now
            esp.clearled()
        else:
            if(pattern[pat][0]=='R'):
                esp.red()
            if(pattern[pat][0]=='Y'):
                esp.yellow()
            if(pattern[pat][0]=='G'):
                esp.green()
            if(pattern[pat][0]=='P'):
                esp.pink()

    elif(state == 'light-2'):
        now = time.ticks_ms()
        if(now-s_time >= 2000):
            state = 'light-3'
            s_time = now
            esp.clearled()
        else:
            if(pattern[pat][1]=='R'):
                esp.red()
            if(pattern[pat][1]=='Y'):
                esp.yellow()
            if(pattern[pat][1]=='G'):
                esp.green()
            if(pattern[pat][1]=='P'):
                esp.pink()
    
    elif(state == 'light-3'):
        now = time.ticks_ms()
        if(now-s_time >= 2000):
            state = 'light-4'
            s_time = now
            esp.clearled()
        else:
            if(pattern[pat][2]=='R'):
                esp.red()
            if(pattern[pat][2]=='Y'):
                esp.yellow()
            if(pattern[pat][2]=='G'):
                esp.green()
            if(pattern[pat][2]=='P'):
                esp.pink()
    
    elif(state == 'light-4'):
        now = time.ticks_ms()
        if(now-s_time >= 2000):
            state = 'check-ans'
            s_time = now
            esp.clearled()
        else:
            if(pattern[pat][3]=='R'):
                esp.red()
            if(pattern[pat][3]=='Y'):
                esp.yellow()
            if(pattern[pat][3]=='G'):
                esp.green()
            if(pattern[pat][3]=='P'):
                esp.pink()
    
    elif(state == 'check-ans'):
        now = time.ticks_ms()
        if(now-s_time >= 2000):
            state = 'light-1'
            s_time = now
            esp.clearled()
        else:
            val = fbutton.get_value()
            print(val)
            for i in range(4):
                if(val[i]==True and sw_state[i]==False):
                    counter[i]+=1
                    sw_state[i]=True
                elif(val[i]==True and sw_state[i]==True):
                    sw_state[i]=True
                elif(val[i]==False and sw_state[i]==True):
                    sw_state[i]=False
                    
            esp.oled.fill(0)
            esp.oled.text("LED SEQUENCING EIEI", 0, 0, 1)
            esp.oled.text("red button "+str(counter[0]-1)+"time(s)", 0, 10, 1)
            esp.oled.text("yellow button "+str(counter[1]-1)+"time(s)", 0, 20, 1)
            esp.oled.text("green button "+str(counter[2]-1)+"time(s)", 0, 30, 1)
            esp.oled.text("yellow button "+str(counter[3]-1)+"time(s)", 0, 40, 1)
            esp.oled.show()

    if(esp.sw.value()):
        if(counter == ans[pat]):
            esp.oled.fill(0)
            esp.oled.text("You pass!!!!!", 0, 0, 1)
            esp.oled.show()
            break


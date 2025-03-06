from machine import Pin, I2C, PWM, ADC
import ssd1306
import random
import time

from esp32_s3 import ESP32_S3
from joystick_jane import Joystick

s_time = time.time()

joy = Joystick()

esp = ESP32_S3()


esp.oled.text("LED SEQUENCING", 0, 0, 1)
esp.oled.show()

pattern1 = {
    1:["R", "Y"],
    2:["Y", "G"],
    3:["R", "G"],
    4:["Y", "R"],
    5:["G", "R"],
    6:["G", "Y"]
}
pattern2 = {
    1:["R", "Y", "G"],
    2:["Y", "G", "R"],
    3:["R", "G", "Y"],
    4:["Y", "R", "G"],
    5:["G", "R", "Y"],
    6:["G", "Y", "R"]
}

ans = {
    1:"Right",
    2:"Left",
    3:"Up",
    4:"Up",
    5:"Down",
    6:"Down"
}

state = 'light-1'
level=1
mistake = 0
correct = 0

for i in range(4):
    if(level<=2):
        pat1 = random.randint(1, 6)
        print(pattern1[pat1])
        print(ans[pat1])
        passed = False
        x = []
        y = []
        counter=0
        state = 'light-1'
        s_time = time.ticks_ms()
        while (not passed):
            
            if(state == 'light-1'):
                now = time.ticks_ms()
                if(now-s_time >= 2000):
                     esp.clearled()
                     state = 'light-2'
                     s_time = now
                else:
                    if(pattern1[pat1][0]=="R"):
                        esp.red()
                    elif(pattern1[pat1][0]=="Y"):
                        esp.yellow()
                    elif(pattern1[pat1][0]=="G"):
                        esp.green()
                    
            
            if(state == 'light-2'):
                now = time.ticks_ms()
                if(now-s_time >= 2000):
                    state = 'check-ans'
                    esp.clearled()
                    s_time = now
                else:
                    if(pattern1[pat1][1]=="R"):
                        esp.red()
                    elif(pattern1[pat1][1]=="Y"):
                        esp.yellow()
                    elif(pattern1[pat1][1]=="G"):
                        esp.green()

            if(state == 'check-ans'):
                now = time.ticks_ms()
                if(now-s_time):
                    val = joy.get_value()
                    d = joy.check_direction(val[0], val[1])
                    #print(d)
                    
                    if(d[0] == ans[pat1] or d[1] == ans[pat1]):
                        passed = True
                        correct+=1
                        esp.oled.fill(0)
                        print("Pass level", level)
                        esp.oled.text("LED SEQUENCING", 0, 0, 1)
                        esp.oled.text("Pass Level "+str(level), 0, 10, 1)
                        esp.oled.show()
                        level+=1
                        break
                    if not (d[0] == 'CenterX' and d[1] == 'CenterY'):
                        mistake+=1
                        state = 'light-1'
         
    else:
        pat2 = random.randint(1, 6)
        print(pattern2[pat2])
        print(ans[pat2])
        passed = False
        x = []
        y = []
        counter=0
        state = 'light-1'
        s_time = time.ticks_ms()
        while (not passed):
            
            if(state == 'light-1'):
                now = time.ticks_ms()
                if(now-s_time >= 2000):
                     esp.clearled()
                     state = 'light-2'
                     s_time = now
                else:
                    if(pattern2[pat2][0]=="R"):
                        esp.red()
                    elif(pattern2[pat2][0]=="Y"):
                        esp.yellow()
                    elif(pattern2[pat2][0]=="G"):
                        esp.green()
                        
            if(state == 'light-2'):
                now = time.ticks_ms()
                if(now-s_time >= 2000):
                    state = 'light-3'
                    esp.clearled()
                    s_time = now
                else:
                    if(pattern2[pat2][1]=="R"):
                        esp.red()
                    elif(pattern2[pat2][1]=="Y"):
                        esp.yellow()
                    elif(pattern2[pat2][1]=="G"):
                        esp.green()
                        
            if(state == 'light-3'):
                now = time.ticks_ms()
                if(now-s_time >= 2000):
                    state = 'check-ans'
                    esp.clearled()
                    s_time = now
                else:
                    if(pattern2[pat2][2]=="R"):
                        esp.red()
                    elif(pattern2[pat2][2]=="Y"):
                        esp.yellow()
                    elif(pattern2[pat2][2]=="G"):
                        esp.green()
                        
            if(state == 'check-ans'):
                now = time.ticks_ms()
                if(now-s_time):
                    val = joy.get_value()
                    d = joy.check_direction(val[0], val[1])
                    #print(d)
                    
                    if(d[0] == ans[pat2] or d[1] == ans[pat2]):
                        passed = True
                        correct+=1
                        esp.oled.fill(0)
                        print("Pass level", level)
                        esp.oled.text("LED SEQUENCING", 0, 0, 1)
                        esp.oled.text("Pass Level "+str(level), 0, 10, 1)
                        esp.oled.show()
                        level+=1
                        break
                    if not (d[0] == 'CenterX' and d[1] == 'CenterY'):
                        mistake+=1
                        state = 'light-1'
         
print(correct)

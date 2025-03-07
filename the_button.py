from machine import Pin, I2C, PWM, ADC
import random, ssd1306, time, esp32_s3
from complexbutton import ComplexButton

def check_button(last_state):
    if esp.sw.value() == 0 and esp.sw.value() != last_state:
        return True
    return False

def display_center(text, y):
    esp.oled.text(text,60-len(text)*3,y,1)

def display_time(sec):
    minute = sec//60
    sec %= 60
    sec = round(sec, 3)
    tm.tm.clear()
    tm.tm.show(f'{minute:02}{sec:02}', 7)

# using default address 0x3C
esp = esp32_s3.ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
tm = ComplexButton(10, 12, 11)


TIME = 100 # ---------------- GENERAL BOMB TIME
TIME_PRECISION = 0.1
STRIKE = 0


last_state = esp.sw.value()
check_time = time.ticks_ms()
last_time = time.ticks_ms()

while True:
    display_time(TIME)
    no_mistake = True
    sudden = False
    hold = False
    
    r = 31
    texts = ["Abort", "Defuse", "Hold", "Press", "Touch"]
    text = random.choice(texts)
    rand = random.randint(0, 2) # ------------------ change to (0, 3) if able
    esp.clearled()
    
    if rand == 0:
        esp.red(255)
        
    if rand == 1:
        esp.yellow(255)
            
    if rand == 2:
        esp.green(255)
    
    print(text)
    esp.oled.fill(0)
    esp.oled.ellipse(64,32,r,r,1,0) # --------------------- DISPLAY BUTTON WITH WORD IN OLED
    display_center(text, 30)
    esp.oled.show()
    
    if text == 'Abort':
        if rand in (0, 2): # ----------- If Red, Green
            hold = True
                     
        else:
            sudden = True
        
    
    elif text == 'Defuse':
        if rand == 1: # ----------- If Yellow
            hold = True
  
        else:
            sudden = True
    
    elif text == 'Hold':
        if rand == 2: # ------- If Green
            hold = True
        else:
            sudden = True
    
    elif text == 'Press':
        if rand in (0, 1): # ------ If Red, Yellow
            hold = True
        else:
            sudden = True
    
    elif text == 'Touch':
        if rand == 1:	# ------- If Yellow
            hold = True
        else:
            sudden = True
        
    
    if sudden:
        print("Sudden")
        while esp.sw.value() == 1:
            last_time = time.ticks_ms()
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
        while esp.sw.value() == 0:
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
        if time.ticks_ms() - last_time >= 500:
            no_mistake = False
    
    if hold:
        print("Hold")
        wait_time = random.randint(3, 3)*1000
        while esp.sw.value() == 1:
            last_time = time.ticks_ms()
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
        while time.ticks_ms() - last_time <= wait_time: # -- Wrong If released between wait time
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
            if esp.sw.value() == 1:
                no_mistake = False
                break
        else:
            no_mistake = True
            esp.oled.fill(0)
            display_center("Release", 15)
            display_center("the button", 30)
            esp.oled.show()
            last_time = time.ticks_ms()
            while time.ticks_ms() - last_time <= 1500: # -- Wrong If not released in 1500 ms
                if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                    TIME -= TIME_PRECISION
                    check_time = time.ticks_ms()
                    display_time(TIME)
                if esp.sw.value() == 1:
                    break
            else:
                no_mistake = False
    
    if no_mistake:
        break
    else:
        esp.oled.fill(0)
        display_center("Failed", 15)
        display_center("Try again.", 30)
        esp.oled.show()
        time.sleep(2)
        TIME -= 2
        STRIKE += 1
        display_time(TIME)

esp.oled.fill(0)
display_center("Passed", 30)
esp.oled.show()


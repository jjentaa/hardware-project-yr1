from machine import Pin, I2C, PWM, ADC
import random, ssd1306, time

from esp32_s3 import ESP32_S3
from joystick import Joystick

# Initialize components
esp = ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000, board_id=2)
joy = Joystick(x_invert=True)

if esp.board_id == 1:
    from complexbutton import ComplexButton
    
    complexbutton = ComplexButton(10, 12, 11)
    tm = complexbutton.tm
    
elif esp.board_id == 2:
    from tm1637 import TM1637
    from fourbutton import FourButton, FourLeds
    
    four_buttons = FourButton(5, 6, 18, 8)
    four_leds = FourLeds(r=9, y=10, g=45, b=21)
    tm = TM1637(12, 11)
    
TIME = 100 # ---------------- GENERAL BOMB TIME
TIME_PRECISION = 0.1
STRIKE = 0
STRIKE_LIMIT = 3

def check_button(last_state):
    if esp.sw.value() == 0 and esp.sw.value() != last_state:
        return True
    return False

def display_center(text, y=30):
    esp.oled.text(text,60-len(text)*3,y,1)

def update_timer():
    global TIME, check_time
    if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
        TIME -= TIME_PRECISION
        check_time = time.ticks_ms()
        display_time(TIME)

def display_time(sec):
    minute = int(sec // 60)
    sec %= 60
    tm.clear()
    if esp.board_id == 1:
        tm.show(f'{minute:02.0f}{sec:02.1f}', 7)
    elif esp.board_id == 2:
        tm.show(f'{minute:02.0f}{sec:02.0f}', 1)

last_state = esp.sw.value()
check_time = time.ticks_ms()
last_time = time.ticks_ms()

while TIME > 0:
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
            if TIME <= 0:
                break
            update_timer()
        while esp.sw.value() == 0:
            if TIME <= 0:
                break
            update_timer()
        if time.ticks_ms() - last_time >= 500:
            no_mistake = False
    
    if hold:
        print("Hold")
        wait_time = random.randint(3, 3)*1000
        while esp.sw.value() == 1:
            last_time = time.ticks_ms()
            if TIME <= 0:
                break
            update_timer()
        while time.ticks_ms() - last_time <= wait_time: # -- Wrong If released between wait time
            if TIME <= 0:
                break
            update_timer()
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
                if TIME <= 0:
                    break
                update_timer()
                if esp.sw.value() == 1:
                    break
            else:
                no_mistake = False
    
    if no_mistake:
        break
    else:
        STRIKE += 1
        if STRIKE >= STRIKE_LIMIT:
            TIME = 0
        esp.oled.fill(0)
        display_center("Failed", 15)
        display_center("Try again.", 30)
        esp.oled.show()
        STRIKE += 1
        while time.ticks_ms() - last_time <= 2000: # Show wrong for 2 seconds
            if TIME <= 0:
                break
            update_timer()

if TIME > 0:
    esp.oled.fill(0)
    display_center("Passed", 30)
    esp.oled.show()
else:
    esp.oled.fill(0)
    display_center("Game over.", 30)
    esp.oled.show()


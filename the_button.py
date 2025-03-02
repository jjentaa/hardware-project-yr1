from machine import Pin, I2C, PWM, ADC
import random, ssd1306, time, esp32_s3

def current_ms():
    return time.time_ns() // 1000000

def check_button(last_state):
    if esp.sw.value() == 0 and esp.sw.value() != last_state:
        return True
    return False

# using default address 0x3C
esp = esp32_s3.ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)


TIME = 60 # ---------------- GENERAL BOMB TIME
TIME_PRECISION = 0.1
STRIKE = 0


last_state = esp.sw.value()
check_time = current_ms()
last_time = current_ms()

while True:
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
    # esp.oled.ellipse(64,32,r,r,1,0) # --------------------- DISPLAY BUTTON WITH WORD IN OLED
    # esp.oled.text(text,60-len(text)*3,30,1)
    # esp.oled.show()
    
    if text == 'Abort':
        if rand in [0, 2]: # ----------- If 0, 2
            hold = True
                     
        else:
            sudden = True
        
    
    elif text == 'Defuse':
        if rand == 1: # ----------- If 1
            hold = True
  
        else:
            sudden = True
    
    elif text == 'Hold':
        sudden = True
    
    elif text == 'Press':
        hold = True         
    
    elif text == 'Touch':
        if rand == 1:
            hold = True
        else:
            sudden = True
        
    
    if sudden:
        while esp.sw.value() == 1:
            check_time = current_ms()
            last_time = current_ms()
        while esp.sw.value() == 0:
            if current_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = current_ms()
        if current_ms() - last_time >= 500:
            no_mistake = False
    
    if hold:
        wait_time = random.randint(3, 3)*1000
        while esp.sw.value() == 1:
            check_time = current_ms()
            last_time = current_ms()
        while current_ms() - last_time <= wait_time: # -- Wrong If released between wait time
            if current_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = current_ms()
#                 print(TIME, esp.sw.value())
            if esp.sw.value() == 1:
                no_mistake = False
                break
        else:
            no_mistake = True
            print("Release the button")
            last_time = current_ms()
            while current_ms() - last_time <= 1500: # -- Wrong If not released in 1500 ms
                if current_ms() - check_time >= TIME_PRECISION * 1000:
                    TIME -= TIME_PRECISION
                    check_time = current_ms()
#                     print(TIME, esp.sw.value())
                if esp.sw.value() == 1:
                    break
            else:
                no_mistake = False
    
    if no_mistake:
        break
    else:
        print("Not Passed, Try Again")
        STRIKE += 1

print("Passed")


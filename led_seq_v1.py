from machine import Pin, I2C, PWM, ADC
import ssd1306
import random
import time

from esp32_s3 import ESP32_S3
from joystick import Joystick
from complexbutton import ComplexButton

# Initialize components
joy = Joystick(x_invert=True)
esp = ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
tm = ComplexButton(10, 12, 11)  # TM1637 display for timer

# Game parameters
TIME = 1  # General game time in seconds
TIME_PRECISION = 0.1  # Update timer every 0.1 seconds
STRIKE = 0  # Track wrong answers
STRIKE_LIMIT = 3  # Game over after 3 strikes
check_time = time.ticks_ms()  # For timer tracking

# LED patterns and answers
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

def display_time(sec):
    minute = sec // 60
    sec %= 60
    sec = round(sec, 3)
    tm.tm.clear()
    tm.tm.show(f'{minute:02}{sec:02}', 7)

def draw_progress_bar(level):
    # Draw a progress bar showing level progress (1-4)
    esp.oled.rect(20, 28, 90, 8, 1)
    progress = int((level-1) * 22.5)  # Each level fills 1/4 of the bar
    if progress > 0:
        esp.oled.fill_rect(20, 28, progress, 8, 1)

def show_strike_info(level):
    esp.oled.fill(0)
    esp.oled.rect(0, 0, 128, 16, 1)
    esp.oled.text("LED SEQUENCE", 12, 4, 1)
    draw_progress_bar(level)
    esp.oled.text("LVL:" + str(level) + "/4", 5, 40, 1)
    esp.oled.text("Strikes: " + str(STRIKE) + "/" + str(STRIKE_LIMIT), 0, 52, 1)
    esp.oled.show()

# Initialize game state
state = 'light-1'
level = 1
total_levels = 4
correct = 0
display_time(TIME)  # Initialize timer display

# Main game loop
show_strike_info(level)

game_active = True
while game_active and TIME > 0 and STRIKE < STRIKE_LIMIT and level <= total_levels:
    # Update timer
    if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
        TIME -= TIME_PRECISION
        check_time = time.ticks_ms()
        display_time(TIME)
    
    # Select pattern based on level
    if level <= 2:
        pattern_set = pattern1
        pattern_num = random.randint(1, 6)
        current_pattern = pattern_set[pattern_num]
        print(current_pattern)
        print(ans[pattern_num])
        
        # Game sequence
        passed = False
        state = 'light-1'
        s_time = time.ticks_ms()
        while not passed and TIME > 0 and STRIKE < STRIKE_LIMIT:
            # Update timer continuously during game
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
                
            if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
                break
                
            # Handle light sequence
            if state == 'light-1':
                now = time.ticks_ms()
                if now - s_time >= 2000:
                    esp.clearled()
                    state = 'light-2'
                    s_time = now
                else:
                    if current_pattern[0] == "R":
                        esp.red()
                    elif current_pattern[0] == "Y":
                        esp.yellow()
                    elif current_pattern[0] == "G":
                        esp.green()
            
            elif state == 'light-2':
                now = time.ticks_ms()
                if now - s_time >= 2000:
                    state = 'check-ans'
                    esp.clearled()
                    s_time = now
                else:
                    if current_pattern[1] == "R":
                        esp.red()
                    elif current_pattern[1] == "Y":
                        esp.yellow()
                    elif current_pattern[1] == "G":
                        esp.green()

            elif state == 'check-ans':
                now = time.ticks_ms()
                if now - s_time:
                    d = joy.direction()
                    
                    if ans[pattern_num] in d:
                        passed = True
                        correct += 1
                        print("Pass level", level)
                        level += 1
                        show_strike_info(level)
                        break
                    if not (d[0] == 'Center' and d[1] == 'Center'):
                        # Incorrect answer
                        STRIKE += 1
                        # Show error message
                        esp.oled.fill(0)
                        esp.oled.text("INCORRECT!", 25, 20, 1)
                        esp.oled.text(f"Strikes: {STRIKE}/3", 20, 40, 1)
                        esp.oled.show()
                        
                        # Wait briefly so player can see the message
                        error_start = time.ticks_ms()
                        while time.ticks_ms() - error_start < 1000:  # Show for 1 second
                            # Keep updating the timer during this time
                            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                                TIME -= TIME_PRECISION
                                check_time = time.ticks_ms()
                                display_time(TIME)
                        
                        if STRIKE >= STRIKE_LIMIT:
                            break
                        else:
                            show_strike_info(level)
                            time.sleep(1)
                            TIME -= 1
                            state = 'light-1'
                            s_time = time.ticks_ms()
    else:
        pattern_set = pattern2
        pattern_num = random.randint(1, 6)
        current_pattern = pattern_set[pattern_num]
        print(current_pattern)
        print(ans[pattern_num])
        
        # Game sequence
        passed = False
        state = 'light-1'
        s_time = time.ticks_ms()
        while not passed and TIME > 0 and STRIKE < STRIKE_LIMIT:
            # Update timer continuously during game
            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                TIME -= TIME_PRECISION
                check_time = time.ticks_ms()
                display_time(TIME)
                
            if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
                break
                
            # Handle light sequence
            if state == 'light-1':
                now = time.ticks_ms()
                if now - s_time >= 2000:
                    esp.clearled()
                    state = 'light-2'
                    s_time = now
                else:
                    if current_pattern[0] == "R":
                        esp.red()
                    elif current_pattern[0] == "Y":
                        esp.yellow()
                    elif current_pattern[0] == "G":
                        esp.green()
            
            elif state == 'light-2':
                now = time.ticks_ms()
                if now - s_time >= 2000:
                    esp.clearled()
                    state = 'light-3'
                    s_time = now
                else:
                    if current_pattern[1] == "R":
                        esp.red()
                    elif current_pattern[1] == "Y":
                        esp.yellow()
                    elif current_pattern[1] == "G":
                        esp.green()
                    
            elif state == 'light-3':
                now = time.ticks_ms()
                if now - s_time >= 2000:
                    state = 'check-ans'
                    esp.clearled()
                    s_time = now
                else:
                    if current_pattern[2] == "R":
                        esp.red()
                    elif current_pattern[2] == "Y":
                        esp.yellow()
                    elif current_pattern[2] == "G":
                        esp.green()

            elif state == 'check-ans':
                now = time.ticks_ms()
                if now - s_time:
                    d = joy.direction()
                    print(d)
                    
                    if ans[pattern_num] in d:
                        passed = True
                        correct += 1
                        print("Pass level", level)
                        level += 1
                        show_strike_info(level)
                        break
                    if not (d[0] == 'Center' and d[1] == 'Center'):
                        # Incorrect answer
                        STRIKE += 1
                        # Show error message
                        esp.oled.fill(0)
                        esp.oled.text("INCORRECT!", 25, 20, 1)
                        esp.oled.text(f"Strikes: {STRIKE}/3", 20, 40, 1)
                        esp.oled.show()
                        
                        # Wait briefly so player can see the message
                        error_start = time.ticks_ms()
                        while time.ticks_ms() - error_start < 1000:  # Show for 1 second
                            # Keep updating the timer during this time
                            if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                                TIME -= TIME_PRECISION
                                check_time = time.ticks_ms()
                                display_time(TIME)
                        
                        if STRIKE >= STRIKE_LIMIT:
                            break
                        else:
                            show_strike_info(level)
                            time.sleep(1)
                            TIME -= 1
                            state = 'light-1'
                            s_time = time.ticks_ms()

# Game over screen
esp.oled.fill(0)
if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
    esp.oled.text("GAME OVER!", 25, 20, 1)
else:
    esp.oled.text("GAME COMPLETE!", 15, 20, 1)

esp.oled.text(f"Score: {correct}", 30, 40, 1)
esp.oled.show()

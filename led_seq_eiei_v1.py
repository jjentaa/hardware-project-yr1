from machine import Pin, I2C, PWM, ADC
import ssd1306, random, time

from esp32_s3 import ESP32_S3
from joystick import Joystick
from fourbutton import FourButton, FourLeds
from tm1637 import TM1637

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
    
# Game parameters
TIME = 100  # General game time in seconds
TIME_PRECISION = 0.1  # Update timer every 0.1 seconds
STRIKE = 0  # Track wrong answers
STRIKE_LIMIT = 3  # Game over after 3 strikes
check_time = time.ticks_ms()  # For timer tracking
s_time = time.ticks_ms()
check_ans_time = time.ticks_ms()
total_levels = 4
level = 1
correct = 0

pattern = {
    1:["R", "Y", "G", "B"],
    2:["Y", "G", "B", "R"],
    3:["R", "G", "Y", "B"],
    4:["Y", "R", "G", "B"],
    5:["G", "R", "B", "Y"],
    6:["G", "Y", "R", "B"]
}

ans = {
    1:[2,2,1,1],
    2:[2,1,2,1],
    3:[1,2,2,1],
    4:[2,1,1,2],
    5:[1,2,1,2],
    6:[1,1,1,3]
}

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

def draw_progress_bar(level):
    # Draw a progress bar showing level progress (1-4)
    esp.oled.rect(20, 55, 90, 8, 1)
    progress = int((level-1) * 22.5)  # Each level fills 1/4 of the bar
    if progress > 0:
        esp.oled.fill_rect(20, 55, progress, 8, 1)

def show_strike_info():
    esp.oled.fill(0)
    esp.oled.text("LED SEQUENCE EIEI", 0, 0, 1)
    esp.oled.text("LVL:" + str(level) + "/4", 0, 15, 1)
    esp.oled.text("Strikes: " + str(STRIKE) + "/" + str(STRIKE_LIMIT), 0, 30, 1)
    
    draw_progress_bar(level)
    esp.oled.show()
    
def show_counter_info():
    esp.oled.fill(0)
    esp.oled.text("LED SEQUENCE EIEI", 0, 0, 1)
    esp.oled.text("Red : "+str(counter[0])+" times", 0, 12, 1)
    esp.oled.text("Yellow : "+str(counter[1])+" times", 0, 24, 1)
    esp.oled.text("Blue : "+str(counter[2])+" times", 0, 36, 1)
    esp.oled.text("Green : "+str(counter[3])+" times", 0, 48, 1)
    esp.oled.show()

# Initialize game state
state = 'light-1'
pat = random.randint(1, 6)
print("Pattern:", pattern[pat])
print("Answer:", ans[pat])
counter = [0, 0, 0, 0]
display_time(TIME)  # Initialize timer display

# Main game loop
show_strike_info()
game_active = True

while game_active and TIME > 0 and STRIKE < STRIKE_LIMIT and level <= total_levels:

    update_timer()
    
    if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
        TIME = 0
        break
    
    if state == 'light-1':
        now = time.ticks_ms()
        if now - s_time >= 2000:
            state = 'light-2'
            s_time = now
            four_leds.clear()
        else:
            if pattern[pat][0] == 'R':
                four_leds.red(255)
            elif pattern[pat][0] == 'Y':
                four_leds.yellow(255)
            elif pattern[pat][0] == 'G':
                four_leds.green(255)
            elif pattern[pat][0] == 'B':
                four_leds.blue(255)

    elif state == 'light-2':
        now = time.ticks_ms()
        if now - s_time >= 2000:
            state = 'light-3'
            s_time = now
            four_leds.clear()
        else:
            if pattern[pat][1] == 'R':
                four_leds.red(255)
            elif pattern[pat][1] == 'Y':
                four_leds.yellow(255)
            elif pattern[pat][1] == 'G':
                four_leds.green(255)
            elif pattern[pat][1] == 'B':
                four_leds.blue(255)
    
    elif state == 'light-3':
        now = time.ticks_ms()
        if now - s_time >= 2000:
            state = 'light-4'
            s_time = now
            four_leds.clear()
        else:
            if pattern[pat][2] == 'R':
                four_leds.red(255)
            elif pattern[pat][2] == 'Y':
                four_leds.yellow(255)
            elif pattern[pat][2] == 'G':
                four_leds.green(255)
            elif pattern[pat][2] == 'B':
                four_leds.blue(255)
    
    elif state == 'light-4':
        now = time.ticks_ms()
        if now - s_time >= 2000:
            state = 'check-ans'
            s_time = now
            counter = [0, 0, 0, 0]  # Reset counter for new answer attempt
            four_leds.clear()
        else:
            if pattern[pat][3] == 'R':
                four_leds.red(255)
            elif pattern[pat][3] == 'Y':
                four_leds.yellow(255)
            elif pattern[pat][3] == 'G':
                four_leds.green(255)
            elif pattern[pat][3] == 'B':
                four_leds.blue(255)
    
    elif state == 'check-ans':
        # Keep updating timer while checking answer
        val = four_buttons.read()
        for i in range(4):
            if val[i] == True:
                counter[i] += 1
        
        show_counter_info()
        
        # Check if answer is submitted (using switch button)
        if esp.sw.value() == 0:
            print("Submitted answer:", counter)
            print("Correct answer:", ans[pat])
            
            # Check if answer is correct
            correct_answer = True
            for i in range(4):
                if counter[i] != ans[pat][i]:
                    correct_answer = False
                    break
            
            if correct_answer:
                # Display success message
                esp.oled.fill(0)
                esp.oled.text("CORRECT!", 25, 20, 1)
                esp.oled.text("Level passed!", 20, 30, 1)
                esp.oled.show()
                
                # Wait briefly to show success message
                success_start = time.ticks_ms()
                while time.ticks_ms() - success_start < 1500:  # Show for 1.5 seconds
                    update_timer()
                
                # Move to next level
                level += 1
                correct += 1
                
                if level > total_levels:
                    break  # Game complete
                
                # Set up next level
                pat = random.randint(1, 6)
                print("New pattern:", pattern[pat])
                print("New answer:", ans[pat])
                counter = [0, 0, 0, 0]
                show_strike_info()
                state = 'light-1'
                s_time = time.ticks_ms()
                
            else:
                # Incorrect answer
                STRIKE += 1
                
                # Show error message
                esp.oled.fill(0)
                esp.oled.text("INCORRECT!", 25, 20, 1)
                esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 20, 40, 1)
                esp.oled.show()
                
                # Wait briefly to show error message
                error_start = time.ticks_ms()
                while time.ticks_ms() - error_start < 1500:  # Show for 1.5 seconds
                    update_timer()
                
                if STRIKE >= STRIKE_LIMIT:
                    TIME = 0
                    break
                
                # Try again with same pattern
                counter = [0, 0, 0, 0]
                show_strike_info()
                state = 'light-1'
                s_time = time.ticks_ms()

# Game over screen
display_time(TIME)
esp.oled.fill(0)
if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
    esp.oled.text("GAME OVER!", 25, 20, 1)
else:
    esp.oled.text("GAME COMPLETE!", 15, 20, 1)
esp.oled.show()

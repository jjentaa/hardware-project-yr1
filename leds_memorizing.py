from machine import Pin, I2C, PWM, ADC
import ssd1306, time, random

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

# Game configuration
TIME = 100  # seconds
TIME_PRECISION = 0.1
STRIKE = 0
LIMIT_STRIKE = 3
STRIKE = 0
level = 1
max_level = 7

# Game state variables
sequences = []
player_input = []
pattern_timer = 0
display_led_index = 0
display_led_state = False
input_timeout = 0
flash_timer = 0
game_state = "sequence"  # sequence, input, success, fail, gameover

led_functions = [four_leds.red, four_leds.yellow, four_leds.blue, four_leds.green]

# Game initialization
sequences.append(random.randint(0, 3))
last_update_time = time.ticks_ms()
pattern_timer = time.ticks_ms()
display_led_index = 0
display_led_state = False

def display_center(text, y=30):
    esp.oled.text(text,60-len(text)*3,y,1)

def display_time(sec):
    minute = int(sec // 60)
    sec %= 60
    tm.clear()
    if esp.board_id == 1:
        tm.show(f'{minute:02.0f}{sec:02.1f}', 7)
    elif esp.board_id == 2:
        tm.show(f'{minute:02.0f}{sec:02.0f}', 1)

def update_display():
    # Update 7-segment display
    global TIME
    display_time(TIME)
        
    # Update OLED with minimal information
    esp.oled.fill(0)
    esp.oled.rect(0, 0, 128, 64, 1)  # Border
    esp.oled.text(f"Level: {level}", 10, 10, 1)
    esp.oled.text(f"Strikes: {STRIKE}/{LIMIT_STRIKE}", 10, 25, 1)
#     
    if game_state == "fail":
        esp.oled.text("WRONG!", 40, 45, 1)
    elif game_state == "success":
        esp.oled.text("CORRECT!", 35, 45, 1)
            
    esp.oled.show()

# Main game loop
while TIME > 0:
    current_time = time.ticks_ms()
    
    # Update time
    if time.ticks_diff(current_time, last_update_time) >= TIME_PRECISION * 1000:
        TIME -= TIME_PRECISION
        last_update_time = current_time
        
        if TIME <= 0 or STRIKE >= LIMIT_STRIKE:
            TIME = 0
    
    # State machine
    if game_state == "sequence":
        # Display the sequence: beep each LED only once
        if display_led_state:  # LED is currently on
            if time.ticks_diff(current_time, pattern_timer) > 300:
                four_leds.clear()
                display_led_state = False
                pattern_timer = current_time
        else:  # LED is off, wait before next LED
            if time.ticks_diff(current_time, pattern_timer) > 200:
                if display_led_index < len(sequences):
                    # Show the next LED once
                    led_functions[sequences[display_led_index]](255)
                    display_led_state = True
                    pattern_timer = current_time
                    display_led_index += 1
                else:
                    # Sequence display complete, move to input state
                    game_state = "input"
                    player_input = []
                    input_timeout = current_time
                    four_leds.clear()
    
    elif game_state == "input":
        # Accumulate button presses without immediate evaluation
        button_presses = four_buttons.read()
        
        for i in range(4):
            if button_presses[i]:
                # Flash the LED for this button
                led_functions[i](255)
                flash_timer = current_time
                
                # Only add the press if we haven't reached the sequence length
                if len(player_input) < len(sequences):
                    player_input.append(i)
                    input_timeout = current_time  # reset timeout on valid press
        
        # Turn off LED after brief flash
        if time.ticks_diff(current_time, flash_timer) > 200:
            four_leds.clear()
        
        # Once the full sequence is entered, evaluate the answer
        if len(player_input) == len(sequences):
            if player_input == sequences:
                if level < max_level:
                    level += 1
                game_state = "success"
                pattern_timer = current_time
            else:
                STRIKE += 1
                game_state = "fail"
                pattern_timer = current_time
        
        # Check for input timeout
        if time.ticks_diff(current_time, input_timeout) > 5000:
            # Replay the same sequence
            game_state = "sequence"
            pattern_timer = current_time
            display_led_index = 0
            display_led_state = False
            player_input = []
    
    elif game_state == "success":
        if time.ticks_diff(current_time, pattern_timer) > 500:
            four_leds.clear()
        if time.ticks_diff(current_time, pattern_timer) > 2000:
            if level > max_level:
                game_state = "gameover"
            else:
                four_leds.clear()
                sequences.append(random.randint(0, 3))
                game_state = "sequence"
                pattern_timer = current_time
                display_led_index = 0
                display_led_state = False  # Start fresh for sequence display
    
    elif game_state == "fail":
        if time.ticks_diff(current_time, pattern_timer) > 500:
            four_leds.clear()
        if time.ticks_diff(current_time, pattern_timer) > 2000:
            if STRIKE >= LIMIT_STRIKE:
                game_state = "gameover"
            else:
                # Replay the same sequence
                game_state = "sequence"
                pattern_timer = current_time
                display_led_index = 0
                display_led_state = False
                four_leds.clear()
                player_input = []
    
    elif game_state == "gameover":
        four_leds.clear()
        break
    
    # Update displays
    update_display()

if TIME > 0:
    esp.oled.fill(0)
    display_center("Passed", 30)
    esp.oled.show()
else:
    esp.oled.fill(0)
    display_center("Game over.", 30)
    esp.oled.show()


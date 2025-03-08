from machine import Pin, I2C, PWM, ADC
import ssd1306, time, random
import array

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

TIME = 100  # General bomb time
TIME_PRECISION = 0.1
STRIKE = 0
STRIKE_LIMIT = 3
SUBMIT_COOLDOWN = 500  # 500ms cooldown for submit button
last_submit_time = 0

morse_dict = {
    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 'g': '--.', 'h': '....',
    'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---', 'p': '.--.',
    'q': '--.-', 'r': '.-.', 's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
    'y': '-.--', 'z': '--..'
}

word_dict = {
    'bombs': 38.07, 'node': 38.17, 'else': 38.32, 'board': 38.59,
    'enum': 38.69, 'unit': 38.76, 'next': 38.80, 'unix': 38.84
}
word_list = list(word_dict.keys())
freq_list = list(word_dict.values())
sorted_freq_list = sorted(word_dict.values())

option = random.randint(0, 10000) % len(word_dict)
i = random.randint(0, 10000) % len(word_dict)
print(option, word_list[option], word_dict[word_list[option]])
check_time = time.ticks_ms()
last_time = time.ticks_ms()
morse_index = 0
letter_index = 0
is_dot_dash = True
is_beeping = False
morse_timer = time.ticks_ms()
joystick_cooldown = time.ticks_ms()

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
        
def update_oled(side=None):
    select_freq = sorted_freq_list[i]
    esp.oled.fill(0)
    esp.oled.rect(5, 3, 120, 15, 1)
    esp.oled.rect(20, 28, 90, 30, 1)
    esp.oled.text(f"{select_freq:.2f} MHz", 29, 38, 1)
    rect_center = int((select_freq - 38) * 115)
    esp.oled.fill_rect(rect_center - 1, 1, rect_center // 16 + 1, 19, 1)
    left_triangle = array.array('i', [13, 31, 13, 51, 3, 41])
    right_triangle = array.array('i', [115, 31, 115, 51, 125, 41])
    esp.oled.poly(0, 0, left_triangle, 1)
    esp.oled.poly(0, 0, right_triangle, 1)
    if side == 'left':
        esp.oled.poly(0, 0, left_triangle, 1, 1)
    if side == 'right':
        esp.oled.poly(0, 0, right_triangle, 1, 1)
    esp.oled.show()

def update_morse():
    global morse_index, letter_index, is_dot_dash, is_beeping, morse_timer
    if time.ticks_ms() - morse_timer >= 300:
        if morse_index < len(word_list[option]):
            letter = word_list[option][morse_index]
            if letter_index < len(morse_dict[letter]):
                symbol = morse_dict[letter][letter_index]
                if is_dot_dash:
                    esp.yellow(512)
                    is_beeping = True
                    delay = 300 if symbol == '.' else 1000
                else:
                    esp.clearled()
                    delay = 450
                    letter_index += 1
                is_dot_dash = not is_dot_dash
            else:
                morse_index += 1
                letter_index = 0
                delay = 1000
        else:
            morse_index = 0
            delay = 3000
        morse_timer = time.ticks_ms() + delay

display_time(TIME)
update_oled()

while TIME > 0:
    update_timer()
    
    if time.ticks_ms() - joystick_cooldown > 200:
        joy_x = joy.read()[0]
        if joy_x == -1 and i > 0:
            i -= 1
            update_oled('left')
            joystick_cooldown = time.ticks_ms()
        elif joy_x == 1 and i < len(freq_list) - 1:
            i += 1
            update_oled('right')
            joystick_cooldown = time.ticks_ms()
        elif joy_x == 0:
            update_oled()
    
    if joy.read()[2]:
        if time.ticks_ms() - last_submit_time > SUBMIT_COOLDOWN:
            last_submit_time = time.ticks_ms()
            if sorted_freq_list[i] == word_dict[word_list[option]]:
                break  # Correct selection, exit loop
            else:
                STRIKE += 1
                # Add visual feedback for incorrect answer
                esp.oled.fill(0)
                esp.oled.text("INCORRECT!", 25, 20, 1)
                esp.oled.text(f"Strikes: {STRIKE}/3", 20, 40, 1)
                esp.oled.show()
                # Wait briefly so player can see the message
                error_start = time.ticks_ms()
                while time.ticks_ms() - error_start < 1000:  # Show for 1 second
                    update_timer()
                    pass
                if STRIKE >= STRIKE_LIMIT:
                    TIME = 0
                    
                update_oled()
    
    update_morse()
    
if TIME > 0:
    esp.oled.fill(0)
    display_center("Passed", 30)
    esp.oled.show()
else:
    esp.oled.fill(0)
    display_center("Game over.", 30)
    esp.oled.show()


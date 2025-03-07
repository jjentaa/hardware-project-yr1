from machine import Pin, I2C, PWM, ADC
import ssd1306, time, esp32_s3, random
import array
from joystick import Joystick
from complexbutton import ComplexButton

esp = esp32_s3.ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
tm = ComplexButton(10, 12, 11)
joy = Joystick(x_invert=True)

TIME = 100  # General bomb time
TIME_PRECISION = 0.1
STRIKE = 0
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

option = random.randint(0, len(word_dict) - 1)
i = random.randint(0, len(freq_list) - 1)
print(option, word_list[option], word_dict[word_list[option]])
check_time = time.ticks_ms()
last_time = time.ticks_ms()
morse_index = 0
letter_index = 0
is_dot_dash = True
is_beeping = False
morse_timer = time.ticks_ms()
joystick_cooldown = time.ticks_ms()

def display_time(sec):
    minute = sec // 60
    sec %= 60
    sec = round(sec, 3)
    tm.tm.clear()
    tm.tm.show(f'{minute:02}{sec:02}', 7)

def update_oled():
    select_freq = sorted_freq_list[i]
    esp.oled.fill(0)
    esp.oled.rect(5, 3, 120, 15, 1)
    esp.oled.rect(20, 28, 90, 30, 1)
    esp.oled.text(f"{select_freq} MHz", 29, 38, 1)
    rect_center = int((select_freq - 38) * 115)
    esp.oled.fill_rect(rect_center - 1, 1, rect_center // 16 + 1, 19, 1)
    left_triangle = array.array('i', [13, 31, 13, 51, 3, 41])
    right_triangle = array.array('i', [115, 31, 115, 51, 125, 41])
    esp.oled.poly(0, 0, left_triangle, 1)
    esp.oled.poly(0, 0, right_triangle, 1)
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
    if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
        TIME -= TIME_PRECISION
        check_time = time.ticks_ms()
        display_time(TIME)
    
    if time.ticks_ms() - joystick_cooldown > 200:
        joy_x = joy.read()[0]
        if joy_x == -1 and i > 0:
            i -= 1
            update_oled()
            joystick_cooldown = time.ticks_ms()
        elif joy_x == 1 and i < len(freq_list) - 1:
            i += 1
            update_oled()
            joystick_cooldown = time.ticks_ms()
    
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
                    # Keep updating the timer during this time
                    if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
                        TIME -= TIME_PRECISION
                        check_time = time.ticks_ms()
                        display_time(TIME)
                    pass
                if STRIKE >= 3:
                    TIME = 0
                    
                update_oled()
    
    update_morse()
    
esp.oled.fill(0)
esp.oled.text("Game Over", 30, 30, 1)
esp.oled.show()

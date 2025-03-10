from machine import Pin, I2C, PWM, ADC
import ssd1306, random, time, array

from esp32_s3 import ESP32_S3
from joystick import Joystick

import network
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS,
    TOPIC_PREFIX
)
from umqtt.simple import MQTTClient

# Initialize components
esp = ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000, board_id=2) #--- CHANGE BOARD_ID
joy = Joystick(x_invert=True)

if esp.board_id == 1:
    from complexbutton import ComplexButton
    complexbutton = ComplexButton(10, 12, 11)
    tm = complexbutton.tm
elif esp.board_id == 2:
    from tm1637 import TM1637
    from fourbutton_leds import FourButton, FourLeds
    four_buttons = FourButton(5, 6, 18, 8)
    four_leds = FourLeds(r=9, y=10, g=45, b=21)
    tm = TM1637(12, 11)

# TOPIC
TOPIC_TIME = f'{TOPIC_PREFIX}/{esp.board_id}/time'
TOPIC_STRIKE = f'{TOPIC_PREFIX}/{esp.board_id}/strike'
TOPIC_SWITCH = f"{TOPIC_PREFIX}/{esp.board_id}/switch"
TOPIC_SECRET_CODE = f"{TOPIC_PREFIX}/{esp.board_id}/secret_code"
TOPIC_GENERAL = f'{TOPIC_PREFIX}/general'
TOPIC_START = f'{TOPIC_PREFIX}/start'

# GAME MODE SELECTION
all_game_modes = ['normal', 'manual', 'demo']
game_mode = 'normal' # Choose either 'normal', 'manual', 'demo' or else the game will start in 'normal' mode
seed = None # Default: None, Can fix seed to get the same game, must be non-negative integers

# Global variables
TIME = 600  # 10 minutes in seconds
STRIKE = 0
STRIKE_LIMIT = 3
TIME_PRECISION = 1
GAME_START = False
check_time = time.ticks_ms()


def connect_wifi():
    mac = ':'.join(f'{b:02X}' for b in wifi.config('mac'))
    print(f'WiFi MAC address is {mac}')
    wifi.active(True)
    print(f'Connecting to WiFi {WIFI_SSID}.')
    wifi.connect(WIFI_SSID, WIFI_PASS)
    while not wifi.isconnected():
        print('.', end='')
        time.sleep(0.5)
    print('\nWiFi connected.')


def connect_mqtt():
    print(f'Connecting to MQTT broker at {MQTT_BROKER}.')
    mqtt.connect()
    mqtt.set_callback(mqtt_callback)
    mqtt.subscribe(TOPIC_GENERAL)
    mqtt.subscribe(TOPIC_START)
    print('MQTT broker connected.')


def mqtt_callback(topic, payload):
    global GAME_START
    if topic.decode() == TOPIC_START and payload.decode() == "start":
        GAME_START = True
        
# Common functions
def display_time(sec):
    """Display the remaining time on the 7-segment display."""
    minute = int(sec // 60)
    sec %= 60
    tm.clear()
    if esp.board_id == 1:
        tm.show(f'{minute:02.0f}{sec:02.1f}', 5)
    elif esp.board_id == 2:
        tm.show(f'{minute:02.0f}{sec:02.0f}', 1)
        
    mqtt.check_msg()
    mqtt.publish(TOPIC_TIME, f"{minute:02.0f}:{sec:02.0f}")
    mqtt.publish(TOPIC_STRIKE, str(STRIKE))

def display_center(text, y=30):
    """Center text on the OLED display."""
    esp.oled.text(text, 60 - len(text) * 3, y, 1)

def update_timer():
    """Update the global TIME variable and refresh the display."""
    global TIME, check_time
    if time.ticks_ms() - check_time >= TIME_PRECISION * 1000:
        TIME -= TIME_PRECISION
        check_time = time.ticks_ms()
        display_time(TIME)

# Game functions

def play_maze():
    """Maze game: Navigate from start to goal using joystick."""
    global TIME, STRIKE
    maze_patterns = [
        [[0b0001, 0b0011, 0b0011, 0b0100], [0b0001, 0b0011, 0b0110, 0b1100], [0b0001, 0b0110, 0b1101, 0b1010], [0b0001, 0b1011, 0b1011, 0b0010]],
        [[0b0101, 0b0011, 0b0111, 0b0110], [0b1001, 0b0110, 0b1100, 0b1000], [0b0101, 0b1110, 0b1101, 0b0010], [0b1000, 0b1000, 0b1001, 0b0010]],
        [[0b0100, 0b0101, 0b0010, 0b0100], [0b1001, 0b1110, 0b0101, 0b1110], [0b0100, 0b1101, 0b1010, 0b1100], [0b1001, 0b1010, 0b0001, 0b1010]],
        [[0b0101, 0b0011, 0b0110, 0b0100], [0b1001, 0b0010, 0b1101, 0b1010], [0b0101, 0b0011, 0b1110, 0b0100], [0b1000, 0b0001, 0b1011, 0b1010]],
        [[0b0101, 0b0011, 0b0111, 0b0110], [0b1101, 0b0010, 0b1000, 0b1000], [0b1001, 0b0111, 0b0111, 0b0010], [0b0001, 0b1010, 0b1001, 0b0010]],
        [[0b0100, 0b0101, 0b0011, 0b0110], [0b1001, 0b1110, 0b0101, 0b1010], [0b0101, 0b1010, 0b1001, 0b0110], [0b1001, 0b0011, 0b0010, 0b1000]]
    ]
    recog_patterns = {0: ((1,0), (2,1)), 1: ((3,0), (0,1)), 2: ((3,1), (0,3)), 3: ((2,1), (2,3)), 4: ((0,2), (3,2)), 5: ((2,0), (3,3))}
    DIRECTIONS = {(0, -1): 0b1000, (0, 1): 0b0100, (-1, 0): 0b0010, (1, 0): 0b0001, (0, 0): 0b1111}
    
    rand = random.randint(0, 5)
    maze = maze_patterns[rand]
    recog = recog_patterns[rand]
    
    def get_random_positions():
        while True:
            start = (random.randint(0, 1), random.randint(0, 1))
            end = (random.randint(2, 3), random.randint(2, 3))
            if start != end:
                return start, end
    
    (player_x, player_y), (goal_x, goal_y) = get_random_positions()
    
    def can_move(new_x, new_y):
        dx, dy = new_x - player_x, new_y - player_y
        if (dx, dy) not in DIRECTIONS:
            return False
        return (maze[player_y][player_x] & DIRECTIONS[(dx, dy)]) != 0
    
    def move_to(new_x, new_y):
        global STRIKE
        if can_move(new_x, new_y):
            nonlocal player_x, player_y
            player_x, player_y = new_x, new_y
            update_display()
        else:
            esp.oled.text("Invalid", 70, 20, 1)
            esp.oled.text("move!", 80, 30, 1)
            esp.oled.show()
            STRIKE += 1
    
    def update_display():
        esp.oled.fill(0)
        cell_size = 16
        margin = 8
        for row in range(4):
            for col in range(4):
                x, y = col * cell_size + margin, row * cell_size + margin
                if (col, row) == (goal_x, goal_y):
                    esp.oled.text("X", x-2, y-2, 1)
                elif (col, row) == (player_x, player_y):
                    esp.oled.fill_rect(x - 4, y - 4, 12, 12, 1)
                else:
                    esp.oled.fill_rect(x, y, 4, 4, 1)
                for pattern in recog:
                    if (col, row) == pattern:
                        esp.oled.ellipse(x + 2, y + 2, 7, 7, 1)
        esp.oled.show()
    
    print(f'rand = {rand}')
    print(f'recog = {recog}')
    print(f'Start:({player_x},{player_y})\nEnd:({goal_x},{goal_y})')
    update_display()
    xy = complexbutton.get_xy() if esp.board_id == 1 else (0, 0)
    old_xy = xy
    while TIME > 0 and STRIKE < STRIKE_LIMIT:
        update_timer()
        xy = complexbutton.get_xy() if esp.board_id == 1 else (0, 0)
        if xy and xy != old_xy:
            old_xy = xy
            new_x, new_y = xy
            if 0 <= new_x < 4 and 0 <= new_y < 4:
                move_to(new_x, new_y)
                if (player_x, player_y) == (goal_x, goal_y):
                    break
    esp.oled.fill(0)
    esp.oled.show()

def play_thebutton():
    """The Button game: Press or hold the button based on instructions."""
    global TIME, STRIKE
    texts = ["Abort", "Defuse", "Hold", "Press", "Touch"]
    text = random.choice(texts)
    rand = random.randint(0, 2)
    if esp.board_id == 1: # ------------------ DEPENDS ON THE BOARD
        colors = [[0, 2], [1], [2], [0, 1], [1]]
    elif esp.board_id == 2:
        colors = [[0, 1], [1, 2], [0], [2], [0, 2]]
    esp.clearled()
    if rand == 0:
        esp.red(255)
    elif rand == 1:
        esp.yellow(255)
    elif rand == 2:
        esp.green(255)
    print(text)
    esp.oled.fill(0)
    esp.oled.ellipse(64, 32, 31, 31, 1, 0)
    display_center(text, 30)
    esp.oled.show()
    
    sudden = False
    hold = False
    if text == 'Abort':
        sudden = (rand not in colors[0])
    elif text == 'Defuse':
        sudden = (rand not in colors[1])
    elif text == 'Hold':
        sudden = (rand not in colors[2])
    elif text == 'Press':
        sudden = (rand not in colors[3])
    elif text == 'Touch':
        sudden = (rand not in colors[4])
    
    no_mistake = True
    last_time = time.ticks_ms()
    if sudden:
        print("Sudden mode")
        while esp.sw.value() == 1 and TIME > 0:
            last_time = time.ticks_ms()
            update_timer()
        while esp.sw.value() == 0 and TIME > 0:
            update_timer()
        if time.ticks_ms() - last_time >= 500:
            no_mistake = False
    else:
        print("Hold mode")
        wait_time = random.randint(3, 3) * 1000
        while esp.sw.value() == 1 and TIME > 0:
            last_time = time.ticks_ms()
            update_timer()
        while time.ticks_ms() - last_time <= wait_time and TIME > 0:
            update_timer()
            if esp.sw.value() == 1:
                no_mistake = False
                break
        else:
            esp.oled.fill(0)
            display_center("Release", 15)
            display_center("the button", 30)
            esp.oled.show()
            last_time = time.ticks_ms()
            while time.ticks_ms() - last_time <= 1500 and TIME > 0:
                update_timer()
                if esp.sw.value() == 1:
                    break
            else:
                no_mistake = False
    
    if not no_mistake:
        STRIKE += 1
        esp.oled.fill(0)
        display_center("Failed", 15)
        display_center("Try again.", 30)
        esp.oled.show()
        while time.ticks_ms() - last_time <= 2000 and TIME > 0:
            update_timer()
    else:
        esp.oled.fill(0)
        esp.oled.show()

def play_morse_code():
    """Morse Code game: Match frequency to decode word."""
    global TIME, STRIKE
    morse_dict = {'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--', 'z': '--..'}
    if esp.board_id == 1:
        word_dict = {'bombs': 38.07, 'node': 38.17, 'else': 38.32, 'board': 38.59, 'enum': 38.69, 'unit': 38.76, 'next': 38.80, 'unix': 38.84}
        average_mhz = 38
    elif esp.board_id == 2:
        word_dict = {'heap': 84.08, 'core': 84.10, 'heat': 84.29, 'code': 84.31, 'chip': 84.52, 'hack': 84.63, 'hash': 84.79, 'chmod': 84.95}
        average_mhz = 84
    word_list = list(word_dict.keys())
    freq_list = list(word_dict.values())
    sorted_freq_list = sorted(freq_list)
    
    option = random.randint(0, 10000) % len(word_dict)
    i = random.randint(0, 10000) % len(word_dict)
    last_submit_time = 0
    morse_index = 0
    letter_index = 0
    is_dot_dash = True
    morse_timer = time.ticks_ms()
    joystick_cooldown = time.ticks_ms()
    old_joy_sw = joy.read()[2]
    print(f"Option: {option}, Word: {word_list[option]}, Correct Frequency: {word_dict[word_list[option]]}")  # Debug: Solution
    
    def update_oled(side=None):
        select_freq = sorted_freq_list[i]
        esp.oled.fill(0)
        esp.oled.rect(5, 3, 120, 15, 1)
        esp.oled.rect(20, 28, 90, 30, 1)
        esp.oled.text(f"{select_freq:.2f} MHz", 29, 38, 1)
        rect_center = int((select_freq - average_mhz) * 115)
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
    
        # Timing constants
    DOT_DURATION = 300    # ms
    DASH_DURATION = 1000  # ms
    INTER_SYMBOL_GAP = 450  # ms
    INTER_LETTER_GAP = 1000  # ms
    INTER_WORD_GAP = 3000    # ms

    # Initialize
    state = 'symbol'
    next_action_time = time.ticks_ms()
    morse_index = 0
    letter_index = 0

    def update_morse():
        nonlocal state, next_action_time, morse_index, letter_index
        if time.ticks_ms() >= next_action_time:
            if state == 'symbol':
                if morse_index < len(word_list[option]):
                    letter = word_list[option][morse_index]
                    if letter_index < len(morse_dict[letter]):
                        symbol = morse_dict[letter][letter_index]
                        esp.yellow(512)  # Light LED
                        duration = DOT_DURATION if symbol == '.' else DASH_DURATION
                        next_action_time = time.ticks_ms() + duration
                        state = 'clear_symbol'
                    else:
                        state = 'inter_letter'
                        next_action_time = time.ticks_ms() + INTER_LETTER_GAP
                        morse_index += 1
                        letter_index = 0
                else:
                    state = 'inter_word'
                    next_action_time = time.ticks_ms() + INTER_WORD_GAP
                    morse_index = 0
            elif state == 'clear_symbol':
                esp.clearled()  # Turn off LED
                next_action_time = time.ticks_ms() + INTER_SYMBOL_GAP
                state = 'symbol'
                letter_index += 1
            elif state == 'inter_letter':
                state = 'symbol'
            elif state == 'inter_word':
                state = 'symbol'
    
    update_timer()
    update_oled()
    while TIME > 0 and STRIKE < STRIKE_LIMIT:
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
                
        if joy.read()[2] == False:
            old_joy_sw = joy.read()[2]
        if joy.read()[2] and old_joy_sw != True or esp.sw.value() == 0:
            last_submit_time = time.ticks_ms()
            selected_freq = sorted_freq_list[i]
            correct_freq = word_dict[word_list[option]]
            old_joy_sw = joy.read()[2]
            if selected_freq == correct_freq:
                break
            else:
                STRIKE += 1
                esp.oled.fill(0)
                esp.oled.text("INCORRECT!", 25, 20, 1)
                esp.oled.text(f"Strikes: {STRIKE}/3", 20, 40, 1)
                esp.oled.show()
                error_start = time.ticks_ms()
                while time.ticks_ms() - error_start < 1000:
                    update_timer()
                update_oled()
        update_morse()
    esp.oled.fill(0)
    esp.oled.show()

def play_led_memorizing():
    """LED Memorizing game: Repeat the LED sequence."""
    global TIME, STRIKE
    level = 1
    max_level = 7
    sequences = [random.randint(0, 3)]
    player_input = []
    pattern_timer = time.ticks_ms()
    display_led_index = 0
    display_led_state = False
    input_timeout = 0
    flash_timer = 0
    game_state = "sequence"
    led_functions = [four_leds.red, four_leds.yellow, four_leds.blue, four_leds.green]
    last_update_time = time.ticks_ms()
    
    def update_display():
        update_timer()
        esp.oled.fill(0)
        esp.oled.rect(0, 0, 128, 64, 1)
        esp.oled.text(f"LED Memorizing", 10, 5, 1)
        esp.oled.text(f"Level: {level}", 10, 20, 1)
        esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 10, 30, 1)
        if game_state == "fail":
            esp.oled.text("WRONG!", 40, 45, 1)
        elif game_state == "success":
            esp.oled.text("CORRECT!", 35, 45, 1)
        esp.oled.show()
    
    while TIME > 0 and STRIKE < STRIKE_LIMIT:
        current_time = time.ticks_ms()
        if game_state == "sequence":
            print(f'Sequence = {sequences}')
            if display_led_state:
                if time.ticks_diff(current_time, pattern_timer) > 300:
                    four_leds.clear()
                    display_led_state = False
                    pattern_timer = current_time
            else:
                if time.ticks_diff(current_time, pattern_timer) > 200:
                    if display_led_index < len(sequences):
                        led_functions[sequences[display_led_index]](255)
                        display_led_state = True
                        pattern_timer = current_time
                        display_led_index += 1
                    else:
                        game_state = "input"
                        player_input = []
                        input_timeout = current_time
                        four_leds.clear()
        elif game_state == "input":
            button_presses = four_buttons.read()
            for i in range(4):
                if button_presses[i]:
                    led_functions[i](255)
                    flash_timer = current_time
                    if len(player_input) < len(sequences):
                        player_input.append(i)
                        input_timeout = current_time
            if time.ticks_diff(current_time, flash_timer) > 200:
                four_leds.clear()
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
            if time.ticks_diff(current_time, input_timeout) > 5000:
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
                    break
                sequences.append(random.randint(0, 3))
                game_state = "sequence"
                pattern_timer = current_time
                display_led_index = 0
                display_led_state = False
        elif game_state == "fail":
            if time.ticks_diff(current_time, pattern_timer) > 500:
                four_leds.clear()
            if time.ticks_diff(current_time, pattern_timer) > 2000:
                game_state = "sequence"
                pattern_timer = current_time
                display_led_index = 0
                display_led_state = False
                player_input = []
        update_display()
    esp.oled.fill(0)
    esp.oled.show()

def play_led_sequence():
    """LED Sequence game: Match joystick direction to LED pattern."""
    global TIME, STRIKE
    if esp.board_id == 1:
        pattern1 = {1:["R", "Y"], 2:["Y", "G"], 3:["R", "G"], 4:["Y", "R"], 5:["G", "R"], 6:["G", "Y"]}
        pattern2 = {1:["R", "Y", "G"], 2:["Y", "G", "R"], 3:["R", "G", "Y"], 4:["Y", "R", "G"], 5:["G", "R", "Y"], 6:["G", "Y", "R"]}
        ans = {1:"Right", 2:"Left", 3:"Up", 4:"Up", 5:"Down", 6:"Down"}
    elif esp.board_id == 2:
        pattern1 = {1:["R", "G"], 2:["Y", "G"], 3:["G", "Y"], 4:["Y", "R"], 5:["R", "Y"], 6:["G", "R"]}
        pattern2 = {1:["G", "R", "Y"], 2:["Y", "R", "G"], 3:["Y", "G", "R"], 4:["R", "G", "Y"], 5:["G", "Y", "R"], 6:["R", "Y", "G"]}
        ans = {1:"Left", 2:"Up", 3:"Down", 4:"Right", 5:"Left", 6:"Up"}
    state = 'light-1'
    level = 1
    total_levels = 4
    
    def draw_progress_bar(level):
        esp.oled.rect(20, 28, 90, 8, 1)
        progress = int((level-1) * 22.5)
        if progress > 0:
            esp.oled.fill_rect(20, 28, progress, 8, 1)
    
    def show_strike_info(level):
        esp.oled.fill(0)
        esp.oled.rect(0, 0, 128, 16, 1)
        esp.oled.text("LED SEQUENCE", 12, 4, 1)
        draw_progress_bar(level)
        esp.oled.text(f"LVL:{level}/4", 5, 40, 1)
        esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 0, 52, 1)
        esp.oled.show()
    
    show_strike_info(level)
    while TIME > 0 and STRIKE < STRIKE_LIMIT and level <= total_levels:
        update_timer()
        pattern_set = pattern1 if level <= 2 else pattern2
        pattern_num = random.randint(1, 6)
        current_pattern = pattern_set[pattern_num]
        print(f'Current Pattern : {current_pattern}') # Debug
        print(f'Correct Answer  : {ans[pattern_num]}') # Debug
        passed = False
        state = 'light-1'
        s_time = time.ticks_ms()
        while not passed and TIME > 0 and STRIKE < STRIKE_LIMIT:
            update_timer()
            now = time.ticks_ms()
            if state == 'light-1':
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
                if now - s_time >= 2000:
                    esp.clearled()
                    state = 'light-3' if level > 2 else 'check-ans'
                    s_time = now
                else:
                    if current_pattern[1] == "R":
                        esp.red()
                    elif current_pattern[1] == "Y":
                        esp.yellow()
                    elif current_pattern[1] == "G":
                        esp.green()
            elif state == 'light-3' and level > 2:
                if now - s_time >= 2000:
                    esp.clearled()
                    state = 'check-ans'
                    s_time = now
                else:
                    if current_pattern[2] == "R":
                        esp.red()
                    elif current_pattern[2] == "Y":
                        esp.yellow()
                    elif current_pattern[2] == "G":
                        esp.green()
            elif state == 'check-ans':
                d = joy.direction()
                if ans[pattern_num] in d:
                    passed = True
                    level += 1
                    show_strike_info(level)
                    break
                if not (d[0] == 'Center' and d[1] == 'Center'):
                    STRIKE += 1
                    esp.oled.fill(0)
                    esp.oled.text("INCORRECT!", 25, 20, 1)
                    esp.oled.text(f"Strikes: {STRIKE}/3", 20, 40, 1)
                    esp.oled.show()
                    error_start = time.ticks_ms()
                    while time.ticks_ms() - error_start < 1000:
                        update_timer()
                    show_strike_info(level)
                    time.sleep(1)
                    TIME -= 1
                    state = 'light-1'
                    s_time = time.ticks_ms()
    esp.oled.fill(0)
    display_center("Passed" if TIME > 0 else "Game over.", 30)
    esp.oled.show()

def play_led_seq_eiei():
    """LED Sequence Eiei game: Press buttons to match LED counts."""
    global TIME, STRIKE
    pattern = {1:["R", "Y", "G", "B"], 2:["Y", "G", "B", "R"], 3:["R", "G", "Y", "B"], 4:["Y", "R", "G", "B"], 5:["G", "R", "B", "Y"], 6:["G", "Y", "R", "B"]}
    ans = {
        1:[0,1,0,1],
        2:[1,0,1,0],
        3:[0,0,2,0],
        4:[1,0,0,1],
        5:[0,2,0,0],
        6:[0,0,0,2]
    }
    s_time = time.ticks_ms()
    state = 'light-1'
    level = 1
    total_levels = 4
    pat = random.randint(1, 6)
    print(f'Current Pattern : {pattern[pat]}') # Debug
    print(f'Correct Answer  : {ans[pat]}') # Debug
    counter = [0, 0, 0, 0]
    
    def draw_progress_bar(level):
        esp.oled.rect(20, 55, 90, 8, 1)
        progress = int((level-1) * 22.5)
        if progress > 0:
            esp.oled.fill_rect(20, 55, progress, 8, 1)
    
    def show_strike_info():
        esp.oled.fill(0)
        esp.oled.text("LED SEQUENCE EIEI", 0, 0, 1)
        esp.oled.text(f"LVL:{level}/4", 0, 15, 1)
        esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 0, 30, 1)
        draw_progress_bar(level)
        esp.oled.show()
    
    def show_counter_info():
        esp.oled.fill(0)
        esp.oled.text("LED SEQUENCE EIEI", 0, 0, 1)
        esp.oled.text(f"Red: {counter[0]} times", 0, 12, 1)
        esp.oled.text(f"Yellow: {counter[1]} times", 0, 24, 1)
        esp.oled.text(f"Blue: {counter[2]} times", 0, 36, 1)
        esp.oled.text(f"Green: {counter[3]} times", 0, 48, 1)
        esp.oled.show()
    
    show_strike_info()
    while TIME > 0 and STRIKE < STRIKE_LIMIT and level <= total_levels:
        update_timer()
        now = time.ticks_ms()
        if state == 'light-1':
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
            if now - s_time >= 2000:
                state = 'check-ans'
                s_time = now
                counter = [0, 0, 0, 0]
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
            val = four_buttons.read()
            for i in range(4):
                if val[i]:
                    counter[i] += 1
            show_counter_info()
            if esp.sw.value() == 0 or joy.read()[2]:
                correct_answer = all(counter[i] == ans[pat][i] for i in range(4))
                if correct_answer:
                    esp.oled.fill(0)
                    esp.oled.text("CORRECT!", 25, 20, 1)
                    esp.oled.text("Level passed!", 20, 30, 1)
                    esp.oled.show()
                    success_start = time.ticks_ms()
                    while time.ticks_ms() - success_start < 1500:
                        update_timer()
                    level += 1
                    if level > total_levels:
                        break
                    pat = random.randint(1, 6)
                    print(f'Current Pattern : {pattern[pat]}') # Debug
                    print(f'Correct Answer  : {ans[pat]}') # Debug
                    show_strike_info()
                    state = 'light-1'
                    s_time = time.ticks_ms()
                else:
                    STRIKE += 1
                    esp.oled.fill(0)
                    esp.oled.text("INCORRECT!", 25, 20, 1)
                    esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 20, 40, 1)
                    esp.oled.show()
                    error_start = time.ticks_ms()
                    while time.ticks_ms() - error_start < 1500:
                        update_timer()
                    if STRIKE >= STRIKE_LIMIT:
                        break
                    counter = [0, 0, 0, 0]
                    show_strike_info()
                    state = 'light-1'
                    s_time = time.ticks_ms()
    esp.oled.fill(0)
    esp.oled.show()

# Weighted random selection helper
def weighted_random_choice(games, weights):
    """Select a game based on weights using random.choice()."""
    weighted_list = []
    for game, weight in zip(games, weights):
        weighted_list.extend([game] * weight)
    return random.choice(weighted_list)

# Function to wait for both players to press their switches
def wait_for_start():
    global GAME_START
    GAME_START = False

    if esp.board_id == 1:
        other_player = 2
    elif esp.board_id == 2:
        other_player = 1

    while not GAME_START:
        local_ready = joy.read()[2] or not esp.sw.value()
        mqtt.publish(TOPIC_SWITCH, b"1" if local_ready else b"0")
        esp.oled.fill(0)
        esp.oled.rect(10, 10, 108, 20, 1)
        if local_ready:
            esp.oled.text("Ready.", 40, 15)
            esp.oled.text(f"Waiting for", 10, 40)
            esp.oled.text(f"Player {other_player}.", 10, 55)
        else:
            esp.oled.text("Not Ready.", 30, 15)
            esp.oled.text(f"Press switch", 10, 40)
            esp.oled.text(f"to start.", 10, 55)
        esp.oled.show()
        mqtt.check_msg()
        time.sleep(1)
    
    secret_code = random.randint(1234,9999)
    mqtt.publish(TOPIC_SECRET_CODE, b"{secret_code}")
    for countdown in range(3, 0, -1):
        esp.oled.fill(0)
        display_center(str(countdown), 20)
        display_center(str(secret_code), 30)
        esp.oled.show()
        time.sleep(1)

# Normal mode: weighted random selection of games
def play_normal(games):
    global TIME, STRIKE
    wait_for_start()
    
    # Define weights based on board_id
    if esp.board_id == 1:
        weights = [25, 20, 25, 30]  # Adjust these to control frequency
        num_games = 7
    elif esp.board_id == 2:
        weights = [20, 15, 25, 25, 15]  # Lower weights for longer games
        num_games = 5
    
    # Select games with weights
    random_games = [weighted_random_choice(games, weights) for _ in range(num_games)]
    
    for game in random_games:
        game[1]()  # Run the game function
        update_timer()
        if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
            break
    
    if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
        TIME = 0
        update_timer()

# Manual mode: select games manually (unchanged)
def play_manual(games):
    """Display a menu to select and play games."""
    global TIME, STRIKE
    selected = 0
    while TIME > 0 and STRIKE < STRIKE_LIMIT:
        esp.oled.fill(0)
        for i, (name, _) in enumerate(games):
            if i == selected:
                esp.oled.text(f"> {name}", 10, 10 + i * 10, 1)
            else:
                esp.oled.text(f"  {name}", 10, 10 + i * 10, 1)
        esp.oled.show()
        joy_dir = joy.direction()
        time.sleep(0.1)
        if 'Up' in joy_dir:
            selected = (selected - 1) % len(games)
        elif 'Down' in joy_dir:
            selected = (selected + 1) % len(games)
        elif joy.read()[2] or esp.sw.value() == 0:
            esp.oled.fill(0)
            esp.oled.show()
            games[selected][1]()
            time.sleep(1)
        update_timer()
    
    if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
        TIME = 0
        update_timer()

# Demo mode: fixed random games with a seed
def play_demo(games):
    global TIME, STRIKE
    wait_for_start()
    random.seed(42)  # Fixed seed for predictable randomness
    
    demo_games = games[:4]  # Adjust this as needed
    
    for game in demo_games:
        game[1]()  # Run the game function
        update_timer()
        if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
            break
    
    if TIME <= 0 or STRIKE >= STRIKE_LIMIT:
        TIME = 0
        update_timer()

# Run the program
if __name__ == "__main__":
    
    wifi = network.WLAN(network.STA_IF)
    mqtt = MQTTClient(client_id='',
                      server=MQTT_BROKER,
                      user=MQTT_USER,
                      password=MQTT_PASS)
    connect_wifi()
    connect_mqtt()
    
    board_games = {
        1: [
            ("Maze", play_maze)
        ],
        2: [
            ("LED Memorizing", play_led_memorizing),
            ("LED Seq Eiei", play_led_seq_eiei)
        ],
    }

    games = [
        ("The Button", play_thebutton),
        ("Morse Code", play_morse_code),
        ("LED Sequence", play_led_sequence)
    ]
    
    games.extend(board_games[esp.board_id])
    
    random.seed(seed)
    if game_mode == 'normal':
        play_normal(games)
    elif game_mode == 'manual':
        play_manual(games)
    elif game_mode == 'demo':
        play_demo(games)
    else:
        play_normal(games)

esp.oled.fill(0)
if TIME > 0:
    esp.oled.text(f"Congratulations!", 0, 0, 1)
else:
    esp.oled.text(f"Game over.", 0, 0, 1)
    
esp.oled.text(f"Time Left: {TIME//60:02}:{TIME%60:02.0f}", 0, 15, 1)
esp.oled.text(f"Strikes: {STRIKE}/{STRIKE_LIMIT}", 0, 30, 1)
esp.oled.text(f"Further details", 0, 45, 1)
esp.oled.text(f"on Dashboard.", 0, 55, 1)
esp.oled.show()



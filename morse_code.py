from machine import Pin, I2C, PWM, ADC
import ssd1306, time, esp32_s3
import array

esp = esp32_s3.ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
sw2 = Pin(15, Pin.IN, Pin.PULL_UP)

morse_dict = {
    'a': '.-',
    'b': '-...',
    'c': '-.-.',
    'd': '-..',
    'e': '.',
    'f': '..-.',
    'g': '--.',
    'h': '....',
    'i': '..',
    'j': '.---',
    'k': '-.-',
    'l': '.-..',
    'm': '--',
    'n': '-.',
    'o': '---',
    'p': '.--.',
    'q': '--.-',
    'r': '.-.',
    's': '...',
    't': '-',
    'u': '..-',
    'v': '...-',
    'w': '.--',
    'x': '-..-',
    'y': '-.--',
    'z': '--..',
}

word_dict = {
    'bombs': 38.07,
    'node': 38.17,
    'else': 38.32,
    'board': 38.59,
    'enum': 38.69,
    'unit': 38.76,
    'next': 38.80,
    'unix': 38.84
}
word_list = list(word_dict.keys())
freq_list = list(word_dict.values())
sorted_freq_list = sorted(word_dict.values())

is_solved = False

option = 3
i = 3

while not is_solved:
#     print(word_list[option])
#     for letter in word_list[option]:
#         for symbol in morse_dict[letter]:
#             
#             if symbol == '.':
#                 print(".", end=" ")
#                 esp.yellow(512)
#                 time.sleep(0.3)
#             
#             elif symbol == '-':
#                 print("-", end=" ")
#                 esp.yellow(512)
#                 time.sleep(1)
#                 
#             esp.clearled()
#             time.sleep(0.45)
#                   
#         time.sleep(1)
#         print("\n")
#     time.sleep(3)
#     
#     print("\n")
    
    select_freq = sorted_freq_list[i]
    esp.oled.fill(0)
    
    esp.oled.rect(5, 3, 120, 15, 1)
    esp.oled.rect(20, 28, 90, 30, 1)
    esp.oled.text(f"{select_freq} MHz", 29, 38, 1)
    
    rect_center = int((select_freq-38)*115)
    esp.oled.fill_rect(rect_center-1, 1, rect_center//16+1, 19, 1)
    
    left_triangle = array.array('i', [13,31,13,51,3,41])
    right_triangle = array.array('i', [115,31,115,51,125,41])

    esp.oled.poly(0, 0, left_triangle, 1)
    esp.oled.poly(0, 0, right_triangle, 1)
    
    if sw2.value() == 0:
        if i > 0:
            i -= 1
        esp.oled.poly(0, 0, left_triangle, 1, 1)
        
    if esp.sw.value() == 0:
        if i < len(freq_list)-1:
            i += 1
        esp.oled.poly(0, 0, right_triangle, 1, 1)
    
    esp.oled.show()
    time.sleep(0.1)




            

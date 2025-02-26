import time

import ssd1306
from machine import ADC, Pin

class Joystick:
    def __init__(self, x_pin, y_pin, s_pin):
        self.joystick_x = ADC(Pin(4))  # X-axis
        self.joystick_y = ADC(Pin(5))  # Y-axis
        self.button = Pin(6, Pin.IN, Pin.PULL_UP)  # Button (active LOW)

        self.joystick_x.atten(ADC.ATTN_11DB)
        self.joystick_y.atten(ADC.ATTN_11DB)
    
    def get_value(self):
        return [self.joystick_x.read(), self.joystick_y.read(), self.button.value()]
    
    def check_direction(self, x, y):
        # mean (3010, 3060)
        self.mid_x = 3010
        self.mid_y = 3060
        dx = x - self.mid_y
        dy = y - self.mid_y
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
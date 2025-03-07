import time

import ssd1306
from machine import ADC, Pin

class Joystick:
    def __init__(self, x_pin=16, y_pin=17, s_pin=15):
        self.joystick_x = ADC(Pin(x_pin))  # X-axis
        self.joystick_y = ADC(Pin(y_pin))  # Y-axis
        self.button = Pin(s_pin, Pin.IN, Pin.PULL_UP)  # Button (active LOW)

        self.joystick_x.atten(ADC.ATTN_11DB)
        self.joystick_y.atten(ADC.ATTN_11DB)
    
    def get_value(self):
        return [self.joystick_x.read(), self.joystick_y.read(), self.button.value()]
    
    def check_direction(self, x_val, y_val, center=2000, deadzone=350):
        # mean (3010, 3060)
        if x_val < center - deadzone:
            x_dir = -1
        elif x_val > center + deadzone:
            x_dir = +1
        else:
            x_dir = 0

        if y_val < center - deadzone:
            y_dir = -1
        elif y_val > center + deadzone:
            y_dir = +1
        else:
            y_dir = 0
            
        if x_dir<0:
            xx = "Right"
        else:
            if(x_dir>0):
                xx = "Left"
            else:
                xx = "CenterX"
            
        if y_dir<0:
            yy = "Down"
        else:
            if(y_dir>0):
                yy = "Up"
            else:
                yy = "CenterY"
        
        return [xx, yy]

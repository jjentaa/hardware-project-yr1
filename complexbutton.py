import time

import ssd1306
import tm1638
from machine import ADC, Pin

class ComplexButton:
    def __init__(self, stb_pin, clk_pin, dio_pin):
        self.tm = tm1638.TM1638(stb=Pin(stb_pin), clk=Pin(clk_pin), dio=Pin(dio_pin))
        self.tm.power(1)
        self.tm.brightness(7)

    def get_switch_value(self):
        return f"{self.tm.qyf_keys():016b}"

    def check_pressed_switch(self):
        state = f"{self.tm.qyf_keys():016b}"    
        
        state_ls = []
        for i in range(16):
            if(state[i]=='1'): state_ls.append(True)
            else: state_ls.append(False)

        return state_ls
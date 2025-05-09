import time
import tm1638
from machine import ADC, Pin

class ComplexButton:
    def __init__(self, stb_pin=10, clk_pin=12, dio_pin=11):
        self.tm = tm1638.TM1638(stb=Pin(stb_pin), clk=Pin(clk_pin), dio=Pin(dio_pin))
        self.tm.power(1)
        self.tm.brightness(7)
        self.tm.clear()

    def get_switch_value(self):
        return f"{self.tm.qyf_keys():016b}"
    
    def get_reverse(self):
        sw_value = self.get_switch_value()
        
        reverse = ''
        for i in range(len(sw_value), 0, -1):
            reverse += sw_value[i-1]
        
        return reverse
    
    def get_xy(self):
        reverse = self.get_reverse()
        
        for i in range(len(reverse)):
            if reverse[i] == '1':
                return (i%4, i//4)

    def check_pressed_switch(self):
        state = f"{self.tm.qyf_keys():016b}"    
        
        state_ls = []
        for i in range(16):
            if(state[i]=='1'): state_ls.append(True)
            else: state_ls.append(False)

        return state_ls

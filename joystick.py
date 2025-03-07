from machine import ADC,Pin
import time

class Joystick:
    
    def __init__(self, x_pin=16, y_pin=17, sw_pin=15, x_invert=False, y_invert=False, sw_invert=True):
        self.x = ADC(Pin(x_pin, Pin.IN))
        self.y = ADC(Pin(y_pin, Pin.IN))
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        self.x_invert = x_invert
        self.y_invert = y_invert
        self.sw_invert = sw_invert
        
        self.x.atten(self.x.ATTN_11DB)
        self.y.atten(self.x.ATTN_11DB)
    
    def raw(self):
        if self.sw_invert:
            return (self.x.read(), self.y.read(), not self.sw.value())
        return (self.x.read(), self.y.read(), self.sw.value())
    
    def mod_xy(self, val):
        return round((val - 2047)/ 2048)
    
    def read(self):
        self.xVal, self.yVal, self.swVal = self.raw()
        self.xVal = round((self.xVal - 2047)/ 2048)
        self.yVal = round((self.yVal - 2047)/ 2048)
        
        if self.x_invert:
            self.xVal *= -1
        
        if self.y_invert:
            self.yVal *= -1
        
        return (self.xVal, self.yVal, self.swVal)
    
    def direction(self):
        x_direction = {
            0: 'Center',
            -1: 'Left',
            1: 'Right'
        }
        y_direction = {
            0: 'Center',
            -1: 'Down',
            1: 'Up'
        }
        x, y, sw = self.read()
        return (x_direction[x], y_direction[y])

import time

import ssd1306
from machine import ADC, Pin

class FourButton:
    def __init__(self, adc_pin1, adc_pin2, adc_pin3, adc_pin4):
        self.button1 = Pin(adc_pin1, Pin.IN, Pin.PULL_UP) # red
        self.button2 = Pin(adc_pin2, Pin.IN, Pin.PULL_UP) # yellow
        self.button3 = Pin(adc_pin3, Pin.IN, Pin.PULL_UP) # green
        self.button4 = Pin(adc_pin4, Pin.IN, Pin.PULL_UP) # blue

    def check_press(self):
        state = []
        start_time = time.time()
        counter = 0
        
        while(counter<20):
            # record state every 0.1 second
            if(time.time()-start_time>(counter+1)):
                state.append([self.button1.value(), self.button2.value(), self.button3.value(), self.button4.value()])
                counter+=1

        checked = [False, False, False, False]
        for j in range(len(state)):
            checked = [state[j][i] or checked[i] for i in range(4)]
        
        return checked
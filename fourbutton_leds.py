import time
from machine import Pin, I2C, PWM, ADC

class FourButton:
    def __init__(self, pin1, pin2, pin3, pin4):
        self.button1 = Pin(pin1, Pin.IN, Pin.PULL_UP)  # red
        self.button2 = Pin(pin2, Pin.IN, Pin.PULL_UP)  # yellow
        self.button3 = Pin(pin3, Pin.IN, Pin.PULL_UP)  # green
        self.button4 = Pin(pin4, Pin.IN, Pin.PULL_UP)  # blue
        
        self.last_state = [1, 1, 1, 1]
    
    def read(self):
        states = [self.button1.value(), self.button2.value(), self.button3.value(), self.button4.value()]
        results = [False, False, False, False]
        
        for i in range(4):
            if states[i] == 0 and self.last_state[i] == 1:
                results[i] = True
                    
            self.last_state[i] = states[i]
        
        return results

class FourLeds:
    def __init__(self, r=9, y=10, g=45, b=21, PWM_FREQ=5000):
        self._r = PWM(Pin(r))
        self._y = PWM(Pin(y))
        self._g = PWM(Pin(g))
        self._b = PWM(Pin(b))

        self._r.init(freq=PWM_FREQ)
        self._y.init(freq=PWM_FREQ)
        self._g.init(freq=PWM_FREQ)
        self._b.init(freq=PWM_FREQ)
        
        self.clear()
    
    def red(self, duty=255):
        self._r.duty(duty)
    
    def yellow(self, duty=255):
        self._y.duty(duty)
        
    def green(self, duty=255):
        self._g.duty(duty)
        
    def blue(self, duty=255):
        self._b.duty(duty)
        
    def clear(self):
        self.red(0)
        self.yellow(0)
        self.green(0)
        self.blue(0)


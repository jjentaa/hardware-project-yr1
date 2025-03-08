from machine import Pin, I2C, PWM, ADC
import ssd1306

class ESP32_S3:
    
    def __init__(self, r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000):
        self._i2c = I2C(0, sda=Pin(sda), scl=Pin(scl))
        self.oled = ssd1306.SSD1306_I2C(128, 64, self._i2c)
        
        self._ldr = ADC(Pin(ldr))
        self._ldr.atten(ADC.ATTN_11DB)
        
        self.sw = Pin(sw, Pin.IN, Pin.PULL_UP)

        self._r = PWM(Pin(r))
        self._y = PWM(Pin(y))
        self._g = PWM(Pin(g))

        self._r.init(freq=PWM_FREQ)
        self._y.init(freq=PWM_FREQ)
        self._g.init(freq=PWM_FREQ)
        
        self.clearled()
    
    def red(self, duty=255):
        self._r.duty(duty)
    
    def yellow(self, duty=255):
        self._y.duty(duty)
        
    def green(self, duty=255):
        self._g.duty(duty)
        
    def clearled(self):
        self.red(0)
        self.yellow(0)
        self.green(0)
        
    def read_ldr(self, invert=True):
        val = self._ldr.read_uv()
        
        max_val = 3126000 # This is from testing
        percent = int(val*100/max_val) # Turn it into range of 0-100
        if invert:
            percent = 100-percent
        
        if percent >= 100:
            percent = 100
        
        if percent <= 0:
            percent = 0
        
        return percent
    
    def raw_ldr(self):
        return self._ldr.read_uv()
    
        
    
        

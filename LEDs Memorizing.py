import random
import time

from machine import Pin, I2C, PWM, ADC
import ssd1306

class ESP32_S3:
    
    def __init__(self, r=42, y=41, g=40,b=0, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000):
        self._i2c = I2C(0, sda=Pin(sda), scl=Pin(scl))
        self.oled = ssd1306.SSD1306_I2C(128, 64, self._i2c)
        
        self._ldr = ADC(Pin(ldr))
        self._ldr.atten(ADC.ATTN_11DB)
        
        self.sw = Pin(sw, Pin.IN, Pin.PULL_UP)

        self._r = PWM(Pin(r))
        self._y = PWM(Pin(y))
        self._g = PWM(Pin(g))
        self._b = PWM(Pin(b))

        self._r.init(freq=PWM_FREQ)
        self._y.init(freq=PWM_FREQ)
        self._g.init(freq=PWM_FREQ)
        self._b.init(freq=PWM_FREQ)
        
        self.clearled()
    
    def red(self, duty=255):
        self._r.duty(duty)
    
    def yellow(self, duty=255):
        self._y.duty(duty)
        
    def green(self, duty=255):
        self._g.duty(duty)
        
    def blue(self, duty=255):
        self._b.duty(duty)
        
        
    def clearled(self):
        self.red(0)
        self.yellow(0)
        self.green(0)
        self.blue(0)
        
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

######Test phase########

esp = ESP32_S3(r=9, y=10, g=45, b=21, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
esp.clearled()
FB= FourButton(15, 16, 17, 18)
Buzz = Buzzer(4,inverse=False, freq=440, vol=0)
ledlist=['r','g','y','b']
winstreak = 0 
round = 0
listkey =[]
while True:
    esp.oled.rect(1, 1, 127, 63, 1)
    esp.oled.show()
    countkey=0
    round+=1
    checkkey =0
    esp.oled.text('round', 5, 5, 1) 
    esp.oled.text(str(round), 60, 5, 1)
    esp.oled.show()
    listkey=[]
    answerkey=[]
    answerstr = ''
    for i in range(round+3):
        time.sleep(1.5/(i+1))
        light = random.choice(ledlist)
        if light == 'r' :
            esp.red()
            time.sleep(1.5/(i+1))
            esp.clearled()
            listkey.append('r')
        elif light == 'g' :
            esp.green()
            time.sleep(1.5/(i+1))
            esp.clearled()
            listkey.append('g')
        elif light == 'y' :
            esp.yellow()
            time.sleep(1.5/(i+1))
            esp.clearled()
            listkey.append('y')
        elif light == 'b' :
            esp.blue()
            time.sleep(1.5/(i+1))
            esp.clearled()
            listkey.append('b')
    print(listkey) #testcase
    for j in listkey:
        checkkey+=1
        esp.oled.text(str(countkey), 105, 5, 1)
        esp.oled.text('/', 110, 5, 1)
        esp.oled.text(str(round+3), 115, 5, 1)
        esp.oled.text('Pass:',2,30,1)
        esp.oled.show()
        print(countkey)
        while checkkey>countkey:
            while FB.button1.value()== False:
                esp.oled.text(str(answerstr), 41, 30, 0)
                answerkey.append('r')
                answerstr = ''.join(answerkey)
                esp.oled.text(str(countkey), 105, 5, 0)
                countkey+=1
                esp.oled.text(str(countkey), 105, 5, 1)
                esp.oled.text(str(answerstr), 41, 30, 1)
                time.sleep(0.2)
                while FB.button1.value()==False or FB.button2.value()==False or FB.button3.value()==False or FB.button4.value()== False:
                    time.sleep(0.2)
                    pass
                else:
                    break
            while FB.button2.value()== False:
                esp.oled.text(str(answerstr), 41, 30, 0)
                answerkey.append('y')
                answerstr = ''.join(answerkey)
                esp.oled.text(str(countkey), 105, 5, 0)
                countkey+=1
                esp.oled.text(str(countkey), 105, 5, 1)
                esp.oled.text(str(answerstr), 41, 30, 1)
                time.sleep(0.2)
                while FB.button1.value()==False or FB.button2.value()==False or FB.button3.value()==False or FB.button4.value()== False:
                    time.sleep(0.2)
                    pass
                else:
                    break
            while FB.button3.value()== False:
                esp.oled.text(str(answerstr), 41, 30, 0)
                answerkey.append('g')
                answerstr = ''.join(answerkey)
                esp.oled.text(str(countkey), 105, 5, 0)
                countkey+=1
                esp.oled.text(str(countkey), 105, 5, 1)
                esp.oled.text(str(answerstr), 41, 30, 1)
                time.sleep(0.2)
                while FB.button1.value()==False or FB.button2.value()==False or FB.button3.value()==False or FB.button4.value()== False:
                    time.sleep(0.2)
                    pass
                else:
                    break
            while FB.button4.value()== False:
                esp.oled.text(str(answerstr), 41, 30, 0)
                answerkey.append('b')
                answerstr = ''.join(answerkey)
                esp.oled.text(str(countkey), 105, 5, 0)
                countkey+=1
                esp.oled.text(str(countkey), 105, 5, 1)
                esp.oled.text(str(answerstr), 41, 30, 1)
                time.sleep(0.2)
                while FB.button1.value()==False or FB.button2.value()==False or FB.button3.value()==False or FB.button4.value()== False:
                    time.sleep(0.2)
                    pass
                else:
                    break
    if round==6 and answerkey == listkey:
        break
    if answerkey == listkey:
        esp.oled.text('Correct!', 35, 50, 1)
        esp.oled.show()
    else:
        round=0
        esp.oled.text('Wrong!', 36, 50, 1)
        esp.oled.show()
    time.sleep(3)
    esp.oled.fill(0)
    esp.oled.show()
esp.oled.fill(0)
esp.oled.text('You Pass', 50, 30, 1)
while True:
    for i in range(10):
        esp.oled.scroll(-i, 0)
        esp.oled.show()
        time.sleep(0.1)
    for i in range(10):
        esp.oled.scroll(i, 0)
        esp.oled.show()
        time.sleep(0.1)

#'''

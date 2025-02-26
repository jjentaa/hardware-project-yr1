from machine import Pin, PWM

tones = {
    'c': 262,
    'c#': 277,
    'd': 294,
    'd#': 311,
    'e': 330,
    'f': 349,
    'f#': 370,
    'g': 392,
    'g#': 415,
    'a': 440,
    'a#': 466,
    'b': 494,
    'C': 523,
    'C#': 554,
    'D': 587,
    'D#': 622,
    'E': 659,
    'F': 698,
    'F#': 734,
    'G': 784,
    'G#': 831,
    'A': 880,
    'A#': 932,
    'B': 988,
    'x': 0,
    ' ': 0
}

class Buzzer:
    
    def __init__(self, pin, inverse=False, freq=440, vol=0):
        self.pin = pin
        self.inverse = inverse
        self.freq = freq
        self.vol_to_duty(vol)
        
        self.pwm = PWM(Pin(self.pin, Pin.OUT), freq=self.freq, duty=self.duty)
        
    def vol_to_duty(self, vol):
        self.vol = vol
        self.duty = int(vol*10.23)
        if self.inverse:
            self.duty = 1023 - self.duty
    
    def play(self, freq=2637, vol=20):
        self.vol_to_duty(vol)
        
        if freq in tones:
            self.freq = tones[freq]
        else:
            try:
                self.freq = int(freq)
            except:
                raise ValueError('Notes must be integer or in-between c-B')
        
        self.pwm.duty(self.duty)
        self.pwm.freq(self.freq)
    
    def stop(self):
        self.duty = 0
        self.pwm.duty(self.duty)
    
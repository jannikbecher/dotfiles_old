from machine import Pin
from neopixel import NeoPixel
from math import ceil, floor

class Display():
    LED_OFF = (0, 0, 0)
    LED_GREEN = (0, 204, 0)
    LED_YELLOW = (255, 255, 51)
    LED_RED = (255, 0, 0)
    LED_BLUE = (123, 104, 238)

    def __init__(self, pin_l, pin_r, num_leds):
        self.pin_l = Pin(pin_l, Pin.OUT)
        self.pin_r = Pin(pin_r, Pin.OUT)
        self.num_leds = num_leds
        self.np_l = NeoPixel(self.pin_l, self.num_leds)
        self.np_r = NeoPixel(self.pin_r, self.num_leds)
        self.prev_num_leds = 0

    def display_percent(self, percent, color):
        if percent > 1: percent = 1
        if percent < 0: percent = 0
        active_leds = floor(percent*self.num_leds)
        for i in range(self.num_leds):
            if i < active_leds:
                self.np_l[self.num_leds-1-i] = color
                self.np_r[self.num_leds-1-i] = color
            else:
                self.np_l[self.num_leds-1-i] = self.LED_OFF
                self.np_r[self.num_leds-1-i] = self.LED_OFF
        self.np_l.write()
        self.np_r.write()

    def display_values(self, percent):
        color = (0, 0, 0)
        if percent < 0.33:
            color = self.LED_GREEN
        elif percent < 0.67:
            color = self.LED_YELLOW
        else:
            color = self.LED_RED
        self.display_percent(percent, color)

    def display_config(self, percent):
        self.display_percent(percent, self.LED_BLUE)

    def display_pulse(self, brightness):
        self.display_all(self.set_brightness(self.LED_RED, brightness*100))

    def display_all(self, color):
        for i in range(self.num_leds):
            self.np_l[i] = color
            self.np_r[i] = color
        self.np_l.write()
        self.np_r.write()

    def display_none(self):
        for i in range(self.num_leds):
            self.np_l[i] = self.LED_OFF
            self.np_r[i] = self.LED_OFF
        self.np_l.write()
        self.np_r.write()

    def set_brightness(self, color, percent):
        hsv = rgb_to_hsv(color)
        hsv = (hsv[0], hsv[1], percent)
        return hsv_to_rgb(hsv)

def rgb_to_hsv(rgb):
    r,g,b = rgb
    r = r/255
    g = g/255
    b = b/255
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return (0.0, 0.0, v*100)
    s = (maxc-minc) / maxc
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return (h*360, s*100, v*100)

def hsv_to_rgb(hsv):
    h,s,v = hsv
    h = h/360
    s = s/100
    v = v/100
    if s == 0.0:
        return (int(255*v), int(255*v), int(255*v))
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return (int(255*v), int(255*t), int(255*p))
    if i == 1:
        return (int(255*q), int(255*v), int(255*p))
    if i == 2:
        return (int(255*p), int(255*v), int(255*t))
    if i == 3:
        return (int(255*p), int(255*q), int(255*v))
    if i == 4:
        return (int(255*t), int(255*p), int(255*v))
    if i == 5:
        return (int(255*v), int(255*p), int(255*q))

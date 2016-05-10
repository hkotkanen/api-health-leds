from bibliopixel.led import *
from bibliopixel.animation import StripChannelTest
from bibliopixel.animation import BaseStripAnim
from bibliopixel.drivers.LPD8806 import *
import random
import datetime

driver = DriverLPD8806(104, use_py_spi=True, c_order=ChannelOrder.GRB)
led = LEDStrip(driver)

# for i in range(0,103):
#    for col in range(0, 255, 5):
#        led.set(i, (col, 0, 0))
#        led.update()
#

class Auroraborealis(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        # The base class MUST be initialized by calling super like this
        super(Auroraborealis, self).__init__(led, start, end)
        self.hl = 0
        for i in range(self._led.numLEDs):
            self._led.set(i, (0, 100, 100))

    def step(self, amt=1):
        # Fill the strip, with each sucessive color
        sec = datetime.datetime.now().second
        for i in range(self._led.numLEDs):
            if abs(self.hl - i) < 15:
                mi, ma = -2, 58
            else:
                mi, ma = -7, 3
            c = list(self._led.get(i))
            if c[1] < 100 or c[1] > 190: 
                c[1] = 100
            c[1] += random.randint(mi, ma)
            if c[2] < 50 or c[2] > 140: 
                c[2] = 100
            c[2] += random.randint(mi, ma)
            # print i, mi, ma, c
            self._led.set(i, c)
        # Increment the internal step by the given amount
        self.hl += 1
        if self.hl > self._led.numLEDs:
            self.hl = 0
        self._step += amt

#anim = Auroraborealis(led)
#anim.run(fps=10)

class StripTest(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        # The base class MUST be initialized by calling super like this
        super(StripTest, self).__init__(led, start, end)
        # Create a color array to use in the animation
        self._colors = [colors.Red, colors.Orange, colors.Yellow, colors.Green, colors.Blue, colors.Indigo]

    def step(self, amt=1):
        #for i in range(self._led.numLEDs):
        #    self._led.set(i, colors.Off)
        #return

        # Fill the strip, with each sucessive color
        for i in range(self._led.numLEDs):
            self._led.set(i, self._colors[(self._step + i) % len(self._colors)])
        # Increment the internal step by the given amount
        self._step += amt

anim = StripTest(led)
anim.run(fps=8)

import time
import numpy as np
class BlinkOnCommandTest(BaseStripAnim):
    def __init__(self, led, start=0, end=-1):
        # The base class MUST be initialized by calling super like this
        super(BlinkOnCommandTest, self).__init__(led, start, end)
        # Create a color array to use in the animation
        #self._colors = [colors.Red, colors.Orange, colors.Yellow, colors.Green, colors.Blue, colors.Indigo]
        self._last_blinked_ts = np.zeros(self._led.numLEDs) + time.time()
        print self._last_blinked_ts

    def step(self, amt=1):
        for i in range(self._led.numLEDs):
            if (time.time() - self._last_blinked_ts[i]) > 1:
                print time.time() - self._last_blinked_ts[i]
                self._led.set(i, colors.Off)
            else:
                self._led.set(i, colors.Green)

            if random.random() > 0.99:
                print 'set last as current!'
                self._last_blinked_ts[i] = time.time()            
        return

        # Fill the strip, with each sucessive color
        #for i in range(self._led.numLEDs):
        #    self._led.set(i, self._colors[(self._step + i) % len(self._colors)])
        # Increment the internal step by the given amount
        #self._step += amt

#anim = BlinkOnCommandTest(led)
#anim.run(fps=5)

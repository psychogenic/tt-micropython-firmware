'''
Created on Jan 22, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

import logging 
log = logging.getLogger(__name__)

class Pin:
    '''
        Stub class for desktop testing,
        i.e. where machine module DNE
    '''
    OUT = 1
    IN = 2
    IRQ_FALLING = 3
    IRQ_RISING = 4
    PULL_DOWN = 5
    PULL_UP = 6
    OPEN_DRAIN = 7
    def __init__(self, gpio:int, direction:int=0, mode:int=0, pull:int=0):
        self.gpio = gpio
        self.dir = direction
        self.val = 0 
        
    def value(self, setTo:int = None):
        if setTo is not None:
            log.debug(f'Setting GPIO {self.gpio} to {setTo}')
            self.val = setTo 
        return self.val
        
    def init(self, direction:int, pull:int=None):
        log.debug(f'Setting GPIO {self.gpio} to direction {direction}')
        self.dir = direction
        
    def toggle(self):
        if self.val:
            self.val = 0
        else:
            self.val = 1

    def __call__(self, value:int=None):
        if value is not None:
            self.val = value
            return
        return self.val
    
class ADC:
    CORE_TEMP = -1
    def __init__(self, pin):
        self._pin = pin 
        
    def read_u16(self):
        return 0xdead
    
class Timer:
    def __init__(self):
        self._freq = 0
        self._period = 0
        self._mode = 0
        self.callback = None 
    
    def init(self, period:int, mode:int, callback):
        self._period = period 
        self._mode = mode 
        self.callback = callback 
        
    def deinit(self):
        self.callback = None
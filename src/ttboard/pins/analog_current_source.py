'''
Created on Aug 5, 2026

@author: Pat Deegan
@copyright: Copyright (C) 2026 Pat Deegan, https://psychogenic.com
'''

from ttboard.pins.upython import Pin


import ttboard.log as logging
log = logging.getLogger(__name__)

class AnalogCurrentSource:
    '''
        Control for the analog current source.
        Use .enabled attribute to enabled/disable, 
        and .level to set current source level (between 
        0 - 0xffff, higher == more current, up to ~250 uA).
        
        E.g.
        an_cur_src.level = 40000
        # ...
        an_cur_src.enabled = False
        
        # ... later
        an_cur_src.enabled = True # returns to last level set
    '''
    
    def __init__(self, src_ctrl_pin:Pin, db):
        self._src_ctrl_pin = src_ctrl_pin
        self._parent_demoboard = db
        self._pwm = None 
        self._enabled = False 
        self._level = 10
        self.frequencyHz = 1_000_000
        self.enable = False
        
    @property 
    def enabled(self):
        return self._enabled
    
    @enabled.setter 
    def enabled(self, activate:bool):
        self._enabled = True if activate else False
        if activate:
            if self._pwm:
                self._pwm.duty_u16(0xffff - self._level)
            else:
                self._pwm = self._src_ctrl_pin.pwm(self.frequencyHz, 0xffff - self._level)
            
        else:
            if self._pwm:
                self._pwm.deinit()
                self._pwm = None 
            
            self._src_ctrl_pin(1)
            
    @property 
    def level(self):
        return self._level
    
    @level.setter 
    def level(self, u16_level:int):
        try:
            self._level = int(u16_level)
        except ValueError:
            log.error("Level must be int between 0 - 0xffff")
        if u16_level < 1:
            self.enabled = False
        else:
            if self.enabled:
                self._pwm.duty_u16(0xffff - u16_level)
            else:
                self.enable = True 
                
    def __repr__(self):
        enstr = 'disabled'
        if self._enabled:
            enstr = 'enabled'
        
        return f'<AnalogCurrentSource {enstr} {self._level}>'
                
        
                
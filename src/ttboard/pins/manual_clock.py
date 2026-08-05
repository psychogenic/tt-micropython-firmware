'''
Created on Aug 5, 2026

@author: Pat Deegan
@copyright: Copyright (C) 2026 Pat Deegan, https://psychogenic.com
'''

from ttboard.pins.upython import Pin
from machine import Timer

import ttboard.log as logging
log = logging.getLogger(__name__)

def manclkc_irq_handler(pin):
    ManualClockPin.pin_activated = True
    
class ManualClockPin:
    '''
        In DB v3.3 and on, the manual clocking pin
        is moved off of the actual ASIC clock line
        and instead monitored by the RP2 for activity.
        
        By default, this pin will trigger an interrupt to
        set a flag, that flag is checked by a timer (at 3Hz) 
        and on being triggered does a clock_project_once() 
        through the DB.
        
        To disable this function,
         tt.manual_project_clock.monitoring = False
        will disable the timer
        
        The state of the pin may be checked through the demoboard 
        using
            tt.manual_project_clock()
        or
            tt.manual_project_clock.value()
            
    '''
    
    
    pin_activated = False
    
    def __init__(self, clk_pin:Pin, db):
        self._clk_pin = clk_pin
        self._parent_demoboard = db
        self._timer = None
        self._monitoring = False
        self.timerperiodms = 333
        clk_pin.irq(trigger=Pin.IRQ_RISING, handler=manclkc_irq_handler)
        
        
    @property
    def monitoring(self):
        return self._monitoring 
    
    @monitoring.setter
    def monitoring(self, set_to:bool):
        if set_to:
            if self._monitoring or self._timer is not None:
                return 
            
            log.info("Enabling manual clock pin monitoring")
            self._monitoring = True 
            self._timer = Timer()
            self._timer.init(period=self.timerperiodms, mode=Timer.PERIODIC, 
                             callback=self._timer_callback)
        else:
            if not self._monitoring:
                return 
            log.info("Disabling manual clock pin monitoring")
            if self._timer is not None:
                self._timer.deinit() 
                self._timer = None 
                self._monitoring = False
                
            
    def _timer_callback(self, _timer):
        if ManualClockPin.pin_activated:
            ManualClockPin.pin_activated = False 
            # print(f"CLOCKING {self._parent_demoboard}")
            self._parent_demoboard.clock_project_once()
            

    def value(self, value:int=None):
        if value is not None:
            raise ValueError("Don't drive the manual clock!")
            return
        return self._clk_pin()
    
    def __call__(self, value:int=None):
        return self.value(value)

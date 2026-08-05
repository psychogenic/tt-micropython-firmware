'''
Created on Aug 5, 2026

@author: Pat Deegan
@copyright: Copyright (C) 2026 Pat Deegan, https://psychogenic.com
'''

from ttboard.pins.upython import Pin, ADC

import ttboard.log as logging
log = logging.getLogger(__name__)

class ADCPin:
    def __init__(self, p:Pin):
        self._pin = p 
        if hasattr(p, 'raw_pin'):
            self._adc = ADC(p.raw_pin)
        else:
            self._adc = ADC(p)
        
    def read_u16(self):
        return self._adc.read_u16()
    
    @property
    def value(self):
        return self._adc.read_u16()
    
    @property 
    def volts(self):
        return self.value * 3.3 / 0xffff
    
    def __repr__(self):
        return f'<ADC {self._adc} {self.value}>'

class ADCPinList:
    def __init__(self, parent_db):
        self._parent_demoboard = parent_db 
        self._adcpins = [None]*6
        
        
    @property 
    def core_temp(self):
        return 27 - (self[0].volts - 0.706) / 0.001721
    
        
    def __getitem__(self, key):
        try:
            k = int(key)
        except ValueError:
            log.error("Key must be value between 1-5")
            return 
        
        if k < 0 or k > 5:
            log.error("Key must be value between 1-5")
            return 
        
        if self._adcpins[k] is None:
            name = f'adc{k}'
            if hasattr(self._parent_demoboard.pins, name):
                p = getattr(self._parent_demoboard.pins, name)
                self._adcpins[k] = ADCPin(p)
            elif k == 0:
                self._adcpins[k] = ADCPin(ADC.CORE_TEMP)
            else:
                log.error(f"Dunno how to handle ADC {k}?")
            
        return self._adcpins[k]
    
    def __repr__(self):
        return '<ADCPins [1-5]>'
            

    
        
        
        
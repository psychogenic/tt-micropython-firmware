'''
Created on Aug 30, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''
import ttboard.util.platform as platform
from ttboard.pins.upython import Pin
import ttboard.pins.gpio_map
from ttboard.pins.gpio_map import GPIOMapSPASIC

import ttboard.log as logging
log = logging.getLogger(__name__)

class DemoboardVersion:
    '''
        Simple wrapper for an 'enum' type deal with db versions.
        Supported are TT04/TT05 and TT06+
    '''
    UNKNOWN = 0
    TT04 = 1
    TT06 = 2
    
    @classmethod 
    def to_string(cls, v:int):
        asStr = {
            cls.UNKNOWN: 'UNKNOWN',
            cls.TT04: 'TT04/TT05',
            cls.TT06: 'TT06+'
        }
        if v in asStr:
            return asStr[v]
        return 'N/A'

class DemoboardDetect:
    '''
        DemoboardDetect
        centralizes and implements strategies for detecting
        the version of the demoboard.
        
        Because the TT demoboards have had disruptive changes in the 
        migration to TT06+ chips, namely in terms of 
        GPIO mapping and the removal of the demoboard MUX,
        and because the presence or absence of a carrier board on the
        db can make a difference, we use a combination of strategies.
        
        TT06+ boards have a mix of pull-up/pull-downs on the ASIC mux
        control lines, which allow detection of both:
          * the fact this is a TT06+ demoboard; and
          * the fact that the carrier is present
        However, this still looks identical to TT04 for a db with 
        no carrier inserted.
        
        TT04 boards have an on-board MUX, so if we play with that, 
        we should have different values showing on the ASIC mux lines.
        If it has no impact (this pin is mapped to project reset, so 
        it shouldn't unless a project is selected--so this is only assured
        to work on powerup)
        
        This class has:
         a probe() method, to encapsulate all the action,
         PCB, CarrierPresent class attribs to hold the results
         
         
    
    '''
    PCB = DemoboardVersion.UNKNOWN
    CarrierPresent = None 
    CarrierVersion = None 
    
    
    @classmethod 
    def PCB_str(cls):
        return DemoboardVersion.to_string(cls.PCB)
    
    @classmethod 
    def probe_pullups(cls):
        log.info('Forcing TT06 DB for spasic')
        cls.PCB = DemoboardVersion.TT06
        cls.CarrierPresent = True
        return True
        

    @classmethod 
    def rp_all_inputs(cls):
        log.debug("Setting all RP GPIO to INPUTS")
        pins = []
        for i in range(29):
            pins.append(platform.pin_as_input(i, Pin.PULL_DOWN))
            
        return pins
        
    @classmethod 
    def probe(cls):
        result = True
        cls._configure_gpiomap()
        return result
    
    @classmethod
    def force_detection(cls, dbversion:int):
        cls.PCB = dbversion 
        cls._configure_gpiomap()
            
    @classmethod 
    def _configure_gpiomap(cls):
        ttboard.pins.gpio_map.GPIOMap = GPIOMapSPASIC
            
        
    
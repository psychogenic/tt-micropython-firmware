'''
Created on Jan 23, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

from ttboard.pins.upython import Pin
class GPIOMapBase:
    
    @classmethod 
    def project_clock(cls):
        raise RuntimeError('not implemented')
    
    @classmethod 
    def project_reset(cls):
        raise RuntimeError('not implemented')
    
    @classmethod 
    def ctrl_increment(cls):
        raise RuntimeError('not implemented')
    
    @classmethod 
    def ctrl_enable(cls):
        raise RuntimeError('not implemented')
    
    @classmethod 
    def ctrl_reset(cls):
        raise RuntimeError('not implemented')
        

    @classmethod 
    def demoboard_uses_mux(cls):
        return False
    
    @classmethod 
    def mux_select(cls):
        raise RuntimeError('not implemented')
    
    @classmethod
    def muxed_pairs(cls):
        raise RuntimeError('not implemented')
        
    @classmethod
    def muxed_pinmode_map(cls, rpmode:int):
        raise RuntimeError('not implemented')
    
    
    @classmethod 
    def always_outputs(cls):
        return [
            # 'nproject_rst',
            # 'rp_projclk', -- don't do this during "safe" operation
            #'ctrl_ena'
        ]
    
    @classmethod
    def default_pull(cls, pin):
        # both of these now go through MUX and 
        # must therefore rely on external/physical
        # pull-ups.  the nProject reset has PU in 
        # switch debounce, cena... may be a problem 
        # (seems it has a pull down on board?)
        #if pin in ["nproject_rst", "ctrl_ena"]:
        #    return Pin.PULL_UP
        return Pin.PULL_DOWN
    
    @classmethod 
    def get_raw_pin(cls, pin:str, direction:int) -> Pin:
        
        pin_ionum = None
        if isinstance(pin, int):
            pin_ionum = pin 
        else:
            pin_name_to_io = cls.all()
            if pin not in pin_name_to_io:
                return None
            pin_ionum = pin_name_to_io[pin]
            
        return Pin(pin_ionum, direction)
    
    
    @classmethod 
    def all_common(cls):
        retDict = {
            "rp_projclk": cls.RP_PROJCLK,
            "ui_in0": cls.UI_IN0,
            "ui_in1": cls.UI_IN1,
            "ui_in2": cls.UI_IN2,
            "ui_in3": cls.UI_IN3,
            "uo_out4": cls.UO_OUT4,
            "uo_out5": cls.UO_OUT5,
            "uo_out6": cls.UO_OUT6,
            "uo_out7": cls.UO_OUT7,
            "ui_in4": cls.UI_IN4,
            "ui_in5": cls.UI_IN5,
            "ui_in6": cls.UI_IN6,
            "ui_in7": cls.UI_IN7,
            "uio0": cls.UIO0,
            "uio1": cls.UIO1,
            "uio2": cls.UIO2,
            "uio3": cls.UIO3,
            "uio4": cls.UIO4,
            "uio5": cls.UIO5,
            "uio6": cls.UIO6,
            "uio7": cls.UIO7,
            "rpio29": cls.RPIO29
        }
        return retDict

class GPIOMapSPASIC(GPIOMapBase):
    RP_PROJCLK = 0
    PROJECT_nRST = 1
    SLV_SDA1 = 2
    SLV_SCL1 = 3
    MUX_SELECT = 4
    UO_OUT0_CTRL_nRST = 5
    UO_OUT1_CTRL_INC = 6
    UO_OUT2_CTRL_ENA = 7
    UO_OUT3 = 8
    UI_IN0 = 9
    UI_IN1 = 10
    UI_IN2 = 11
    UI_IN3 = 12
    UO_OUT4 = 13
    UO_OUT5 = 14
    UO_OUT6 = 15 
    UO_OUT7 = 16
    UI_IN4  = 17
    UI_IN5  = 18
    UI_IN6  = 19
    UI_IN7  = 20
    UIO0 = 21
    UIO1 = 22
    UIO2 = 23
    UIO3 = 24
    UIO4 = 25
    UIO5 = 26
    UIO6 = 27
    UIO7 = 28
    RPIO29 = 29

    @classmethod 
    def project_clock(cls):
        return cls.RP_PROJCLK
    
    @classmethod 
    def project_reset(cls):
        return cls.PROJECT_nRST
    
    
    @classmethod 
    def demoboard_uses_mux(cls):
        return True
    
    @classmethod 
    def mux_select(cls):
        return cls.MUX_SELECT
    
    
    @classmethod 
    def ctrl_increment(cls):
        return cls.UO_OUT1_CTRL_INC
    
    @classmethod 
    def ctrl_enable(cls):
        return cls.UO_OUT2_CTRL_ENA
    
    @classmethod 
    def ctrl_reset(cls):
        return cls.UO_OUT0_CTRL_nRST
    
    @classmethod 
    def always_outputs(cls):
        return [
            'mux_ctrl'
        ]
    @classmethod 
    def all(cls):
        retDict = cls.all_common()

        retDict.update({
            'nprojectrst': cls.PROJECT_nRST,
            # 'mux_ctrl': cls.MUX_SELECT,
            'cinc': cls.ctrl_increment(),
            'cena': cls.ctrl_enable(),
            'ncrst': cls.ctrl_reset(),
            'uo_out0': cls.UO_OUT0_CTRL_nRST,
            'uo_out1': cls.UO_OUT1_CTRL_INC,
            'uo_out2': cls.UO_OUT2_CTRL_ENA,
            'uo_out3': cls.UO_OUT3
        })

        return retDict

GPIOMap = GPIOMapSPASIC

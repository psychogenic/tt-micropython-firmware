#!/usr/bin/env python
'''
    TT SDK v3.0 migration script
    @copyright: (C) 2026 Pat Deegan, https://psychogenic.com
    
    Tries to do lots of the grunt work of migrating code to the new
    cocotb-like SDK.
    
    If you have a script from a few years ago, which does things like:
    
    def set_pc(tt, addr: int):
        tt.input_byte = addr
        tt.uio2.high()  # set_pc
        tt.clock_project_once()
        tt.uio2.low()
        
        
    i.e. using input_byte rather than ui_in etc, then this script will do most of 
    the work of migrating it.
    
    Use --help to see:
    usage: migratev3.py [-h] [--outdir OUTDIR] [--overwrite] infile [infile ...]
    
    SDK v3 migration tool
    
    positional arguments:
      infile           files to migrate
    
    options:
      -h, --help       show this help message and exit
      --outdir OUTDIR  Destination directory for migrated file(s)
      --overwrite      Allow overwriting files when outputting
      
      
    Sample use cases
    
    1) Look at a single file
    ./migratev3.py path/to/file.py
    
    2) Migrate a single file
    ./migratev3.py path/to/file.py > path/to/migrated.py
    
    3) Write out many files
    Specify a directory in which to dump the contents using --outdir
    ./migratev3.py --outdir /tmp/new path/to/*.py path/to/more/*.py
    
    All files will endup under /tmp/new/path/to/... in exact 
    reflection of relative path used, to any depth.
    
    
    ### Migration
    Main changes from the 2.0 SDK are:
    
    * ui_in, uo_out, uio_in/uio_out naming to reflect the actual chips, rather than
      input_byte, output_byte...
      
    * there are *two* names for the bidir pins: uio_in and uio_out (named according to the 
    ASIC's point of view), depending on if you're reading (uio_out) or writing (uio_in)
    
    * bidir_mode is now set through the uio_oe_pico (PICO perspective output-enable)
    
    * using indices on the pins rather than naming, e.g. what used to be a pin called
      uio0 would be e.g. uio_in[0]

'''
import re 
import argparse
import os
import sys

substitutions = [
    # pins.XXX(DIGIT) -> .XXX = DIGIT
    (r'\.pins\.([^\.]+)\(\s*(\d)\s*\)', r'.\g<1> = \g<2>'),
    # .XXX.low() -> .XXX = 0
    (r'\.([^\.]+)\.low\(\s*\)', r'.\g<1> = 0'),
    # .XXX.high() -> .XXX = 1
    (r'\.([^\.]+)\.high\(\s*\)', r'.\g<1> = 1'),
    # .pins.XXX.value() => .XXX
    (r'\.pins\.([^\.]+)\.value(\s*)', r'.\g<1>'),
    # .input_byte = -> .ui_in = 
    (r'\.input_byte\s*=', '.ui_in ='),
    # return/= ...input_byte -> return/= ui_in.value
    (r'(return\s+|=)\s*([\w\.]+)\.input_byte', r'\g<1> \g<2>.ui_in.value'),
    # .input_byte -> .ui_in.value
    (r'\.input_byte', '.ui_in.value'),
    # return/= ...output_byte -> return/= ...uo_out.value
    (r'(return\s+|=)\s*([^\s]+)\.output_byte', r'\g<1> \g<2>.uo_out.value'),
    # .output_byte -> .uo_out.value
    (r'\.output_byte', '.uo_out.value'),
    # order matters
    (r'\.bidir_byte\s*=', '.uio_in ='),
    (r'(return\s+|=)\s*([^\s]+)\.bidir_byte', r'\g<1> \g<2>.uio_out.value'),
    (r'([^\s]+)\.bidir_byte', r'\g<1>.uio_out.value'),
    (r'\.bidir_mode', '.uio_oe_pico[:]'), #
    (r'\.project_nrst', '.rst_n'),
    (r'\.project_clk([^_]+)', r'.clk\g<1>'),
    
]



special_cases = [
    ('individual_pin_attrib', r'\.(in|out|uio)(\d+)'), 
    ('individual_pin_rawaccess', r'\.(in|out|uio)(\d+)\.\w+'),
    ('individual_pin_write', r'\.(in|out|uio)(\d+)\(([^)]+)\)'),
    ('individual_pin_read', r'\.(in|out|uio)(\d+)\((\s*)\)'),
    
]

def outdebug(s:str):
    print(s, file=sys.stderr)

class Replacer:
    def __init__(self):
        self.substitutions = []
        for v in substitutions:
            self.substitutions.append( [re.compile(v[0]), v[1]])
            
        #self.special_cases = []
        for sc in special_cases:
            #spec = [re.compile(sc[1]), sc[2]]
            #self.special_cases.append(spec)
            setattr(self, sc[0], re.compile(sc[1], re.MULTILINE))
            
    def read(self, fpath:str):
        with open(fpath, 'r') as f:
            return ''.join(f.readlines())
        
    def basic_substitutions(self, contents:str):
        for s in self.substitutions:
            contents = s[0].sub(s[1], contents)
        
        return contents
    
    def special_substitutions(self, contents:str):
        
        set_bitmap = {
            'in': 'ui_in',
            'out': 'uo_out',
            'uio': 'uio_in',
            }
            
        # script is accessing raw pin mode stuff
        # in tt.pins... need to do this in 2 steps
        raw_bitmap1 = {
            'in': 'PINRAWIN',
            'out': 'PINRAWOUT',
            'uio': 'PINRAWUIO',
            }
        raw_bitmap2 = {
            'IN': 'ui_in',
            'OUT': 'uo_out',
            'UIO': 'uio',
            }
        read_bitmat = {
            'in': 'ui_in',
            'out': 'uo_out',
            'uio': 'uio_out',
        
        }
        
        seen = dict()
        
        
        
        for p in self.individual_pin_rawaccess.findall(contents):
            subre = r'\.' + f'{p[0]}{p[1]}' + r'\.'
            repl =  f'.pins.{raw_bitmap1[p[0]]}{p[1]}.'
            outdebug(f"PIN RAW '{subre}', '{repl}'")
            contents = re.sub(subre, repl, contents, 0, re.MULTILINE)
        
        for p in self.individual_pin_write.findall(contents):
            subre = r'\.' + f'{p[0]}{p[1]}' + r'\(' + {p[2]} + r'\)'
            repl =  f'.{set_bitmap[p[0]]}[{p[1]}] = {p[2]}'
            outdebug(f"'{subre}', '{repl}'")
            contents = re.sub(subre, repl, contents, 0, re.MULTILINE)
            
        for p in self.individual_pin_read.findall(contents):
            subre = r'\.' + f'{p[0]}{p[1]}' + r'\(' + {p[2]} + r'\)'
            repl =  f'.{read_bitmap[p[0]]}[{p[1]}]'
            outdebug(f"'{subre}', '{repl}'")
            contents = re.sub(subre, repl, contents, 0, re.MULTILINE)
            
        for p in self.individual_pin_attrib.findall(contents):
            subre = r'\.' + f'{p[0]}{p[1]}'
            repl =  f'.{set_bitmap[p[0]]}[{p[1]}]'
            outdebug(f"PINATTR '{subre}', '{repl}'")
            contents = re.sub(subre, repl, contents, 0, re.MULTILINE)
            
        rawpinfixre = re.compile(r'PINRAW(IN|OUT|UIO)', re.MULTILINE)
        for p in rawpinfixre.findall(contents):
            contents = re.sub(r'PINRAW(IN|OUT|UIO)', raw_bitmap2[p], contents, 0, re.MULTILINE)
            
        
        return contents
    
    def migrate(self, contents:str):
        contents = self.basic_substitutions(contents)
        contents = self.special_substitutions(contents)
        return contents
    
    def migrate_file(self, fpath:str):
        c = self.read(fpath)
        return self.migrate(c)

#
#f = r.read('src/examples/tt_um_psychogenic_neptuneproportional/tt_um_psychogenic_neptuneproportional.py')
def getArgsParser():
    parser = argparse.ArgumentParser(description='SDK v2 migration tool')
    
    parser.add_argument('--outdir', required=False, 
                            type=str, 
                            help="Destination directory for migrated file(s)")
    parser.add_argument('--overwrite', required=False, 
                            action='store_true',
                            help="Allow overwriting files when outputting")
    parser.add_argument('infile', nargs='+', help='files to migrate')
    return parser


def mkdir_if_needed(dirpath:str):
    if not os.path.exists(dirpath):
        outdebug(f'Creating directory: {dirpath}')
        os.makedirs(dirpath)
        
def main():
    
    parser = getArgsParser()
    args = parser.parse_args()
    
    
    if not args.outdir:
        if len(args.infile) != 1:
            outdebug("You MUST specify --outdir if more than one file is to be migrated")
            return
    
    rep = Replacer()
    for infile in args.infile:
        if not os.path.exists(infile):
            outdebug(f"Can't find '{infile}'")
            continue
        outdebug(f"Processing '{infile}'")
        contents = rep.migrate_file(infile)
        if not args.outdir:
            print(contents)
        else:
            destpathdir = os.path.join(args.outdir, os.path.dirname(infile))
            mkdir_if_needed(destpathdir)
            fpath = os.path.join(destpathdir, os.path.basename(infile))
            if os.path.exists(fpath) and not args.overwrite:
                outdebug(f"{fpath} exists and NO --overwrite, skip")
            else:
                outdebug(f"Writing {fpath}")
                with open(fpath, 'w') as f:
                    f.write(contents)

main()

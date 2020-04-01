"""
 Wrapper around building stuff using repotool and Yocto
"""

__version__ = "0.0.1"

verbose_flag = False

def set_verbosity(flag):
    global verbose_flag
    print(f"verbose {flag}")
    verbose_flag = flag

def verbose(*args):
    if verbose_flag:
        print("*** " + "".join(map(str,args)))

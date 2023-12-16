#!/usr/bin/python3
import curses
import sys
import os
import shutil
import glob
from platform import system as ossys
WINDOWS = ossys() == "Windows"

if sys.version_info < (3,7):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!! Serious  Error !!!!!!")
    print("!! Python version too old !!")
    print("! Use version 3.7 or newer !")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    input("Press enter to halt -->")
    sys.exit(5)

try:
    import cursesplus       #Late load libraries
except:
    print("You seem to be missing a library. Run pip install cursesplus")
    input("Press enter to halt -->")
    sys.exit(5)

sys.path.append("/usr/lib/lff")
import epprodkey
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

class FileObject:
    def __init__(self,path):
        self.path = path
        self.isdirectory = os.path.isdir(path)
        if not self.isdirectory:
            self.size = os.path.getsize(path)

def parse_size(data: int) -> str:
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000000000:
        result = f"{round(data/1000000000000000,2)} EB"
    elif data > 2000000000000:
        result = f"{round(data/1000000000000,2)} TB"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    if neg:
        result = "-"+result
    return result

def mass_index_with_progress_bar(stdscr,directory) -> list:
    cursesplus.hidecursor()
    total, used, free = shutil.disk_usage(directory)
    p = cursesplus.ProgressBar(stdscr,used+2,cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Enumerating Files")
    p.ydraw = 0
    msize = 0
    corr = 0
    fi = 0
    cursesplus.displaymsgnodelay(stdscr,["Indexing files","Please be patient"])
    p.step()
    errs = 0
    final: list[FileObject] = []
    ackeddevs = []
    for subdir, dirs, files in os.walk(directory):
        try:
            total, used, free = shutil.disk_usage(subdir)
        except:
            errs += 1
            continue
        if os.stat(subdir).st_dev not in ackeddevs:
            p.max += used
            ackeddevs.append(os.stat(subdir).st_dev)
        p.msg = subdir
        p.update()
        stdscr.addstr(4,0,f"{fi} files ")
        stdscr.addstr(4,15,f"store {parse_size(msize)}          ")
        stdscr.addstr(4,35,f"against {parse_size(p.max)}            ")
        stdscr.addstr(5,0,f"{errs} directory errors",cursesplus.set_colour(cursesplus.BLACK,cursesplus.YELLOW))
        stdscr.addstr(6,0,f"{corr} corrupted files",cursesplus.set_colour(cursesplus.BLACK,cursesplus.RED))
        try:
            for file in files:
                
                fx = os.path.join(subdir, file)
                
                fy = FileObject(fx)
                if fy.size > used:# Corrupted size
                    corr += 1
                    fy.size = -1
                fi += 1
                final.append(fy)
                
                msize += fy.size
                p.value = msize
                

        except:
            errs += 1
            continue
    p.done()
    cursesplus.showcursor()
    return final

def mfind(stdscr):
    mxz = mass_index_with_progress_bar(stdscr,"/")

def main(stdscr):
    while True:
        wtd = cursesplus.coloured_option_menu(stdscr,["Find Large Files","Quit"])
        if wtd == 1:
            sys.exit()
        elif wtd == 0:
            mfind(stdscr)

curses.wrapper(main)
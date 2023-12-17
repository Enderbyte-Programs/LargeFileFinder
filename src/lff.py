#!/usr/bin/python3
import curses
import datetime
import sys
import os
import shutil
import glob
import gzip
from platform import system as ossys
import json
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

cachedir = os.path.expanduser("~/.lffcache")


class FileObject:
    def __init__(self,path):
        if path is None:
            return#Wait for manual execution
        self.path = path
        self.isdirectory = os.path.isdir(path)
        if not self.isdirectory:
            self.size = os.path.getsize(path)
        else:
            self.size = -1
        self.lastmodified = os.path.getmtime(path)
        self.lastadded = os.path.getatime(path)
    def serialize(self) -> dict:
        return {
            "path" : self.path,
            "isdir" : self.isdirectory,
            "size" : self.size,
            "lm" : self.lastmodified,
            "la" : self.lastadded
        }
    @staticmethod
    def loadfromdict(inp:dict):
        x = FileObject(None)
        x.path = inp["path"]
        x.isdirectory = inp["isdir"]
        x.size = inp["size"]
        x.lastmodified = inp["lm"]
        x.lastadded = inp["la"]
        return x

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

def mass_index_with_progress_bar(stdscr,directory,config={}) -> list:
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
    np = cursesplus.PleaseWaitScreen(stdscr,["Saving cache","Please be patient"])
    np.start()
    try:
        with open(cachedir,"wb+") as f:
            jxb = {"updated":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"data":[]}
            for sz in final:
                jxb["data"].append(sz.serialize())
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").ljust(12," ").encode()+gzip.compress(json.dumps(jxb).encode()))
    except:
        np.stop()
        np.destroy()
        cursesplus.messagebox.showerror(stdscr,["There was an error while saving"])
    np.stop()
    np.destroy()
    cursesplus.showcursor()
    return final

def cache_is_old() -> bool:
    if not os.path.isfile(cachedir):
        return False
    else:
        with open(cachedir,'rb') as f:
            data = f.read(12).decode()
                
        #data = read_cache()
        if (datetime.datetime.now() - datetime.datetime.strptime(data.strip(),"%Y-%m-%d %H:%M:%S")).total_seconds() // (3600*24) > 7:
            return True
        else:
            return False
def cache_exists() -> bool:
    return os.path.isfile(cachedir)

def read_cache() -> dict:
    with open(cachedir,"r") as fxz:
        data = json.loads(gzip.decompress(fxz.read()[12:]).decode())
    return data

def mfind(stdscr):
    cursesplus.displaymsgnodelay(stdscr,["Loading","Please wait"])
    if not cache_exists():
        mxz: list[FileObject] = mass_index_with_progress_bar(stdscr,"/")
    elif cache_is_old():
        if cursesplus.messagebox.askyesno(stdscr,["Data from this program is over 1 week old.","Would you like to perform a rescan?"]):
            mxz: list[FileObject] = mass_index_with_progress_bar(stdscr,"/")
        else:
            cursesplus.displaymsgnodelay(stdscr,["Reading cache","Please wait"])
            mxz = [FileObject.loadfromdict(z) for z in read_cache()["data"]]
    elif cache_exists and not cache_is_old():
        cursesplus.displaymsgnodelay(stdscr,["Reading cache","Please wait"])
        mxz = [FileObject.loadfromdict(z) for z in read_cache()["data"]]

    selected = 0
    yoffset = 0
    xoffset = 0
    while True:
        stdscr.clear()
        mx,my = os.get_terminal_size()
        curses.resize_term(my,mx)
        cursesplus.filline(stdscr,0,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(0,0,"For keybindings, press H",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(my-3,0,"─"*(mx-1))
        ei = 0
        for item in mxz[yoffset:(yoffset+my-4)]:
            ei += 1
            stdscr.addstr(ei,0,item.path[0:(mx-1)])
        stdscr.refresh()
        ch = stdscr.getch()

def main(stdscr):
    while True:
        wtd = cursesplus.coloured_option_menu(stdscr,["Find Large Files","Quit"])
        if wtd == 1:
            sys.exit()
        elif wtd == 0:
            mfind(stdscr)

curses.wrapper(main)
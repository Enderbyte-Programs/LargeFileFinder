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
        self.lastmodified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        self.lastadded = datetime.datetime.fromtimestamp(os.path.getatime(path))
    def serialize(self) -> dict:
        return {
            "path" : self.path,
            "isdir" : self.isdirectory,
            "size" : self.size,
            "lm" : self.lastmodified.timestamp(),
            "la" : self.lastadded.timestamp()
        }
    def out(self,size:int,nameoffset:int=0,col=["size","la"]):
        reserved = 42
        
        namer = size-reserved
        xfin = []
        for cx in col:
            xfin.append(str(self.serialize()[cx]))
            if cx == "size":
                xfin[-1] = parse_size_long(int(xfin[-1]))
            if cx == "la" or cx == "lm":
                xfin[-1] = datetime.datetime.fromtimestamp(int(float(xfin[-1]))).strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.path[nameoffset:nameoffset+namer].ljust(namer)} {' '.join([xh.ljust(20) for xh in xfin])}"

    @staticmethod
    def loadfromdict(inp:dict):
        x = FileObject(None)
        x.path = inp["path"]
        x.isdirectory = inp["isdir"]
        x.size = inp["size"]
        x.lastmodified = datetime.datetime.fromtimestamp(inp["lm"])
        x.lastadded = datetime.datetime.fromtimestamp(inp["la"])
        return x

def parse_size(data: int) -> str:
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000000000:#No-one should EVER see this
        result = f"{round(data/1000000000000000,2)} EB"
    elif data > 2000000000000:
        result = f"{round(data/1000000000000,2)} TB"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    else:
        result = "??"
    if neg:
        result = "-"+result
    return result

def parse_size_long(data: int) -> str:
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000000000:#No-one should EVER see this
        result = f"{round(data/1000000000000000,2)} exabytes"
    elif data > 2000000000000:
        result = f"{round(data/1000000000000,2)} terabytes"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} gigabytes"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} megabytes"
    elif data > 2000:
        result = f"{round(data/1000,2)} kilobytes"
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
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").ljust(19," ").encode()+gzip.compress(json.dumps(jxb).encode()))
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
            data = f.read(19).decode()
                
        #data = read_cache()
        if (datetime.datetime.now() - datetime.datetime.strptime(data.strip(),"%Y-%m-%d %H:%M:%S")).total_seconds() // (3600*24) > 7:
            return True
        else:
            return False
def cache_exists() -> bool:
    return os.path.isfile(cachedir)

def read_cache() -> dict:
    with open(cachedir,"rb") as fxz:
        data = json.loads(gzip.decompress(fxz.read()[19:]).decode())
    return data

def mfind(stdscr):
    cursesplus.hidecursor()
    curses.mousemask(1)
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
    cursesplus.displaymsgnodelay(stdscr,["Sorting files","Please wait"])
    mxz.sort(key=lambda x: x.size, reverse=True)

    selected = []
    active = 0
    yoffset = 0
    xoffset = 0
    msx = -1
    msy = -1
    while True:
        stdscr.clear()
        mx,my = os.get_terminal_size()
        curses.resize_term(my,mx)
        cursesplus.filline(stdscr,0,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(0,0,"For keybindings, press H [CLICK ME FOR HELP]",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(my-3,0,"─"*(mx-1))
        stdscr.addstr(1,0,"Name".ljust(mx-42)+" "+"Size".ljust(20)+" Last accessed")
        ei = 1
        for item in mxz[yoffset:(yoffset+my-5)]:
            ei += 1
            if yoffset+ei-2 in selected and yoffset+ei-2 != active:
                stdscr.addstr(ei,0,item.out(mx-20,xoffset),cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
            elif yoffset+ei-2 == active and not yoffset+ei-2 in selected:
                stdscr.addstr(ei,0,item.out(mx-20,xoffset),cursesplus.set_colour(cursesplus.BLACK,cursesplus.CYAN))
            elif yoffset+ei-2 == active and yoffset+ei-2 in selected:
                stdscr.addstr(ei,0,item.out(mx-20,xoffset),cursesplus.set_colour(cursesplus.WHITE,cursesplus.CYAN))
            else:
                stdscr.addstr(ei,0,item.out(mx-20,xoffset))
        for es in range(1,my-1):
            stdscr.addstr(es,my-19,"│")
        stdscr.addstr(my-2,mx-20,f"{active}/{len(mxz)} files")
        stdscr.addstr(my-2,0,f"{len(selected)} files selected")
        stdscr.addstr(my-2,20,f"totalling {parse_size(sum([mxz[z].size for z in selected]))}")
        
        if xoffset > 0:
            stdscr.addstr(my-1,0,f"<<< {xoffset}")
        try:
            _, msx, msy, _, _ = curses.getmouse()
        except:
            pass
        if msy >= 0 and msx >= 0:
            stdscr.addstr(msy,msx,"↖",cursesplus.set_colour(cursesplus.BLUE,curses.COLOR_WHITE))
        stdscr.addstr(0,mx-10,f"{msx},{msy}",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.refresh()
        ch = stdscr.getch()
        
        if ch == curses.KEY_DOWN and active < len(mxz)-1:

            active += 1
            if active > yoffset+my-7:
                yoffset += 1
        elif ch == curses.KEY_UP and active > 0:
            active -= 1
            if active < yoffset:
                yoffset -= 1
        elif ch == 115:
            if active in selected:
                selected.remove(active)
            else:
                selected.append(active)
        elif ch == 113:
            return
        elif ch == 114:
            if cursesplus.messagebox.askyesno(stdscr,["Warning","This will perform a full rescan of the selected folder","Are you sure you want to continue?"]):
                mxz: list[FileObject] = mass_index_with_progress_bar(stdscr,"/")
                mxz.sort(key=lambda x: x.size, reverse=True)
        elif ch == curses.KEY_RIGHT:
            xoffset += 1
        elif ch == curses.KEY_LEFT and xoffset > 0:
            xoffset -= 1
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            selected = [active]
        elif ch == curses.KEY_PPAGE and yoffset > 0:
            yoffset -= 1
        elif ch == curses.KEY_NPAGE:
            yoffset += 1
        
        elif ch == 104 or (msx > 25 and msx < 43 and msy == 0):
            cursesplus.displaymsg(stdscr,[
"Q: Quit",
"H: Help",
"Enter: Select",
"S: Add to selection",
"Up Arrow: Move selector up",
"Down arrow: Move selector down",
"Left Arrow: Move names list to the left",
"Right Arrow: Move names list to the right",
"R: Rescan files"

            ])

def main(stdscr):

    mfind(stdscr)

curses.wrapper(main)
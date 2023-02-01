#!/usr/bin/env python3
import os
import sys
import curses
from curses.textpad import rectangle
import sys
import datetime
import cursesplus as libcurses
from glob import glob
import re
import gzip
import json
os.system("mode 160,42")#Windows, force large size
sade = True
ldir = "/"
if len(sys.argv) > 1:
    ldir = sys.argv[1]
    sade = True
else:
    sade = False
    ldir = "/"
def parse_size(data: int) -> str:
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    if neg:
        result = "-"+result
    return result

def writecache(data: dict):
    ndate: bytes = str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")).encode()
    compressed_data: bytes = gzip.compress(json.dumps(data).encode())
    finaldata: bytes = ldir.encode()+b'\n'+ndate+b'\n'+compressed_data
    cachefile = os.path.expandvars("%USERPROFILE%\\.lffcache")
    with open(cachefile,"wb+") as f:
        f.write(finaldata)

def main(stdscr):
    global ldir
    if not sade:
        opath = libcurses.cursesinput(stdscr,"What File Path do you want to scan?")
        if not os.path.isdir(opath.strip()):
            libcurses.displaymsg(stdscr,["Bad Path"])
            return

        ldir = opath.strip()
    stdscr.erase()
    stdscr.addstr(0,0,"LFF by Enderbyte Programs...")
    stdscr.refresh()

    totalsize = 0
    refresh = True
    fileslist = {}
    selected = 0
    offset = 0
    stdscr.nodelay(False)
    curses.start_color()
    xoffset = 0
    dlist = []
    libcurses.load_colours(True)
    FILTERED = 0
    FILTEREXT = ""
    FILTERRE = ""
    cdate = str(datetime.datetime.now())
    
    #curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_WHITE)
    try:

        stdscr.addstr(0,0,"Reading cache")
        stdscr.refresh()
        if not os.path.isfile(os.path.expandvars("%USERPROFILE%\\.lffcache")):
            pass
        else:
            try:
                _stime = datetime.datetime.now()
                try:
                    with open(os.path.expandvars("%USERPROFILE%\\.lffcache"),"rb") as f:
                        rawdata = f.read()
                except:
                    raise FileNotFoundError("Cache not found")
                cpath = rawdata.split(b'\n')[0]
                cdate = datetime.datetime.strptime(rawdata.split(b'\n')[1].decode(),"%Y-%m-%d %H-%M-%S")
                xdata = b'\n'.join(rawdata.split(b'\n')[2:])
                
                fileslist = json.loads(gzip.decompress(xdata).decode())
                fileslist = {k:v for k,v in fileslist.items() if k.startswith(ldir)}
                locatek = list(fileslist.items())[0][0].replace(ldir,"")
                if locatek[0] == "\\":
                    locatek = locatek[1:]
                locateks = locatek.split("\\")[0]
                for lp in list(fileslist.items()):
                    if locateks != lp[0]:
                        break
                else:
                    #UNDIVERSE!
                    raise RuntimeError("Insufficient diversity")
                if len(fileslist) == 0:
                    raise RuntimeError("empty")
                nfileslist = list(fileslist.items())
            except Exception as e:
                stdscr.addstr(5,0,f"Cache could not be used. {e}")
                stdscr.refresh()
                os.remove(os.path.expandvars("%USERPROFILE%\\.lffcache"))
            else:
                refresh = False
                _etime = datetime.datetime.now()
        
        while True:
            fl = 0
            sx,sy = os.get_terminal_size()
            maxname = sx - 15
            flx = 0
            if refresh:
                fileslist = {}
                nfileslist = []
                _stime = datetime.datetime.now()
                stdscr.addstr(0,0,"Calculating Files")
                stdscr.refresh()
                for subdir, dirs, files in os.walk(ldir):
                    for file in files:
                        fl += 1
                        try:
                            flx += 1
                            stdscr.addstr(0,0," "*(sx-1))
                            stdscr.addstr(0,0,f"Indexing Files ({parse_size(totalsize)})"[0:sx-1])
                            stdscr.refresh()
                            size = os.path.getsize(os.path.join(subdir, file))
                            fileslist[os.path.join(subdir, file)] = size
                            totalsize += size
                            
                        except (PermissionError, FileNotFoundError, OSError):
                            pass
                stdscr.addstr(1,0,"Sorting...")
                stdscr.refresh()
                fileslist = {k: v for k, v in sorted(fileslist.items(), key=lambda item: item[1],reverse=True)}
                nfileslist = list(fileslist.items())
                stdscr.addstr(2,0,"Saving Cache")
                stdscr.refresh()
                writecache(fileslist)
                cdate = datetime.datetime.now()
                
                _etime = datetime.datetime.now()
            refresh = False
            totalsize = 0
            if FILTERED == 1:
                fileslist = {k:v for k,v in fileslist.items() if k.endswith(FILTEREXT.strip())}
                nfileslist = list(fileslist.items())
            elif FILTERED == 2:
                try:
                    fileslist = {k:v for k,v in fileslist.items() if re.search(FILTERRE,k) != None}
                    nfileslist = list(fileslist.items())
                except:
                    libcurses.displaymsg(stdscr,["Regex Error","There was an error in the filter","Filter will now be disabled."])
            
            stdscr.addstr(0,0," "*(sx-1))
            stdscr.addstr(0,0,f"{len(nfileslist)} files in {_etime - _stime}| coords: {xoffset},{selected} | Press h for help | Data from {str(cdate)}"[0:sx-1])
            rectangle(stdscr,1,0,sy-2,sx-1)
            if len(nfileslist) == 0:
                stdscr.addstr(2,1,":( No files found. Press Q to quit or F to change filters")
            yinc = 0
            for file in nfileslist[offset:offset+(sy-4)]:
                yinc += 1
                
                name, size = file
                name = name[xoffset:]  
                if len(name) > maxname:
                    name = name[0:maxname-3] + "..."
                else:
                    name = name + ((maxname-len(name))*" ")
                
                size = parse_size(size)
                message = name + " " + size
                if yinc + offset -1 == selected:
                    stdscr.addstr(yinc + 1,1,message,curses.color_pair(1))
                else:
                    stdscr.addstr(yinc + 1,1,message)
            try:
                stdscr.addstr(sy-1,0,(str(os.path.getsize(list(fileslist.keys())[selected])) + " Bytes, Last updated: "+ str(datetime.datetime.fromtimestamp(os.path.getctime(list(fileslist.keys())[selected]))))[0:sx-1])
            except FileNotFoundError:
                stdscr.addstr(sy-1,0,"Error, file not found. Please refresh")
            except IndexError:
                selected = len(nfileslist)-1
            except PermissionError:
                stdscr.addstr(sy-1,0,"Error: no permission!")
            stdscr.refresh()
            ch = stdscr.getch()
            if ch == 114:
                refresh = True#Refresh if R is pressed
            elif ch == curses.KEY_DOWN:
                if selected == len(fileslist)-1:
                    pass
                else:
                    selected += 1
                    if selected > offset + (sy-5):
                        offset += 1# Page goes down
            elif ch == curses.KEY_UP:
                if selected > 0:
                    selected -= 1
                    if selected < offset and offset > 0:
                        offset -= 1
            elif ch == curses.KEY_RIGHT:
                xoffset+= 1
            elif ch == curses.KEY_LEFT:
                if xoffset > 0:
                    xoffset -= 1
            elif ch == curses.KEY_SLEFT:
                xoffset = 0
            elif ch == 101:
                offset = len(nfileslist)-1
                selected = len(nfileslist)-1
            elif ch == 104:
                libcurses.displaymsg(stdscr,[
                    "LFF help menu",
                    "DEL: Delete selected file (permanently)",
                    "H: help menu",
                    "E: Jump to bottom of page",
                    "T: Jump to top of page",
                    "R: Refresh sizes (takes a long time)",
                    "Right Arrow: Move page right",
                    "Left Arrow: Move page left",
                    "Shift Left Arrow: Move page all the way to the left",
                    "Down Arrow: Move page down",
                    "Up Arrow: Move page up",
                    "S: Change terminal size (WINDOWS7 Only)",
                    "Q: Quit Program",
                    "D: More Deletion Options",
                    "F: Filter Options",
                    "C: Clear cache"
                ])
            elif ch == 99:
                if libcurses.askyesno(stdscr,"Are you sure you want to clear the cache? Future startups will take a long time."):
                    os.remove(os.path.expandvars("%USERPROFILE%\\.lffcache"))
            elif ch == 100 or curses.keyname(ch).decode() == "^D":
                #More deletion option
                stdscr.erase()
                __O = libcurses.displayops(stdscr,["Back","Delete Selected Item","Delete Everything","Delete everything of certain extension"])
                if __O == 0:
                    pass
                elif __O == 1:
                    try:
                        os.remove(list(fileslist.keys())[selected])
                        del fileslist[list(fileslist.keys())[selected]]
                        if selected > 0:
                            selected -= 1
                        fileslist = {k: v for k, v in sorted(fileslist.items(), key=lambda item: item[1],reverse=True)}
                        nfileslist = list(fileslist.items())
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        libcurses.displaymsg(stdscr,["Failed to remove file.",str(e)[0:sx-10]])
                elif __O == 2:
                    stdscr.erase()
                    if libcurses.askyesno(stdscr,"Are you sure that you want to delete EVERY FILE HERE?"):
                        if libcurses.askyesno(stdscr,"THIS CAN BE VERY DESTRUCTIVE! ARE YOU SURE YOU WANT TO PROCEED"):
                            stdscr.erase()
                            for file in list(fileslist.keys()):
                                stdscr.addstr(0,0,file)
                                stdscr.refresh()
                                try:
                                    os.remove(file)
                                except:
                                    stdscr.addstr(1,0,f"Failed to delete")
                            selected = 0
                            refresh = True
                            libcurses.displaymsg(stdscr,["All files deleted"])
                        
                elif __O == 3:
                    stdscr.erase()
                    npext = libcurses.cursesinput(stdscr,"Please input the extension you would like to delete.")
                    stdscr.erase()
                    if libcurses.askyesno(stdscr,f"Warning: This can be very destructive! Continue?"):
                        stdscr.erase()
                        for file in list(fileslist.keys()):
                            if file.endswith(npext.strip()):
                                stdscr.addstr(0,0,file)
                                try:
                                    os.remove(file)
                                except:
                                    stdscr.addstr(1,0,f"Failed to delete")
                        refresh = True
                                
            elif ch == 113:
                stdscr.erase()
                if libcurses.askyesno(stdscr,"Are you sure you want to quit?"):
                    return
            elif ch == 102:
                stdscr.clear()
                _fop = libcurses.displayops(stdscr,["Back","Disable Filter","Filter by extension","Filter by regex"])
                if _fop > 0 and FILTERED > 0:
                    refresh = True
                if _fop == 1:
                    FILTERED = 0
                    
                    selected = 0
                    offset = 0
                if _fop == 2:
                    FILTEREXT = libcurses.cursesinput(stdscr,"What extension to filter?")
                    FILTERED = 1
                    
                    selected = 0
                    offset = 0
                if _fop == 3:
                    FILTERED = 2
                    
                    selected = 0
                    offset = 0
                    FILTERRE = libcurses.cursesinput(stdscr,"What RegEx to filter?")
                
            elif ch == 116:
                selected = 0
                offset = 0
            elif ch == 115:
                #Change Terminal size Size
                try:
                    newx = int(libcurses.cursesinput(stdscr,"How many columns should there be?").strip())
                    newy = int(libcurses.cursesinput(stdscr,"How many rows should there be?").strip())
                except:
                    libcurses.displaymsg(stdscr,"Invalid input")
                else:
                    os.system(f"mode {newx},{newy}")
            elif ch == curses.KEY_DC:
                try:
                    os.remove(list(fileslist.keys())[selected])
                    del fileslist[list(fileslist.keys())[selected]]
                    if selected > 0:
                        selected -= 1
                    fileslist = {k: v for k, v in sorted(fileslist.items(), key=lambda item: item[1],reverse=True)}
                    nfileslist = list(fileslist.items())
                except FileNotFoundError:
                    pass
                except Exception as e:
                    libcurses.displaymsg(stdscr,["Failed to remove file.",str(e)[0:sx-10]])
            stdscr.erase()
    except KeyboardInterrupt:
        sys.exit(0)

try:
    curses.wrapper(main)
except KeyboardInterrupt:#No traceback on ctrl-c
    sys.exit(0)

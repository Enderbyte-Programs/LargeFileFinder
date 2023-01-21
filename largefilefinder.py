#!/usr/bin/env python3
import os
import sys
import curses
from curses.textpad import rectangle
import sys
import datetime
import libcurses
from glob import glob
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

def main(stdscr):
    global ldir
    if not sade:
        opath = libcurses.cursesinput(stdscr,"What File Path do you want to scan?")
        if not os.path.isdir(opath.strip()):
            libcurses.displaymsg(stdscr,["Bad Path"])
            return

        ldir = opath.strip()
    stdscr.erase()
    stdscr.addstr(0,0,"Initializing File counter (This may take a minute depending on your disk speed)")
    stdscr.refresh()
    file_count = sum(len(files) for _, _, files in os.walk(ldir))

    refresh = True
    fileslist = {}
    selected = 0
    offset = 0
    stdscr.nodelay(False)
    curses.start_color()
    xoffset = 0
    dlist = []
    libcurses.load_colours()
    
    #curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_WHITE)
    try:
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
                            stdscr.addstr(0,0,f"Calculating ({round(flx/file_count*100,1)} %)"[0:sx-1])
                            stdscr.refresh()
                            fileslist[os.path.join(subdir, file)] = os.path.getsize(os.path.join(subdir, file))
                            
                        except (PermissionError, FileNotFoundError, OSError):
                            pass
                stdscr.addstr(1,0,"Sorting...")
                stdscr.refresh()
                fileslist = {k: v for k, v in sorted(fileslist.items(), key=lambda item: item[1],reverse=True)}
                nfileslist = list(fileslist.items())
                _etime = datetime.datetime.now()
            refresh = False
            
            stdscr.addstr(0,0," "*(sx-1))
            stdscr.addstr(0,0,f"{file_count} files in {_etime - _stime}| coords: {xoffset},{selected} | Press h for help"[0:sx-1])
            rectangle(stdscr,1,0,sy-2,sx-1)
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
                    "D: More Deletion Options"
                ])
            elif ch == 100:
                #More deletion option
                stdscr.erase()
                __O = libcurses.displayops(stdscr,["Back","Delete Selected Item","Delete Everything","Delete everything of certain extension","Delete everything larger than certain size","Delete by glob"])
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
                elif __O > 3:
                    libcurses.displaymsg(stdscr,"Not yet implemented. Please look for a newer release.")
                                
            elif ch == 113:
                stdscr.erase()
                if libcurses.askyesno(stdscr,"Are you sure you want to quit?"):
                    return
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

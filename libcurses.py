"""
Libcurses is an extension to the curses module that provides some useful featues. This library will be distributed as part of many Enderbyte Programs software

(c) 2022-2023 Enderbyte Programs, no rights reserved
"""

import curses
from curses.textpad import rectangle, Textbox
import os
from time import sleep
import random

def cursestransition(stdscr,func_to_call,args=(),type=0):
    block = "█"
    mx,my = os.get_terminal_size()
    if type == 0:
        
        for y in range(my-1):
            stdscr.addstr(y,0,block*(mx-1))
            stdscr.refresh()
            sleep(0.01)
        for y in range(my-1):
            stdscr.addstr(y,0," "*(mx-1))
            stdscr.refresh()
            sleep(0.01)
    elif type == 1:
        _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
        while _grid:
            for i in range(round(((my*mx)/(24*80))*20)):# Fixing slow transitions on HD screens
                try:
                    pk = random.choice(_grid)
                    _grid.pop(_grid.index(pk))
                    stdscr.addstr(pk[1],pk[0],block)
                    stdscr.refresh()
                except:
                    break
            sleep(0.01)
        _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
        while _grid:
            for i in range(round(((my*mx)/(24*80))*20)):
                try:
                    pk = random.choice(_grid)
                    _grid.pop(_grid.index(pk))
                    stdscr.addstr(pk[1],pk[0]," ")
                    stdscr.refresh()
                except:
                    break
            sleep(0.01)
    func_to_call(*args)
def displaymsg(stdscr,message: list):
    stdscr.clear()
    x,y = os.get_terminal_size()
    ox = 0
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message]#Limiting characters
    maxs = max([len(s) for s in message])
    rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+2, x//2+(maxs//2+1)+1)
    stdscr.addstr(0,0,"Message: ")
    mi = -(len(message)/2)
    
    for msgl in message:
        mi += 1
        stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl)
    stdscr.addstr(y-2,0,"Press any key to dismiss this message")
    stdscr.refresh()
    stdscr.getch()
    stdscr.erase()

def displaymsgnodelay(stdscr,message: list):
    stdscr.clear()
    x,y = os.get_terminal_size()
    ox = 0
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message]#Limiting characters
    maxs = max([len(s) for s in message])
    rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+2, x//2+(maxs//2+1)+1)
    stdscr.addstr(0,0,"Message: ")
    mi = -(len(message)/2)
    
    for msgl in message:
        mi += 1
        stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl)
    stdscr.refresh()
    stdscr.erase()

def cursesinput(stdscr,prompt: str):
    x,y = os.get_terminal_size()
    stdscr.erase()
    stdscr.addstr(0, 0, prompt)
    stdscr.addstr(5,0,"hit Enter to send")
    editwin = curses.newwin(1,x-2, 2,1)
    rectangle(stdscr, 1,0, 3, x-1)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()
    return message

def displayops(stdscr,options: list,title="Please choose an option") -> int:
    mx, my = os.get_terminal_size()
    selected = 0
    
    options = [l[0:mx-3] for l in options]
    maxlen = max([len(l) for l in options])
    stdscr.addstr(0,0,title[0:mx-1])
    offset = 0
    while True:
        stdscr.addstr(0,0,title[0:mx-1])
        mx, my = os.get_terminal_size()
        options = [l[0:mx-3] for l in options]
        maxlen = max([len(l) for l in options])
        if len(options) > my-5:
            rectangle(stdscr,1,0,my-2,mx-1)
        else:
            rectangle(stdscr,1,0,2+len(options),maxlen+2)
        oi = -1
        for o in options[offset:offset+(my-4)]:
            oi += 1
            try:
                if oi == selected-offset:
                    stdscr.addstr(oi+2,1,o,curses.color_pair(4))
                else:
                    stdscr.addstr(oi+2,1,o)
            except curses.error:
                pass
        stdscr.addstr(my-1,0,"Please choose an option with the arrow keys then press enter."[0:mx-1])
        stdscr.refresh()
        _ch = stdscr.getch()
        if _ch == curses.KEY_ENTER or _ch == 10 or _ch == 13:
            return selected
        elif _ch == curses.KEY_UP and selected > 0:
            if offset > 0 and selected-offset == 0:
                offset -= 1
            selected -= 1
        elif _ch == curses.KEY_DOWN and selected < len(options)-1:
            if selected >= my-6:
                offset += 1
            selected += 1
        elif _ch == curses.KEY_BACKSPACE or _ch == 98:
            return -1
        stdscr.erase()

def askyesno(stdscr,title: str) -> int:
    result = displayops(stdscr,["Yes","No"],title)
    if result == 0:
        return True
    else:
        return False
def load_colours():
    #curses.init_pair(7,curses.COLOR_BLACK,curses.COLOR_BLACK)
    #curses.init_pair(9,curses.COLOR_RED,curses.COLOR_BLACK)
    for i in range(1,10):
        curses.init_pair(i,curses.COLOR_BLACK,curses.COLOR_WHITE)
    #curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_BLACK)
    #curses.init_pair(3,curses.COLOR_GREEN,curses.COLOR_BLACK)
    #curses.init_pair(4,curses.COLOR_CYAN,curses.COLOR_BLACK)
    #curses.init_pair(5,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    #curses.init_pair(8,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    #curses.init_pair(6,curses.COLOR_WHITE,curses.COLOR_BLACK) 

def displayerror(stdscr,e,msg: str):
    displaymsg(stdscr,["An error occured",msg,str(e)])

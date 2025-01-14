import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time
from os import environ
from traceback import format_exc


from Timer import Timer
from define import Flags, logger
from RIPEntry import RIPEntry




def startSettings(stdscr):
    
    
    curses.start_color()
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)  
    curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    stdscr.idcok(False)
    stdscr.idlok(False)
    
def menu(stdscr, router):
    
    startSettings(stdscr)
    stdscr.clear()
    stdscr.nodelay(True)
    curses.curs_set(0)
    
    y,x = stdscr.getmaxyx()
    middle_x = x//2
    middle_y = y//2
    Y_B = curses.color_pair(2)
    B_W = curses.color_pair(3)
    W_B = curses.color_pair(4)
    G_B = curses.color_pair(1)
    M=curses.color_pair(10)
    stdscr.attron(G_B)

    rectangles = [
        {"name": "browse", "coords": (1, 10, 7, 35), "label": "BROWSE"},
        {"name": "search", "coords": (1, 40, 7, 65), "label": "SEARCH"},
        {"name": "commands", "coords": (9, 25, 15, 50), "label": "COMMANDS"},  
    ]
   

    current_index = 0

    while True:
        stdscr.erase()
        for i, rect in enumerate(rectangles):
            y1, x1, y2, x2 = rect["coords"]
            label = rect["label"]

            if i == current_index:
                stdscr.attron(B_W)
            else:
                stdscr.attron(W_B)

            rectangle(stdscr, y1, x1, y2, x2)

            text_x = x1 + (x2 - x1) // 2 - len(label) // 2
            text_y = y1 + (y2 - y1) // 2
            stdscr.addstr(text_y, text_x, label)

            stdscr.attroff(B_W)
            stdscr.attroff(W_B)
        stdscr.addstr(20, middle_x - 15, "Apasati 'q' pentru a iesi", curses.A_BLINK)
        
        key = stdscr.getch()
        if key != -1:
            logger.debug(f'key:{key}')
        if key == curses.KEY_RIGHT:
            current_index = (current_index + 1) % len(rectangles)
        elif key == curses.KEY_LEFT:
            current_index = (current_index - 1) % len(rectangles)
        elif key == ord('\n'):
            if rectangles[current_index]["name"] == "search":
                wrapper(search, router)
                stdscr.clear()
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
                stdscr.idcok(False)
                stdscr.idlok(False)
            elif rectangles[current_index]["name"] == "commands":
                wrapper(modify, router)
                stdscr.clear()
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
                stdscr.idcok(False)
                stdscr.idlok(False)
            elif rectangles[current_index]["name"] == "browse":
                wrapper(browse, router)
                stdscr.clear()
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
                stdscr.idcok(False)
                stdscr.idlok(False)
                
        elif key == ord('q'):  
            stdscr.clear()
            stdscr.refresh()
            return
        
        stdscr.refresh()


def modify(stdscr, router):
    stdscr.clear()
    
    
    height, width = stdscr.getmaxyx()
    middle_x = width//2
    modify_win = curses.newwin(5, 50, 0, width // 2 - 25)
    modify_win.box()
    modify_win.addstr(1, 19, "COMMANDS", curses.A_BOLD | curses.A_REVERSE)

    edit_win = modify_win.derwin(1, 40, 3, 5)
    cutie = Textbox(edit_win)

    output_win = curses.newwin(height - 6, width - 2, 6, 1)  
    output_win.attron(curses.color_pair(4)) 
    output_win.box()
    output_win.attroff(curses.color_pair(4))

    output_win.addstr(1, middle_x - 6 , "OUTPUT", curses.A_BOLD)  
    stdscr.refresh()
    modify_win.refresh()
    output_win.refresh()

    text_buffer = []  

    prompt_text = "asaf&alex@RIPv2-terminal: "

    #adds text to the buffer such that each line is less than 50chars and the words dont get split up
    def addToBuffer(text:str):
        words = text.split(' ')
        while words:
            textAux = []
            for i, word in enumerate(words):
                if len(' '.join(textAux )) +len(word)  < 50:
                    textAux.append(word)
                else:
                    break
        
            line = prompt_text + ' '.join(textAux)
            text_buffer.append(line)
           
            words = words[len(textAux):]
    
    
    commands = ['help-shows this menu',
                'set/get IP timeout/garbage/metric [newval]-sets new val for an interface for timeout/garbage/metric.',
                'whoami-displays the router\'s ID.',
                'set/get update [newVal]-sets new val for the update timer.',
                'q-quit this mode.',
                'clear-clears the screen.',
                'interfaces-displays the IP addresses.',
                'status-prints the pids of the processes.'
                ]
    
   
        
        
    def displayOutput(text_buffer):
        #maxim 15 linii pe ecran (ultimele 15)
        if len(text_buffer)>15:
            text_buffer = text_buffer[-15:]
        output_win.clear()  
        output_win.box()  
        output_win.addstr(1, middle_x - 6,  "OUTPUT", curses.A_BOLD)  
        for i, line in enumerate(text_buffer[-(height - 9):]):  
            output_win.addstr(i + 3, 1, line)  
        output_win.refresh()
    
    for i in commands:
        addToBuffer(i)
        
    displayOutput(text_buffer)
    
    while True:
        cutie.edit()  

        text = cutie.gather().strip()
        
        #text = comanda introdusa
        #in text_buffer se baga textul output
        
        
        if text.lower() == "q":
            stdscr.clear()
            stdscr.refresh()
            return
        elif text.lower()=="status":
            addToBuffer(f'{router.listenProcess.is_alive()} {router.sendProcess.is_alive()} {router.timeCheckerProcess.is_alive()}')
        elif text.lower() == "clear":
            output_win.clear()  
            output_win.box()  
            output_win.addstr(1, middle_x - 6, "OUTPUT", curses.A_BOLD)  
            output_win.refresh()
            text_buffer = []
        elif text.lower()=="help":
            
            
            for command in commands:
                addToBuffer(command)
                
        elif text.lower()=="whoami":
            ID = environ['ID']
            addToBuffer(f'Router ID: {ID}.')
            
        elif text.lower()=="interfaces":
            IP = list(router.sendSockets.keys())
            addToBuffer(', '.join(IP))
            
        else:
            
            words = text.split(' ')
            
            logger.debug(words)
            try:
                
                if words[0]=="set":
                    if words[1] == "update":
                        newVal = float(words[2])    
                        if newVal > 0:
                            router.setUpdate(newVal)
                            addToBuffer(f'Update timer changed to {newVal} s.')
                        else:
                            addToBuffer('New val must be a positive number.')
                            
                    
                    
                    elif words[1] in list(router.sendSockets.keys()):
                        
                        if words[2]=='timeout':
                            newVal = float(words[3])
                            if newVal>0:
                                router.setTimeout(newVal, words[1])
                                addToBuffer(f'Timeout for {words[1]} changed to {newVal} s.')
                            else:
                                addToBuffer(f'Newval must be a positive float.')
                        elif words[2]=='garbage':
                            newVal = float(words[3])
                            if newVal >0:
                                router.setGarbage(newVal, words[1])
                                addToBuffer(f'Garbage for {words[1]} changed to {newVal} s.')
                            else:
                                addToBuffer('Newval must be a positive float.')
                        elif words[2]=='metric':
                            newVal = int(words[3])
                            if newVal > 0:
                                router.setMetric(newVal, words[1])
                                addToBuffer(f'Metric for {words[1]} changed to {newVal}.')
                            else:
                                addToBuffer('Newval must be a positive integer.')
                        else:
                            addToBuffer('Wrong format.')
                    else:
                        addToBuffer('Error: unrecognized command/wrong format. Run help to see all the available commands and their format.')
                        
                        
                        
                        
                elif words[0] =="get":
                    if words[1]=="update":

                        addToBuffer(f'The update timeout is {router.getUpdate()} s.')
                    elif words[1] in list(router.sendSockets.keys()):
                        if words[2]=='timeout':
                            addToBuffer(f'The timeout for {words[1]} is {router.getTimeout(words[1])} s.')
                        elif words[2]=='metric':
                            addToBuffer(f'The metric for {words[1]} is {router.getMetric(words[1])}.')
                        elif words[2]=='garbage':
                            addToBuffer(f'The garbage for {words[1]} is {router.getGarbage(words[1])} s.')
                        else:
                            addToBuffer(f'Wrong format.')
                    else:
                        addToBuffer('Error: unrecognized command. Run help to see all the available commands.')
                else:
                    addToBuffer('Error: unrecognized command. Run help to see all the available commands.')
            except BaseException as e:
                logger.error(format_exc())
                addToBuffer('Error: unrecognized command/wrong format. Run help to see all the available commands and their format.')
                
            
            
        
        displayOutput(text_buffer)
        

        modify_win.clear()
        modify_win.box()
        modify_win.addstr(1, 19, "COMMANDS", curses.A_BOLD)
        stdscr.refresh()
        modify_win.refresh()

        edit_win.move(0, 0)  
        stdscr.refresh()
        modify_win.refresh()


def search(stdscr,  router):
    curses.curs_set(0)  
    stdscr.clear()

    Y_B = curses.color_pair(2)
    G_B = curses.color_pair(1)
    M = curses.color_pair(10)
    _, middle_x = stdscr.getmaxyx()
    middle_x = middle_x //2
    curses.start_color()

    stdscr.addstr(0, 37, "SEARCH", curses.A_BOLD | Y_B | curses.A_REVERSE)
    win = curses.newwin(5, 50, 1, middle_x - 25)
    win.attron(G_B)  
    win.box()
    win.attroff(G_B)

    win.refresh()

    search_input = win.derwin(1, 40, 3, 5)  
    search_textbox = Textbox(search_input)

    win_AF_id = curses.newwin(3, 30, 10, 5)
    win_AF_id.box()
    win_AF_id.refresh()
    
    win_IPADDR = curses.newwin(3, 30, 10, 45)
    win_IPADDR.box()
    win_IPADDR.refresh()

    win_Subnet = curses.newwin(3, 30, 14, 5)
    win_Subnet.box()
    win_Subnet.refresh()

    win_NextHop = curses.newwin(3, 30, 14, 45)
    win_NextHop.box()
    win_NextHop.refresh()

    win_Metric = curses.newwin(3, 30, 18, 25)
    win_Metric.box()
    win_Metric.refresh()

    
    stdscr.addstr(9, 16, "AF_ID", curses.A_BOLD | M)
    stdscr.addstr(9, 58, "IP", curses.A_BOLD | M)
    stdscr.addstr(13, 14, "SUBNET MASK", curses.A_BOLD | M)
    stdscr.addstr(13, 55, "NEXT HOP", curses.A_BOLD | M)
    stdscr.addstr(17, 37, "METRIC", curses.A_BOLD | M)
    stdscr.refresh()

    
    options = [
        ("SEARCH", search_textbox, win),
        ("AF_ID", None, win_AF_id),
        ("IP", None, win_IPADDR),
        ("Subnet Mask", None, win_Subnet),
        ("Next Hop", None, win_NextHop),
        ("Metric", None, win_Metric)
    ]
    current_option = 0

    def clear_boxes():
        for _, _, subwin in options:  
            subwin.erase()
            subwin.box()
            subwin.refresh()
    
    def draw_menu():
        win.attron(G_B)  
        win.box()
        win.attroff(G_B)

        for idx, (label, _, subwin) in enumerate(options):
            if idx == current_option:
                if label != "SEARCH":  
                    subwin.attron(curses.A_REVERSE)  
            else:
                subwin.attroff(curses.A_REVERSE)  
            subwin.box()
            subwin.refresh()

        stdscr.refresh()
        win.refresh()  

    
    draw_menu()

    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_LEFT:
            current_option = (current_option - 1) % len(options)
        elif key == curses.KEY_RIGHT:
            current_option = (current_option + 1) % len(options)
        elif key == ord("\n"):  
            label, textbox, subwin = options[current_option]

            subwin.attroff(curses.A_REVERSE)
            subwin.box()
            subwin.refresh()

            if label == "SEARCH":  
                text = textbox.gather().strip()
                if text.lower() == "clear":
                    clear_boxes()
                    search_textbox.win.move(0, 0)
                curses.curs_set(1)
                textbox.edit()
                curses.curs_set(0)
            elif label == "AF_ID":  
                edit_AF = subwin.derwin(1, 20, 1, 5)
                cutie_AF = Textbox(edit_AF)
                curses.curs_set(1)
                cutie_AF.edit()
                curses.curs_set(0)
            elif label == "IP":  
                edit_IP = subwin.derwin(1, 20, 1, 5)
                cutie_IP = Textbox(edit_IP)
                curses.curs_set(1)
                cutie_IP.edit()
                curses.curs_set(0)
            elif label == "Subnet Mask":  
                edit_Subnet = subwin.derwin(1, 20, 1, 5)
                cutie_Subnet = Textbox(edit_Subnet)
                curses.curs_set(1)
                cutie_Subnet.edit()
                curses.curs_set(0)
            elif label == "Next Hop":  
                edit_NextHop = subwin.derwin(1, 20, 1, 5)
                cutie_NextHop = Textbox(edit_NextHop)
                curses.curs_set(1)
                cutie_NextHop.edit()
                curses.curs_set(0)
            elif label == "Metric":  
                edit_Metric = subwin.derwin(1, 20, 1, 5)
                cutie_Metric = Textbox(edit_Metric)
                curses.curs_set(1)
                cutie_Metric.edit()
                curses.curs_set(0)

            draw_menu()

        elif key == ord("q"):  
            stdscr.clear()
            stdscr.refresh()
            curses.flushinp() 
            return

        draw_menu()    



def window_text(window):
    G_B = curses.color_pair(1)
    window.addstr(1,2, '> AF_id:', curses.A_BOLD | G_B)
    window.addstr(2,2, '> IP:', curses.A_BOLD | G_B)
    window.addstr(3,2, '> Subnet:', curses.A_BOLD | G_B)
    window.addstr(4,2, '> NextHop:', curses.A_BOLD | G_B)
    window.addstr(5,2 ,'> Metrica:', curses.A_BOLD | G_B)
    window.addstr(6,2, '> RouteTag:', curses.A_BOLD|G_B)
    window.addstr(7,2, '> TimeOut:', curses.A_BOLD | G_B)
    window.addstr(8,2, '> Garbage:', curses.A_BOLD | G_B)
    window.addstr(9,2, '> Flags:', curses.A_BOLD | G_B)
def addText(window, ripEntry, timeout, garbage, flag, selected=False):
    C = curses.color_pair(11)
    M = curses.color_pair(10)
    
    if selected:
        font = M | curses.A_BOLD
    else:
        font = C | curses.A_BOLD
    window.addstr(1,15, str(ripEntry.getAF_id()), font)
    window.addstr(2,15, str(ripEntry.getIP()), font)
    window.addstr(3,15, str(ripEntry.getSubnet()), font)
    window.addstr(4,15, str(ripEntry.getNextHop()), font)
    window.addstr(5,15, str(ripEntry.getMetric()), font)
    window.addstr(6,15, str(ripEntry.getRT()), font)
    
    if timeout.getTimer()==-1:
        timeout="Not activated"
    else:
        timeout = round(timeout.getTimeout()- (time.time() - timeout.getTimer()),1)
    
    if garbage.getTimer()==-1:
        garbage="Not activated"
    else:
        garbage = round(garbage.getTimeout()- (time.time() - garbage.getTimer()),1)
        
    if flag == Flags.CHANGED:
        flag = "Changed"
    else:
        flag = "Unchanged"
    
    window.addstr(7,15, str(timeout), font)
    window.addstr(8,15, str(garbage), font)
    window.addstr(9,15, str(flag), font)
def delText(window):
    blank = "               "
    C = curses.color_pair(11)
    for i in range(1,10):
        window.addstr(i,15, blank)          
def browse(stdscr, router):
    stdscr.nodelay(True)
    stdscr.clear()
    
    
    curses.curs_set(0)
    curses.start_color()
    
    
    h,w =stdscr.getmaxyx()

    hWin = 11
    wWin = 35
    winArr = []


    logger.debug(f'{h} {w}')
    upLeftWin = curses.newwin(hWin, wWin, 1, 1)
    
    winArr.append(upLeftWin)
    
    upRightWin = curses.newwin(hWin, wWin, 1, w-1-1-wWin)
    winArr.append(upRightWin)
    
    downLeftWin = curses.newwin(hWin, wWin, h-1-1-hWin, 1)
    winArr.append(downLeftWin)
    
    downRightWin = curses.newwin(hWin, wWin, h-1-1-hWin, w-2-wWin)
    winArr.append(downRightWin)
    
    
    
    
    
    start = 0
    
    
    entries = router.table.getAllEntries()
    timeoutDict = router.table.getAllTimeout()
    garbageDict = router.table.getAllGarbage()
    flagDict = router.table.getAllFlag()
    
    toAdd = len(entries)%4
    if toAdd!=0:
        toAdd = 4-toAdd
    for i in range(0,toAdd):
        entries.append(RIPEntry())
    timeoutDict['0.0.0.0'] = Timer(0)
    garbageDict['0.0.0.0'] = Timer(0)
    flagDict['0.0.0.0'] = Flags.UNCHANGED
    
    
    for win in winArr:
        window_text(win)
        win.box()
    
    
        
    
        
    upLeft = True
    upRight = False
    downLeft = False
    downRight = False
            

    
    def draw():
        B_W = curses.color_pair(3)
        W_B = curses.color_pair(4)
        target = 0
        if upRight:
            target=1
        elif downLeft:
            target=2
        elif downRight:
            target = 3
        i = 0
        for win in winArr:
            delText(win)
            try:
                key = entries[start+i].getIP()
                if i == target:
                    addText(win, entries[start+i], timeoutDict[key], garbageDict[key], flagDict[key], True)
                else:
                    addText(win, entries[start+i], timeoutDict[key], garbageDict[key], flagDict[key])
                i = i+1
            except KeyError:
                continue
            win.refresh()
        
    
    stdscr.refresh()
    draw()
    refresh = Timer(0.1)
    refresh.activate()
    
    
    
    
    while True:
        
        if refresh.tick():
            nextUpdate = Timer(other=router.update)
            entries = router.table.getAllEntries()
            timeoutDict = router.table.getAllTimeout()
            garbageDict = router.table.getAllGarbage()
            flagDict = router.table.getAllFlag()
            toAdd = len(entries)%4
            if toAdd!=0:
                toAdd = 4-toAdd
            for i in range(0,toAdd):
                entries.append(RIPEntry())
            timeoutDict['0.0.0.0'] = Timer(0)
            garbageDict['0.0.0.0'] = Timer(0)
            flagDict['0.0.0.0'] = Flags.UNCHANGED
            
            if start>=len(entries):
                start = len(entries)-1-3
                upLeft = False
                upRight = False
                downLeft = False
                downRight = True
            draw()
            refresh.reset()
        

        
        
        key = stdscr.getch()
        if key == ord('q'):
            stdscr.clear()
            stdscr.refresh()
            return
        elif key == curses.KEY_RIGHT: 
             
            if upLeft:
                upLeft = False
                upRight = True
            elif upRight:
                continue
            elif downLeft:
                downLeft = False
                downRight = True
            elif downRight:
                continue
            
        elif key == curses.KEY_LEFT:  
            if upLeft:
                continue
            elif upRight:
                upLeft = True
                upRight = False
            elif downLeft:
                continue
            elif downRight:
                downRight = False
                downLeft=True
                
                
        elif key == curses.KEY_DOWN:  
            if upLeft:
                upLeft=False
                downLeft = True
            elif upRight:
                upRight = False
                downRight = True
                
            else:
                if start+4<len(entries):
                    start=start+4
                    
                    if downLeft:
                        
                        upLeft = True
                        downLeft = False
                        downRight=False
                        upRight = False
                    else:
                        upLeft = False
                        downLeft = False
                        downRight=False
                        upRight = True
                    

        elif key == curses.KEY_UP:  
            if downLeft:
                downLeft = False
                upLeft = True
            elif downRight:
                downRight = False
                upRight = True
            else:
                if start-4>=0:
                    start=start-4
                    if upRight:
                        upLeft = False
                        downLeft = False
                        downRight=True
                        upRight = False
                    else:
                        upLeft = False
                        downLeft = True
                        downRight=False
                        upRight = False
                
            

def CLI(router):
    wrapper(menu, router)
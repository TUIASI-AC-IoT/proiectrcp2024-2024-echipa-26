import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time

# o sa mai fac curat

stdscr = curses.initscr()
curses.start_color()
height, width = stdscr.getmaxyx()
middle_y = height // 2
middle_x = width // 2

curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
G_B = curses.color_pair(1)
Y_B = curses.color_pair(2)
M = curses.color_pair(10)

def startSettings(stdscr):
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)


def endSettings(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()


def searchAndBrowse(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    B_W = curses.color_pair(3)
    W_B = curses.color_pair(4)
    stdscr.attron(G_B)

    rectangles = [
        {"name": "browse", "coords": (1, 10, 7, 35), "label": "BROWSE"},
        {"name": "search", "coords": (1, 40, 7, 65), "label": "SEARCH"},
        {"name": "modify", "coords": (9, 25, 15, 50), "label": "MODIFY"},  
    ]

    current_index = 0

    while True:
        stdscr.clear()
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
        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_RIGHT:
            current_index = (current_index + 1) % len(rectangles)
        elif key == curses.KEY_LEFT:
            current_index = (current_index - 1) % len(rectangles)
        elif key == ord("\n"):  
            if rectangles[current_index]["name"] == "search":
                stdscr.attroff(curses.color_pair(1))
                stdscr.attroff(curses.color_pair(2))
                search(stdscr) 
            elif rectangles[current_index]["name"] == "modify":
                stdscr.attroff(curses.color_pair(1))
                stdscr.attroff(curses.color_pair(2))
                modify(stdscr)
            elif rectangles[current_index]["name"] == "browse":
                stdscr.addstr(17, 0, "BROWSE NU ARE NIMIC INCA :)")
            stdscr.refresh()
            stdscr.getch()
        elif key == ord('q'):  
            break


def modify(stdscr):
    stdscr.clear()
    curses.curs_set(1)

    height, width = stdscr.getmaxyx()

    modify_win = curses.newwin(5, 50, 0, width // 2 - 25)
    modify_win.box()
    modify_win.addstr(1, 20, "COMMANDS", curses.A_BOLD)

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

    while True:
        cutie.edit()  

        text = cutie.gather().strip()

        if text.lower() == "quit":
            curses.curs_set(0)
            break

        elif text == "":  
            continue 

        elif text.lower() == "clear":
            output_win.clear()  
            output_win.box()  
            output_win.addstr(1, middle_x - 6, "OUTPUT", curses.A_BOLD)  
            output_win.addstr(2, 1, prompt_text)  
            output_win.refresh()
            text_buffer = []  

        
        if text:
            text_buffer.append(f"{prompt_text}{text}")  
            output_win.clear()  
            output_win.box()  
            output_win.addstr(1, middle_x - 6,  "OUTPUT", curses.A_BOLD)  
            for i, line in enumerate(text_buffer[-(height - 9):]):  
                output_win.addstr(i + 3, 1, line)  
            output_win.refresh()

        modify_win.clear()
        modify_win.box()
        modify_win.addstr(1, 20, "COMMANDS", curses.A_BOLD)
        stdscr.refresh()
        modify_win.refresh()

        edit_win.move(0, 0)  
        stdscr.refresh()
        modify_win.refresh()



def search(stdscr):
    curses.curs_set(0)  
    stdscr.clear()

    
    curses.start_color()

    stdscr.addstr(0, 37, "SEARCH", curses.A_BOLD | Y_B)
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
            break

        draw_menu()

    curses.flushinp()    

def CLI(stdscr):
    #loadingScreen(stdscr)
    startSettings(stdscr)
    endSettings(stdscr)

wrapper(CLI) # asa trebuie apelat pt debugging daca sunt erori
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time

# o sa mai fac curat

def startSettings():
    stdscr = curses.initscr()
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    height, width = stdscr.getmaxyx()
    middle_y = height // 2
    middle_x = width // 2
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    G_B = curses.color_pair(1)
    Y_B = curses.color_pair(2)
    M = curses.color_pair(10)
    return stdscr, G_B, Y_B, M, middle_x, middle_y

def endSettings(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()

def searchAndBrowse(stdscr, G_B, Y_B, M, middle_x, middle_y):
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
        {"name": "commands", "coords": (9, 25, 15, 50), "label": "COMMANDS"},  
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
                search(stdscr, G_B, Y_B, M, middle_x, middle_y) 
            elif rectangles[current_index]["name"] == "commands":
                stdscr.attroff(curses.color_pair(1))
                stdscr.attroff(curses.color_pair(2))
                modify(stdscr, middle_x, middle_y)
            elif rectangles[current_index]["name"] == "browse":
                browse(stdscr, G_B, Y_B, M, middle_x, middle_y)
            stdscr.refresh()
            stdscr.getch()
        elif key == ord('q'):  
            endSettings(stdscr)
            break


def modify(stdscr, middle_x, middle_y):
    stdscr.clear()
    curses.curs_set(1)

    height, width = stdscr.getmaxyx()

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
        modify_win.addstr(1, 19, "COMMANDS", curses.A_BOLD)
        stdscr.refresh()
        modify_win.refresh()

        edit_win.move(0, 0)  
        stdscr.refresh()
        modify_win.refresh()

def search(stdscr, G_B, Y_B, M, middle_x, middle_y):
    curses.curs_set(0)  
    stdscr.clear()

    
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
            break

        draw_menu()

    curses.flushinp()    

def window_text(window, G_B):

    window.addstr(1,2, '> AF_id :', curses.A_BOLD | G_B)
    window.addstr(2,2, '> IP :', curses.A_BOLD | G_B)
    window.addstr(3,2, '> Subnet : ', curses.A_BOLD | G_B)
    window.addstr(4,2, '> NextHop : ', curses.A_BOLD | G_B)
    window.addstr(5,2 ,'> Metrica : ', curses.A_BOLD | G_B)
    window.addstr(6,2, '> TimeOut : ', curses.A_BOLD | G_B)
    window.addstr(7,2, '> Garbage : ', curses.A_BOLD | G_B)
    window.addstr(8,2, '> Flags : ', curses.A_BOLD | G_B)


def parseText():
    
    af = []
    ip = []
    subnet = []
    nexthop = []
    metric = []
    routeTag = []

    with open("demo.txt", "r") as file:
        for line in file:
            line = line.strip() 
            if line.startswith("AF_id:"):
                af.append(line.split(":", 1)[1].strip())
            elif line.startswith("IP:"):
                ip.append(line.split(":", 1)[1].strip())
            elif line.startswith("Subnet:"):
                subnet.append(line.split(":", 1)[1].strip())
            elif line.startswith("NextHop:"):
                nexthop.append(line.split(":", 1)[1].strip())
            elif line.startswith("Metric:"):
                metric.append(line.split(":", 1)[1].strip())
            elif line.startswith("Route Tag:"):
                routeTag.append(line.split(":", 1)[1].strip())
    
    return {
        "AF_id": af,
        "IP": ip,
        "Subnet": subnet,
        "NextHop": nexthop,
        "Metric": metric,
        "Route Tag": routeTag
    }
          
def browse(stdscr, G_B, Y_B, M, middle_x, middle_y):
    curses.curs_set(0)  
    stdscr.clear()
    curses.start_color()

    parsed_data = parseText()

    winArr = []


    win1 = curses.newwin(10, 38, 3, 1)
    winArr.append(win1)
    win2 = curses.newwin(10, 38, 3, 41)
    winArr.append(win2)
    win3 = curses.newwin(10, 38, 14, 1)
    winArr.append(win3)
    win4 = curses.newwin(10, 38, 14, 41)
    winArr.append(win4)
    
    for i, window in enumerate(winArr):
        window.box()
        window_text(window, G_B)

        if i < len(parsed_data["AF_id"]):
            af_id = parsed_data["AF_id"][i]
            ip = parsed_data["IP"][i]
            subnet = parsed_data["Subnet"][i]
            nexthop = parsed_data["NextHop"][i]
            metric = parsed_data["Metric"][i]
            route_tag = parsed_data["Route Tag"][i]

            window.addstr(1, 20, af_id, M | curses.A_BOLD)
            window.addstr(2, 20, ip, M | curses.A_BOLD)
            window.addstr(3, 20, subnet, M | curses.A_BOLD)
            window.addstr(4, 20, nexthop, M | curses.A_BOLD)
            window.addstr(5, 20, metric, M | curses.A_BOLD)
            window.addstr(6, 20, route_tag, M | curses.A_BOLD)

    stdscr.refresh()    
    for win in winArr:
        win.refresh()
    
    stdscr.addstr(0, 37, "BROWSE", curses.A_BOLD | curses.A_REVERSE | Y_B)
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
def CLI(stdscr):
    #loadingScreen(stdscr)
    stdscr, G_B, Y_B, M, middle_x, middle_y = startSettings()
    searchAndBrowse(stdscr, G_B, Y_B, M, middle_x, middle_y)

wrapper(CLI)
__author__ = 'jeremiahd'

import curses
import redis
import argparse
import sys
import datetime

DEFAULT_TEXT = 0
GREEN_TEXT = 1
RED_TEXT = 2


class RedisList:
    def __init__(self, display_name, key_name):
        self.display_name = display_name
        self.key_name = key_name
        self.size = 0
        self.last_updated = None

    def __str__(self):
        return '{}:{}'.format(self.key_name, self.display_name)


# cmdline args
parser = argparse.ArgumentParser(description='monitor redis lists and clients.', add_help=False)
parser.add_argument('file', metavar='FILENAME', type=argparse.FileType('r'), default=sys.stdin,
                    help='filename with lists to monitor (one per line)')
parser.add_argument('-H', '--help', action='help', help='show this help message and exit')
parser.add_argument('-h', '--host', metavar='HOST', type=str, default='localhost', dest='host', help='redis hostname')
parser.add_argument('-p', '--port', metavar='PORT', type=int, default=6379, dest='port', help='redis port')
parser.add_argument('-d', '--database', metavar='DB', type=int, default=0, dest='db', help='redis database')

args = parser.parse_args()

# load list from file
rlists = []
for line in args.file:
    rlists.append(RedisList(str(line).strip(), str(line).strip()))

# redis
r = redis.StrictRedis(host=args.host, port=args.port, db=args.db)

# ui settings
list_name_col_width = max(max([len(l.display_name) for l in rlists]) + 4, 12)
list_size_col_width = 8
list_changed_col_width = 12

clients_id_col_width = 4
clients_addr_col_width = 20
clients_cmd_col_width = 8
clients_idle_col_width = 8


def main(screen):
    # init curses
    curses.noecho()
    curses.cbreak()
    curses.use_default_colors()
    curses.curs_set(0)

    # init colors
    curses.init_pair(GREEN_TEXT, curses.COLOR_GREEN, -1)
    curses.init_pair(RED_TEXT, curses.COLOR_RED, -1)

    # init default screen
    height, width = screen.getmaxyx()
    screen.addstr(0, 0, "Mode: list monitoring")
    refresh_func = show_list_screen

    while True:
        screen.nodelay(True)

        c = screen.getch()

        if c == ord('q'):
            sys.exit(0)
        elif c == ord('l'):
            screen.clear()
            screen.addstr(0, 0, "Mode: list monitoring")
            screen.clrtoeol()
            refresh_func = show_list_screen
        elif c == ord('c'):
            screen.clear()
            screen.addstr(0, 0, "Mode: client monitoring")
            screen.clrtoeol()
            refresh_func = show_client_screen

        screen.addstr(height - 1, 0, "q - quit, l - monitor lists, c - monitor clients")
        refresh_func(screen)
        screen.move(height - 1, 0)
        screen.refresh()


def show_client_screen(screen):
    screen.addstr(2, 0, "ID".ljust(clients_id_col_width) + "ADDRESS".ljust(clients_addr_col_width) +
                  "CMD".ljust(clients_cmd_col_width) + "IDLE".ljust(clients_idle_col_width))
    row = 3
    for c in r.client_list():
        idle = str(datetime.timedelta(seconds=int(c['idle']))).split('.', 2)[0]

        screen.addstr(row, 0, str(c['id']))
        screen.addstr(row, clients_id_col_width, str(c['addr']))
        screen.clrtoeol()

        screen.addstr(row, clients_id_col_width + clients_addr_col_width, str(c['cmd']))
        screen.clrtoeol()

        screen.addstr(row, clients_id_col_width + clients_addr_col_width + clients_idle_col_width, idle)
        screen.clrtoeol()

        row += 1


def show_list_screen(screen):
    height, width = screen.getmaxyx()
    current_time = datetime.datetime.now()
    # row header
    screen.addstr(2, 0, "LIST".ljust(list_name_col_width) + "SIZE".ljust(list_size_col_width) + "IDLE".ljust(
        list_changed_col_width))

    # rows
    row = 3
    for l in rlists:

        if l.last_updated is None:
            l.last_updated = current_time

        current_size = r.llen(l.key_name)

        if current_size > l.size:
            l.last_updated = current_time
            color = GREEN_TEXT
        elif current_size < l.size:
            l.last_updated = current_time
            color = RED_TEXT
        else:
            color = DEFAULT_TEXT

        l.size = current_size
        idle = str(current_time - l.last_updated).split('.', 2)[0]

        screen.addstr(row, 0, l.display_name)
        screen.addstr(row, list_name_col_width, str(l.size), curses.color_pair(color))
        screen.clrtoeol()

        screen.addstr(row, list_name_col_width + list_size_col_width, idle, curses.color_pair(color))
        screen.clrtoeol()

        column = list_name_col_width + list_size_col_width + list_changed_col_width
        display_line = "*" * l.size if column + l.size < width else "*" * (width - column)
        screen.addstr(row, column, display_line, curses.color_pair(color))
        screen.clrtoeol()

        row += 1


curses.wrapper(main)

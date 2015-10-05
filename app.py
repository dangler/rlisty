from time import sleep
import curses
import redis
import argparse
import sys

DEFAULT_TEXT = 0
GREEN_TEXT = 1
RED_TEXT = 2


class RedisList:
    def __init__(self, display_name, key_name):
        self.display_name = display_name
        self.key_name = key_name
        self.size = 0
        self.last_update = None

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
col1_width = max(max([len(l.display_name) for l in rlists]) + 4, 12)
col2_width = 8


def main(screen):
    curses.noecho()
    curses.cbreak()
    curses.use_default_colors()

    curses.init_pair(GREEN_TEXT, curses.COLOR_GREEN, -1)
    curses.init_pair(RED_TEXT, curses.COLOR_RED, -1)

    # header
    screen.addstr(0, 0, "Mode: monitor list")

    while True:
        sleep(2)

        height, width = screen.getmaxyx()

        # row header
        screen.addstr(2, 0, "LIST".ljust(col1_width) + "SIZE".ljust(col2_width))

        # rows
        row = 3
        color = 0
        for l in rlists:
            current_size = r.llen(l.key_name)
            if current_size > l.size:
                color = GREEN_TEXT
            elif current_size < l.size:
                color = RED_TEXT
            else:
                color = DEFAULT_TEXT

            l.size = current_size

            screen.addstr(row, 0, l.display_name.ljust(col1_width))
            screen.addstr(row, col1_width, str(l.size), curses.color_pair(color))
            screen.addstr(row, col1_width + col2_width, "*" * l.size + " " * (l.size - current_size),
                          curses.color_pair(color))

            row += 1

        screen.addstr(height-1, 0, str(color))
        screen.move(row, 0)
        screen.refresh()

curses.wrapper(main)

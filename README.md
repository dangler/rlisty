# rlisty

## Description

rlisty is interactive terminal application built for Redis to monitor a set of lists/queues and clients

## Installation

```
pip install git+https://github.com/dangler/ally.git
```

## Usage

```
usage: rlisty [-H] [-h HOST] [-p PORT] [-d DB] FILENAME

monitor redis lists and clients.

positional arguments:
  FILENAME              filename with lists to monitor (one per line)

optional arguments:
  -H, --help            show this help message and exit
  -h HOST, --host HOST  redis hostname (default: localhost
  -p PORT, --port PORT  redis port (default: port)
  -d DB, --database DB  redis database (default: 0)

when running, commands are: q - quit, l - monitor lists, c - monitor clients
  ```

### Monitoring lists/queues

![Monitoring lists/queues](/docs/lists.png?raw=true "Monitoring lists/queues")

### Monitoring clients

![Monitoring clients](/docs/clients.png?raw=true "Monitoring clients")
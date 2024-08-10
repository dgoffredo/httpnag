
import argparse
import socket as net
import sqlite3
import sys
import time
import traceback


class Log:
    def __init__(self):
        self.enabled = False

    def __call__(self, *args, **kwargs):
        if self.enabled:
            kwargs['file'] = kwargs.get('file', sys.stderr)
            return print(*args, **kwargs)


log = Log()


class Sql:
    INSERT_AN_ERROR = """
insert into Errors(StartingWhenEpochSeconds,  DurationSeconds,  MessageId)
values(
  :startingWhenEpochSeconds,
  :durationSeconds,
  (select Id from ErrorMessages where Message = :message));"""

    INSERT_AN_ERROR_MESSAGE = """
insert or ignore into ErrorMessages(Message)
                             values(:message);"""

    INSERT_A_RESPONSE = """
insert into Responses(StartingWhenEpochSeconds,  DurationSeconds,  ResponseSizeBytes)
               values(:startingWhenEpochSeconds, :durationSeconds, :responseSizeBytes);"""

    CREATE_TABLES = """
create table if not exists ErrorMessages(
    Id integer primary key not null,
    Message text not null,
    unique (Message)
);

create table if not exists Errors(
    StartingWhenEpochSeconds real not null,
    DurationSeconds          real not null,
    MessageId                integer not null,
    foreign key (MessageId) references ErrorMessages(Id));

create table if not exists Responses(
    StartingWhenEpochSeconds real not null,
    DurationSeconds          real not null,
    ResponseSizeBytes        integer not null);
"""


def recv_until(sock, terminator, bufsize=1024*8):
    data = b''
    while True:
        data += sock.recv(bufsize)
        index = data.rfind(terminator)
        if index != -1:
            return data[:index + len(terminator)]


def http_head(address, port):
    log('Creating socket.')
    with net.socket() as sock:
        sock.settimeout(2) # seconds
        log(f'Connecting to {address}:{port}.')
        sock.connect((address, port))
        log('Sending payload.')
        sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
        log('Receiving response.')
        return recv_until(sock, b'\r\n\r\n')


def http_nag(address, port, db):
    response = None
    after = None
    before = time.time()
    try:
        response = http_head(address, port)
        after = time.time()
    except Exception:
        after = time.time()
        message = traceback.format_exc()
        log(message)
        db.execute(Sql.INSERT_AN_ERROR_MESSAGE, {
            'message': message
        })
        db.execute(Sql.INSERT_AN_ERROR, {
            'startingWhenEpochSeconds': before,
            'durationSeconds': after - before,
            'message': message
        })
        db.commit()
        return

    log(f'Received response: {repr(response)}.')

    db.execute(Sql.INSERT_A_RESPONSE, {
        'startingWhenEpochSeconds': before,
        'durationSeconds': after - before,
        'responseSizeBytes': len(response)
    })
    db.commit()


def open_database(path):
    db = sqlite3.connect(path)
    db.executescript(Sql.CREATE_TABLES)
    db.commit()
    return db


def nag_loop(address, port, db, sleep_seconds):
    while True:
        http_nag(address, port, db)
        log(f'About to sleep for {sleep_seconds} seconds.')
        time.sleep(sleep_seconds)


def parse_command_line(args):
    parser = argparse.ArgumentParser(description='Nag an HTTP endpoint.')

    parser.add_argument('--database_path', type=str, default='httpnag.sqlite',
                        help='path to database file (created if nonexistent)')
    parser.add_argument('--address', type=str, default='74.68.159.94',
                        help='IP address of target host')
    parser.add_argument('--port', type=int, default=80,
                        help='TCP port of target server')
    parser.add_argument('--sleep_seconds', type=float, default=5,
                        help='duration, in seconds, between requests')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='log activity to standard error')

    return parser.parse_args()


def main():
    options = parse_command_line(sys.argv[1:])
    log.enabled = options.verbose
    db = open_database(options.database_path)
    try:
        nag_loop(options.address,
                 options.port,
                 db,
                 options.sleep_seconds)
    except KeyboardInterrupt:
        pass # parent process (e.g. command shell) wants us to go away
    

if __name__ == '__main__':
    main()

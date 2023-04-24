import argparse
import logging
from pathlib import Path
import appdirs
import contextlib
import os
import asyncio
from enum import Enum
from .env import History, TextCursor, VarEnv
import signal
import termios
import sys
from typing import Optional
from .load import command_executor, command_loader
from .env import logger
term = termios.tcgetattr(sys.stdin.fileno())


class Arrow(Enum):
    UP = 'A'
    DOWN = 'B'
    RIGHT = 'C'
    LEFT = 'D'

    @classmethod
    def by_alpha(cls, alpha: str):
        for v in cls.__members__.values():
            if v.value == alpha:
                return v
        raise KeyError()


class CMD:
    def __init__(
        self,
        history: History,
        env: VarEnv,
        hostname: str = 'relix',
) -> None:
        self.text: TextCursor = TextCursor()
        self.env = env
        self.env['cwd'] = os.getcwd()
        self.hostname = f'{os.getlogin()}@{hostname}: '
        self.history = history
        self.width_terminal = os.get_terminal_size().columns
        signal.signal(signal.SIGWINCH, self.terminal_change)

    def terminal_change(self, *args, **kwargs):
        self.width_terminal = os.get_terminal_size().columns
        self.display('', from_prompt=True)

    def history_by_arrow(self, key: Arrow):
        if key in [Arrow.UP, Arrow.DOWN]:
            self.text.text = (
                self.history.prev() if key == Arrow.UP else self.history.next()
            )
        elif self.text and key in [Arrow.LEFT, Arrow.RIGHT]:
            if key == Arrow.LEFT:
                self.text.back()
            elif key == Arrow.RIGHT:
                self.text.next()

    async def write(self, text: str):
        self.text.add_char(text)

    def display(self, text: Optional[str] = None, from_prompt=False):
        if from_prompt:
            text = self.hostname + (
                text or self.text.printable()
            )
            sys.stdout.write(
                '\r' +
                text +
                ' '*(self.width_terminal - text.__len__())
            )
            sys.stdout.write('\r')
        else:
            sys.stdout.write(
                '\r' +
                (text or self.text.text) +
                ' '*(self.width_terminal - self.text.text.__len__())
            )
            sys.stdout.write('\r')
        sys.stdout.flush()

    async def on_backspace(self):
        self.text.backspace()

    async def on_arrow(self):
        pass

    async def execute(self, text: str):
        await command_executor(
            text,
            env_set=self.env.set,
            env_get=self.env.get,
            display=self.display,
        )

    async def on_enter(self):
        self.display(
            self.text.text +
            ' '*(
                self.width_terminal - self.history.current_history().__len__()
            ),
            from_prompt=True
        )
        self.history.add_history(self.text.text)
        if self.text.text in ['exit', 'q']:
            self.history.dump_history()
            term[3] &= termios.ECHO | termios.ECHOCTL | termios.BRKINT
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, term)
            sys.exit(0)
        await self.execute(self.text.text)
        self.text.clear()

    @contextlib.contextmanager
    def raw_mode(self, file):
        old_attrs = termios.tcgetattr(file.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        try:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
            yield
        finally:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)

    async def start(self):
        try:
            with self.raw_mode(sys.stdin):
                k = ''
                while True:
                    if k == '\x1b':
                        k2 = sys.stdin.read(1)
                        if k2 == '[':
                            self.history_by_arrow(
                                Arrow.by_alpha(
                                    sys.stdin.read(1)
                                )
                            )
                    elif k == '\n':
                        try:
                            await self.on_enter()
                        except KeyboardInterrupt as e:
                            self.display(e.__str__())
                            self.text.clear()
                            raise e
                    elif k == '\x7f':
                        await self.on_backspace()
                    else:
                        self.text.add_char(k)
                    self.display(from_prompt=True)
                    try:
                        k = sys.stdin.read(1)
                    except KeyboardInterrupt:
                        sys.exit(1)
        except Exception as e:
            self.display(e.__str__())
            sys.exit(1)


async def interactive():
    await init()


async def init():
    args = argparse.ArgumentParser('relix')
    args.add_argument(
        '-l', help='libraries',
        type=str
    )
    args.add_argument(
        '--hostname',
        help='hostname',
        type=str,
        default='relix'
    )
    args.add_argument(
        '-v',
        help='verbose',
        action='store_const',
        const=logging.DEBUG,
        default=logging.INFO,
        dest='level'
    )
    args.add_argument(
        '-t',
        help='Test All Files',
        action='store_true',
        dest='test'
    )
    parse = args.parse_args()
    logger.setLevel(parse.level)
    if parse.l:
        command_loader(Path(parse.l).absolute())
    full_path = Path(appdirs.user_config_dir('relix'))
    if not full_path.exists():
        os.mkdir(full_path)
    history = History(full_path/'.history')
    history.load_history()
    cmd = CMD(
        history,
        VarEnv.initialize()
    )
    libraries = full_path / 'libraries/command'
    if not libraries.exists():
        os.mkdir(libraries)
    command_loader(libraries)
    if not parse.test:
        await cmd.start()


loop = asyncio.new_event_loop()
loop.run_until_complete(interactive())

from __future__ import annotations
from typing import Optional
import relix
from dataclasses import dataclass
from pathlib import Path
import secrets
from text_password_protect import TextPasswordProtect
import pickle
from colorama import ansi
import logging


logger = logging.getLogger('relix')
logging.basicConfig(format='%(asctime)s  %(message)s', level=logging.INFO)
logger.setLevel(logging.DEBUG)


class TextCursor(object):
    def __init__(self, char_bg: str = ansi.Back.LIGHTGREEN_EX):
        self.__text = ' '
        self.char_bg = char_bg
        self.__position = self.__text.__len__() - 1

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, pos: int):
        if isinstance(pos, int) and pos > -1:
            self.__position = pos
        else:
            raise ValueError()

    @property
    def text(self):
        return self.__text[:-1]

    @text.setter
    def text(self, text_: str):
        self.__text = text_ + ' '
        self.position = self.__text.__len__() - 1

    def printable(self):
        return (
            self.__text[:self.position] +
            self.char_bg +
            self.__text[self.position] +
            ansi.Back.RESET +
            self.__text[self.position+1:]
        )

    def end(self):
        self.position = self.__text.__len__() - 1

    def back(self):
        if self.position > 0:
            self.position -= 1

    def next(self):
        if self.position < self.__text.__len__() - 1:
            self.position += 1

    def add_char(self, char: str):
        self.__text = (
            self.__text[:self.position] +
            char +
            self.__text[self.position:]
        )
        self.position += char.__len__()

    def clear(self):
        self.__text = ' '
        self.position = self.__text.__len__() - 1

    def backspace(self):
        if self.position > 0:
            self.position -= 1
            self.__text = (
                self.__text[:self.position] +
                self.__text[self.position+1:]
            )


class History(list):
    def __init__(self, file: Optional[Path] = None):
        self.append('')
        self.file = file
        self.__position = 0

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, pos: int):
        if isinstance(pos, int) and pos > -1:
            self.__position = pos
        else:
            raise ValueError()

    def len(self):
        return self.__len__() - 1

    def prev(self) -> str:
        if not (self.position < 1):
            self.position -= 1
        return self[self.position]

    def end(self):
        self.position = self.len()
        return self[self.position - 1]

    def next(self):
        if self.position < self.__len__()-1:
            self.position += 1
        return self[self.position]

    def add_history(self, text: str):
        if (not (self[self.position - 1] == text)) or text:
            self[-1] = text
            self.append('')
        return self.end()

    def current_history(self):
        return self[self.position - 1]

    def load_history(self):
        if self.file and self.file.exists():
            with open(self.file, 'rb') as file:
                self.clear()
                self.extend(pickle.load(file))
                self.append('')
                self.position = self.__len__() - 1

    def dump_history(self):
        if self.file:
            for i in range(self.count('')):
                self.remove('')
            with open(self.file, 'wb') as file:
                pickle.dump(self, file)


@dataclass
class VarEnv(dict):
    RELIX_SALT: bytes
    VERSION: str
    FILENAME = '.env.pickle'

    def __post_init__(self):
        self.ncdc = TextPasswordProtect(self.RELIX_SALT)

    def set(self, key: str, val: str, password: Optional[str] = None):
        self.update({
            key: self.ncdc.encrypt(
                val,
                password
            ) if password else val
        })

    def get(self, key: str, password: Optional[str] = None) -> str | None:
        get = super().get(key)
        if get:
            if password:
                return self.ncdc.decrypt(get, password)
            return get

    @classmethod
    def initialize(cls):
        return cls(
            RELIX_SALT=secrets.token_bytes(16),
            VERSION=getattr(
                relix,
                '__version__'
            ) if hasattr(relix, 'VERSION') else '0.0.0'
        )


@dataclass
class Settings:
    RELIX_SALT: bytes
    VERSION: str

    def load_from_file(self, path: Path) -> Settings:
        with open(path, 'rb') as file:
            return pickle.load(file)

    def dump(self, path):
        with open(path, 'wb') as file:
            return pickle.dump(self, file)

    @classmethod
    def initialize(cls):
        return cls(
            RELIX_SALT=secrets.token_bytes(16),
            VERSION=getattr(
                relix,
                '__version__'
            ) if hasattr(relix, 'VERSION') else '0.0.0'
        )

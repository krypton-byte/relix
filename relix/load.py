import sys
import pathlib
import shlex
import os
from typing import Callable, List, Type
from .command.cmd import BaseCommand, display_func
from .env import logger


def nested_mkdir(path: pathlib.Path):
    parts = path.parts
    for i in range(1, parts.__len__() + 1):
        xpath = pathlib.Path().joinpath('/'.join(parts[:i]))
        if xpath.exists():
            if xpath.is_file():
                os.remove(xpath)
                os.mkdir(xpath)
        else:
            os.mkdir(xpath)
            logger.debug(f'create {path.__str__()} dir')


COMMAND: List[Type[BaseCommand]] = []


def command_loader(path: pathlib.Path):
    logger.debug(f'Load Library From {path.parent.name}/{path.name}')
    before = COMMAND.__len__()
    sys.path.insert(0, path.parent.parent.__str__())
    for directory in path.iterdir():
        if directory.__str__()[-3:] == '.py':
            file = directory.__str__().split('/')[-1][:-3]
            mod = getattr(getattr(__import__(f'{path.parent.name}.{path.name}.{file}'), path.name), file)
            for obj in dir(mod):
                if hasattr(
                    getattr(mod, obj),
                    '__bases__'
                ) and BaseCommand in getattr(mod, obj).__bases__:
                    fmod: Type[BaseCommand] = getattr(mod, obj)
                    if fmod not in COMMAND:
                        COMMAND.append(fmod)
    logger.debug(
        (COMMAND.__len__() - before).__str__() +
        ' COMMAND LOADED'
    )


command_loader(pathlib.Path(__file__).parent / 'command')


async def command_executor(
    shell: str,
    env_set: Callable[[str, str, str], None],
    env_get: Callable[[str, str], str | None],
    display=display_func,
):
    shell_parse = shlex.split(shell)
    if shell_parse:
        for __cmd in COMMAND:
            if __cmd.alias == shell_parse[0]:
                cmd_ = __cmd(
                    cmd=shell,
                    display=display,
                    env_set=env_set,
                    env_get=env_get
                )
                try:
                    await cmd_.execute()
                except Exception as e:
                    print('error:', e)
                    display(cmd_.help)
                

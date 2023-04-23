import pathlib
import shlex
from typing import Callable, List, Type
from .command.cmd import BaseCommand, display_func
from .env import logger


def import_nested(obj: object, dir: List[str]):
    return import_nested(getattr(obj, dir[0]), dir[1:])


COMMAND: List[Type[BaseCommand]] = []


def command_loader(name: str):
    for directory in (pathlib.Path(__file__).parent / 'command').iterdir():
        if directory.__str__()[-3:] == '.py':
            file = directory.__str__().split('/')[-1][:-3]
            mod = getattr(__import__(f'{name}.command.{file}').command, file)
            for obj in dir(mod):
                if hasattr(
                    getattr(mod, obj),
                    '__bases__'
                ) and BaseCommand in getattr(mod, obj).__bases__:
                    fmod: Type[BaseCommand] = getattr(mod, obj)
                    if fmod not in COMMAND:
                        COMMAND.append(fmod)


command_loader('relix')
logger.debug(
    COMMAND.__len__().__str__() +
    ' COMMAND LOADED'
)


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
                

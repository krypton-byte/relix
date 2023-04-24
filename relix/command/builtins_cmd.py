from pathlib import Path
import shlex
from .cmd import BaseCommand


class ExportEnv(BaseCommand):
    alias = 'export'

    @property
    def help(self) -> str:
        return 'export <name: str>=<value: str>'

    async def execute(self):
        cmd = shlex.split(self.cmd)
        if cmd[1:] and cmd[1].count('=') == 1:
            self.env_set(*cmd[1].split('='))
        else:
            self.display(self.help)


class Pwd(BaseCommand):
    alias = 'pwd'

    @property
    def help(self) -> str:
        return ''

    async def execute(self):
        self.display(self.env_get('cwd'))


class ChangeDirectory(BaseCommand):
    alias = 'cd'

    @property
    def help(self) -> str:
        return 'cd <dirname>'

    async def execute(self):
        lex = shlex.split(self.cmd)
        if lex.__len__() > 1:
            if lex[1] == '..':
                dirs = Path(self.env_get('cwd')).parent
            else:
                dirs = Path(self.env_get('cwd')) / lex[1]
            if dirs.exists():
                if dirs.is_file():
                    self.display(
                        f'relix: cd: {lex[1]}: Not a directory'
                    )
                else:
                    self.env_set('cwd', dirs.__str__())
            else:
                self.display(
                    f'relix: cd: {lex[1]}: No such file or directory'
                )
        else:
            self.display(self.help)


class ListDirectories(BaseCommand):
    alias = 'ls'

    @property
    def help(self) -> str:
        return ''

    async def execute(self):
        args = shlex.split(self.cmd)
        if args.__len__() > 1:
            if Path(args[1]).exists():
                if Path(args[1]).is_dir():
                    for i in Path(args[1]).iterdir():
                        self.display(i)
                else:
                    self.display(args[1])
            else:
                self.display(
                    'ls: cannot access \'%s\': '
                    'No such file or directory' % args[1])
        else:
            for i in Path(self.env_get('cwd')).iterdir():
                self.display(i.name)

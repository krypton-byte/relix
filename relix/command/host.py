import argparse
from dataclasses import dataclass
import inspect
import ping3
import shlex
from .cmd import BaseCommand
import socket


@dataclass
class GetHostByName(BaseCommand):
    cmd: str
    alias = 'gethost'

    @property
    def help(self):
        return self.alias + ' <hostname|ex: api.myip.com>'

    async def execute(self):
        self.display(socket.gethostbyname(shlex.split(self.cmd)[1]) + '\n')


@dataclass
class Ping(BaseCommand):
    alias = 'ping'

    @property
    def help(self):
        return self.alias + ' <hostname>'

    async def execute(self):
        arg = argparse.ArgumentParser(prog=self.alias, exit_on_error=False)
        try:
            for key, v in dict(inspect.signature(ping3.ping)._parameters).items():
                key = key.replace('_', '-')
                arg.add_argument(f'--{key}', type=v.annotation, required=v.default is inspect._empty, default=v.default)
            n_cmd = shlex.split(self.cmd)[1:]
            parsed = arg.parse_args(n_cmd)
            self.display(ping3.ping(
                **{k: getattr(parsed, k) for k, v in dict(inspect.signature(ping3.ping)._parameters).items() if getattr(parsed, k) is not inspect._empty}
            ))
        except SystemExit:
            self.display(arg.format_help())
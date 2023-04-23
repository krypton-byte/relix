from dataclasses import dataclass
from .cmd import BaseCommand
import httpx


@dataclass
class ExpiredAttack(BaseCommand):
    alias: str = 'my_ip'

    @property
    def help(self) -> str:
        return ''

    async def execute(self):
        async with httpx.AsyncClient() as ahttp:
            resp = await ahttp.get('http://ip-api.com/json/')
            self.display(resp.json()['query'])

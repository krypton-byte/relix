from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Callable, Coroutine, Optional


def display_func(
    text: Optional[str] = None,
    from_prompt: bool = False
) -> None:
    raise NotImplementedError()


@dataclass
class BaseCommand(ABC):
    cmd: str
    env_get: Callable
    env_set: Callable
    alias: str = ''
    display: Callable = display_func,

    @abstractproperty
    def help(self) -> str:
        ...

    @abstractmethod
    def execute(self) -> Coroutine:
        ...

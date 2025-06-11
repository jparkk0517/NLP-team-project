from typing import TypeVar, Type

T = TypeVar("T", bound="Singleton")


class Singleton:
    __instances = {}

    def __new__(cls: Type[T], *args, **kwargs) -> T:
        if cls not in cls.__instances:
            instance = super().__new__(cls)
            cls.__instances[cls] = instance
        return cls.__instances[cls]

    @classmethod
    def get_instance(cls: Type[T], **kwargs) -> T:
        if cls not in cls.__instances:
            cls.__instances[cls] = cls(**kwargs)
        return cls.__instances[cls]

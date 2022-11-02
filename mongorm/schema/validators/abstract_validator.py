from abc import ABC, abstractmethod
from typing import Union, Callable


class AbstractValidator(ABC):
    def __init__(self, error_message: Union[str, Callable] = None):
        self.__error_message: Union[str, Callable] = error_message

    @abstractmethod
    def is_valid(self, value, field_key: str, model) -> bool:
        pass

    def get_error_message(self) -> Union[str, None]:
        if self.__error_message:
            if callable(self.__error_message):
                return self.__error_message()
            return self.__error_message

        return None

__all__ = ['NumberRangeValidator']
from typing import Optional, Callable, Union
from mongorm.schema.validators.abstract_validator import AbstractValidator


class NumberRangeValidator(AbstractValidator):
    def __get_error_message(self) -> str:
        out = ''
        if self.__min_value is not None:
            out += 'Min value' + ': ' + str(self.__min_value)
        if self.__max_value is not None:
            if out:
                out += ' '
            out += 'Max value' + ': ' + str(self.__max_value)

        return out

    def __init__(self, error_message: Union[Callable, str] = None,
                 min_value: Optional[float] = None, max_value: Optional[float] = None):
        if not error_message:
            error_message = self.__get_error_message
        super().__init__(error_message)
        if min_value is None and max_value is None:
            raise ValueError('min_value or max_value must be exist')
        self.__min_value = min_value
        self.__max_value = max_value

    def is_valid(self, value, field_key: str, model) -> bool:
        if value is None:
            return True
        if self.__min_value and value < self.__min_value:
            return False
        if self.__max_value and value > self.__max_value:
            return False
        return True

__all__ = ['ValidationError', 'FieldValidationError']


class FieldValidationError(Exception):
    def __init__(self, message):
        self.__message = message

    @property
    def message(self):
        return self.__message


class ValidationError(Exception):
    def __init__(self, message=None, errors=None):
        if errors is None:
            errors = {}
        self.__message = message
        self.__errors = errors

    @property
    def message(self):
        return self.__message

    def add_error(self, field_key: str, message: str):
        self.__errors[field_key] = message

    @property
    def errors(self):
        return self.__errors

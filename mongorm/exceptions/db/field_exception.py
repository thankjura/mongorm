"""All model fields exceptions."""


class FieldException(Exception):

    def __init__(self, message: str = None):
        self.__message = message

    @property
    def message(self):
        return self.__message


class FieldRequiredException(FieldException):
    pass


class FieldValueException(FieldException):
    pass

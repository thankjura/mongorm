__all__ = ['EmailValidator']

import re
from mongorm.schema.validators.abstract_validator import AbstractValidator


email_regexp = re.compile(r'^([A-Za-z\d]+[.-_])*[A-Za-z\d]+@[A-Za-z\d-]+(\.[A-Z|a-z]{2,})')


class EmailValidator(AbstractValidator):
    def __init__(self, error_message=None):
        if not error_message:
            error_message = 'Bad email format'
        super().__init__(error_message)

    def is_valid(self, value, field_key: str, model) -> bool:
        if value:
            return bool(email_regexp.match(value))
        return False

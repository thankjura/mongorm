__all__ = ['RequiredValidator']

from mongorm.schema.validators.abstract_validator import AbstractValidator


class RequiredValidator(AbstractValidator):
    def is_valid(self, value, field_key: str, model) -> bool:
        return value or value == 0

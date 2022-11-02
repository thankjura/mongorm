__all__ = ['Schema']

import inspect
from typing import Set, Collection

from mongorm.exceptions.db.field_exception import FieldValueException
from mongorm.exceptions.validation_error import ValidationError
from mongorm.schema import fields
from mongorm.schema.abc_schema import AbcSchema
from mongorm.schema.proxy_object import ProxyObject


class Schema(AbcSchema):
    def __init__(self, document=None, extra_fields=None):
        super().__init__()
        self.__changed_fields: Set[str] = set()
        self.__extra_fields = extra_fields if extra_fields else {}
        self.__data = {}
        self._set_data(document)
        for k, f in self.FIELDS.items():
            if k in self.__data:
                continue
            value = f.default() if callable(f.default) else f.default
            if value is not None:
                self.__data[k] = f.loads(value)

    def __wrap_out(self, field_key, value):
        if isinstance(value, (set, list, dict)):
            return ProxyObject(value, lambda: self.__changed_fields.add(field_key))
        field = self.FIELDS.get(field_key)
        if isinstance(field, fields.Collection):
            self.__data[field_key] = []
            return ProxyObject(self.__data[field_key], lambda: self.__changed_fields.add(field_key))
        if isinstance(field, fields.DocumentField) and not field.schema:
            self.__data[field_key] = {}
            return ProxyObject(self.__data[field_key], lambda: self.__changed_fields.add(field_key))

        return value

    def get(self, field_key):
        if self.__data:
            out = self.__data.get(field_key)
            return self.__wrap_out(field_key, out)

        return self.__wrap_out(field_key, None)

    def set(self, field_key, value):
        field = self.FIELDS.get(field_key)
        if field and not field.no_loads:
            self.__data[field_key] = self.FIELDS[field_key].loads(value)
            self.__changed_fields.add(field_key)
        elif not field:
            self.__data[field_key] = value
            self.__changed_fields.add(field_key)

    def _set_data(self, document):
        self.__changed_fields.clear()
        if not document:
            self.__data = {}
        elif isinstance(document, Schema):
            self.__data = document._get_data()
        else:
            for k, v in document.items():
                field = self.FIELDS.get(k)
                if not field:
                    field = self.__extra_fields.get(k)
                if isinstance(field, fields.DocumentField) and field.schema and issubclass(field.schema, Schema):
                    self.__data[k] = field.schema(v)
                elif field:
                    self.__data[k] = field.loads(v)
                else:
                    self.__data[k] = v

    @classmethod
    def __get_data_value(cls, key, value, include: Collection[str] = None, exclude: Collection[str] = None):
        if isinstance(value, Schema):
            child_include = None
            child_exclude = None
            if include:
                child_include = [v.replace(f'{key}.', "", 1) for v in include if v.startswith(f'{key}.')]
            if exclude:
                child_exclude = [v.replace(f'{key}.', "", 1) for v in exclude if v.startswith(f'{key}.')]
            return value._get_data(child_include, child_exclude)
        elif isinstance(value, list):
            child_include = None
            child_exclude = None
            if include:
                child_include = [v.replace(f'{key}.$.', "", 1) for v in include if v.startswith(f'{key}.')]
            if exclude:
                child_exclude = [v.replace(f'{key}.$.', "", 1) for v in exclude if v.startswith(f'{key}.')]
            out_values = []
            for list_item in value:
                out_val = cls.__get_data_value(key, list_item, child_include, child_exclude)
                if out_val:
                    out_values.append(out_val)
            return out_values
        else:
            return value

    def _get_data(self, include: Collection[str] = None, exclude: Collection[str] = None):
        out = {}
        for k, v in self.__data.items():
            if include and k not in include:
                continue

            if exclude and k in exclude:
                continue

            out_val = self.__get_data_value(k, v, include, exclude)
            out[k] = out_val
        return out

    def _get_changes(self, exclude: list = None) -> dict:
        return self._get_data(include=self.__changed_fields, exclude=exclude)

    def has_changes(self):
        for k, v in self.__data.items():
            if isinstance(v, Schema) and v.has_changes():
                return True
        return len(self.__changed_fields) > 0

    async def validate(self, all_fields=True) -> dict:
        errors = {}

        for k, f in self.FIELDS.items():
            if all_fields or k in self._get_changes():
                value = self.get(k)
                for v in f.validators:
                    res = v.is_valid(value, k, self)
                    if inspect.isawaitable(res):
                        res = await res

                    if not res:
                        errors[k] = v.get_error_message()
                        break
                if isinstance(value, Schema):
                    child_errors = await value.validate()
                    for error_key, error_value in child_errors.items():
                        errors[f'{k}.{error_key}'] = error_value

                elif hasattr(f, 'doc_type') and hasattr(f.doc_type, 'validators') and f.doc_type.validators:
                    for val in value:
                        if errors.get(k):
                            break

                        for v in f.doc_type.validators:
                            res = v.is_valid(val, k, self)
                            if inspect.isawaitable(res):
                                res = await res

                            if not res:
                                errors[k] = v.get_error_message()
                                break

        return errors

    def load(self, data):
        error = ValidationError()
        for k, f in self.FIELDS.items():
            if k in data:
                try:
                    self.set(k, data.get(k))
                except FieldValueException as e:
                    error.add_error(k, e.message)

        if error.errors:
            raise error

        return self

    def __json__(self):
        out = {}
        for k, f in self.FIELDS.items():
            if f.no_dumps:
                continue
            value = self.get(k)
            out[k] = f.dumps(value)

        for k, f in self.__extra_fields.items():
            if f.no_dumps:
                continue
            out[k] = f.dumps(self.get(k))

        return out

    @property
    def __name__(self):
        return self.__class__.__name__

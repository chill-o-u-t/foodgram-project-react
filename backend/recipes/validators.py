import re

from django.core.exceptions import ValidationError

from backend.recipes.utils import (
    SYMBOLS_COLOR,
    SYMBOLS_TAG,
    SYMBOLS_USERNAME
)


class TagValidateMixin:
    def validate_slug(self, value):
        if not re.match(SYMBOLS_TAG, value):
            raise ValidationError(
                'Недопустимые символы в slug'
            )
        return value

    def validate_color(self, value):
        if not re.match(SYMBOLS_COLOR, value) or len(value) != 6:
            raise ValidationError(
                'Это не явдяется hex цветом'
            )
        return value


class UserValidateMixin:
    def validate_username(self, value):
        if not re.match(SYMBOLS_USERNAME, value):
            raise ValidationError(
                'Недопустимое имя пользователя!'
            )
        return value

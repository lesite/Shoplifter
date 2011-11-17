import decimal
from mongoengine import IntField


class MoneyField(IntField):
    """
    This is actually an integer field that stores the number of
    cents. This can be used when we need to store precise money
    amounts that cannot afford to lose precision.
    Pros: This supports database operations like sum
    """

    def __init__(
        self, min_value=None, max_value=None, decimal_digits=2, **kwargs):
        self.min_value, self.max_value, self.decimal_digits = \
            min_value, max_value, decimal_digits
        super(MoneyField, self).__init__(**kwargs)

    def aggregate_to_python(self, value):
        return self.to_python(value)

    def to_python(self, value):
        return decimal.Decimal(str(value)) / (10 ** self.decimal_digits)

    def to_mongo(self, value):
        return int(
            (value * (10 ** self.decimal_digits)).to_integral())

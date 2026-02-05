from rest_framework import serializers


class DisplayChoiceField(serializers.ChoiceField):
    """
    Returns the display value on GET,
    Accepts either the display value or the db value on input.
    """

    def to_representation(self, obj):
        return self.choices.get(obj, obj)

    def to_internal_value(self, data):
        if data in self.choices:
            return data

        for key, val in self.choices.items():
            if val.lower() == str(data).lower():
                return key

        self.fail('invalid_choice', input=data)

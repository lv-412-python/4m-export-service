"""Schema for export."""
from marshmallow import Schema, fields, validates, ValidationError


class ExportInputSchema(Schema):
    """Class for input schema."""
    form_id = fields.Int(required=True)
    groups = fields.List(fields.Int)
    export_format = fields.Str(required=True)

    @validates('export_format')
    def is_in_correct_format(self, value):  # pylint: disable=no-self-use
        """Check is export_format in correct type."""
        if value not in ('pdf', 'csv', 'xls'):
            raise ValidationError("Incorrect type.")

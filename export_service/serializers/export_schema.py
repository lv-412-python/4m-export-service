"""Schema for export."""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema


class ExportInputSchema(Schema):
    """Class for input schema."""
    form_id = fields.Int(required=True)
    groups = fields.List(fields.Int)
    export_format = fields.Str(required=True)
    from_date = fields.Date()
    to_date = fields.Date()

    @validates('export_format')
    def is_in_correct_format(self, value):
        """Check is export_format in correct type."""
        if value not in ('pdf', 'csv', 'xls'):
            raise ValidationError("Incorrect type.")

    @validates_schema
    def check_date(self, data):
        """Check is date range correct."""
        try:
            if data["from_date"] > data["to_date"]:
                raise ValidationError("Incorrect date range.")
        except KeyError:
            pass

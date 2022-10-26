"""Currently Validates the following:
    1. Field exists in the SF Object (excluding _sdc metadata)
    2. If the config action is update, that the field can be updated
    3. If the config action is insert, that the field can be created"""


from collections import namedtuple
from typing import Dict

from target_salesforce.utils.exceptions import InvalidStreamSchema

ObjectField = namedtuple("ObjectField", "type createable updateable")


def validate_schema_field(
    field: Dict, object_fields: Dict[str, ObjectField], action: str
):
    """Currently only validates that all incomming fields exist in the SF Object"""
    field_name, field_type = field
    sf_field: ObjectField = object_fields.get(field_name)

    if field_name.startswith("_sdc_"):
        return

    if not sf_field:
        raise InvalidStreamSchema(f"{field_name} does not exist in SF Object")

    if action == "update":
        if not sf_field.updateable and field_name != "Id":
            raise InvalidStreamSchema(
                f"{field_name} is not updatable for this SF Object, invalid for {action} action"
            )

    if action == "insert":
        if not sf_field.createable:
            raise InvalidStreamSchema(
                f"{field_name} is not creatable for this SF Object, invalid for {action} action"
            )

    if action in ["delete", "hard_delete"] and field_name != "Id":
        raise InvalidStreamSchema(
            f"Schema for the {action} action should only include Id"
        )


# TODO: Look into type validation, can quickly get complex with many possible restrictions in SF

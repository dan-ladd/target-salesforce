"""Salesforce target class."""

from singer_sdk.target_base import Target
from singer_sdk import typing as th

from target_salesforce.sinks import (
    SalesforceSink,
)


class TargetSalesforce(Target):
    """Sample target for Salesforce."""

    name = "target-salesforce"
    config_jsonschema = th.PropertiesList(
        th.Property("client_id", th.StringType),
        th.Property("client_secret", th.StringType, secret=True),
        th.Property("refresh_token", th.StringType, secret=True),
        th.Property("username", th.StringType),
        th.Property("password", th.StringType, secret=True),
        th.Property("security_token", th.StringType, secret=True),
        th.Property("is_sandbox", th.BooleanType, default=False),
        th.Property(
            "action",
            th.StringType,
            default="update",
            allowed_values=SalesforceSink.valid_actions,
        ),
    ).to_dict()
    default_sink_class = SalesforceSink

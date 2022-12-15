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
        th.Property(
            "client_id",
            th.StringType,
            description="OAuth client_id"
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,
            description="OAuth client_secret"
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            secret=True,
            description="OAuth refresh_token"
        ),
        th.Property(
            "username",
            th.StringType,
            description="User/password username"
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            description="User/password username"
        ),
        th.Property(
            "security_token",
            th.StringType,
            secret=True,
            description="User/password generated security token. Reset under your Account Settings"
        ),
        th.Property(
            "is_sandbox",
            th.BooleanType,
            default=False,
            description="Is the Salesforce instance a sandbox"
        ),
        th.Property(
            "action",
            th.StringType,
            default="update",
            allowed_values=SalesforceSink.valid_actions,
            description="How to handle incomming records by default (insert/update/delete/hard_delete)"
        ),
    ).to_dict()
    default_sink_class = SalesforceSink

"""Salesforce target sink class, which handles writing streams."""

import json
from typing import Dict, List, Optional
from dataclasses import asdict


from singer_sdk.sinks import BatchSink
from simple_salesforce import Salesforce, bulk, exceptions
from target_salesforce.session_credentials import parse_credentials, SalesforceAuth
from target_salesforce.utils.exceptions import InvalidStreamSchema
from singer_sdk.plugin_base import PluginBase
from target_salesforce.utils.validation import ObjectField
from target_salesforce.utils.transformation import transform_record

from target_salesforce.utils.validation import validate_schema_field


class SalesforceSink(BatchSink):
    """Salesforce target sink class."""

    max_size = 5000
    valid_actions = ["insert", "update", "delete", "hard_delete"]
    include_sdc_metadata_properties = False

    def __init__(
        self,
        target: PluginBase,
        stream_name: str,
        schema: Dict,
        key_properties: Optional[List[str]],
    ):
        super().__init__(target, stream_name, schema, key_properties)
        self.target = target
        self._sf_client = None
        self._batched_records: List[Dict]
        self._object_fields: Dict[str, ObjectField] = None
        self._validate_schema_against_object()

    @property
    def sf_client(self):
        if self._sf_client:
            return self._sf_client
        return self._new_session()

    @property
    def object_fields(self) -> Dict[str, ObjectField]:
        if self._object_fields:
            return self._object_fields
        object_fields = {}

        stream_object = getattr(self.sf_client, self.stream_name)
        for field in stream_object.describe().get("fields"):
            object_fields[field.get("name")] = ObjectField(
                field.get("type"),
                field.get("createable"),
                field.get("updateable"),
            )

        self._object_fields = object_fields
        return self._object_fields

    def _validate_schema_against_object(self):
        for field in self.schema.get("properties").items():
            try:
                validate_schema_field(
                    field, self.object_fields, self.config.get("action")
                )
            except InvalidStreamSchema as e:
                raise InvalidStreamSchema(
                    f"The incomming schema is incompatable with your {self.stream_name} object"
                ) from e

    def _new_session(self):
        session_creds = SalesforceAuth.from_credentials(
            parse_credentials(self.target.config),
            is_sandbox=self.target.config["is_sandbox"],
        ).login()
        self._sf_client = Salesforce(**asdict(session_creds))
        return self._sf_client

    def start_batch(self, context: dict) -> None:
        self.logger.info(f"Starting new batch")
        self._batched_records = []

    def process_record(self, record: dict, context: dict) -> None:
        """Transform and batch record"""

        processed_record = transform_record(record, self.object_fields)

        self._batched_records.append(processed_record)

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written."""

        sf_object: bulk.SFBulkType = getattr(self.sf_client.bulk, self.stream_name)

        self._process_batch_by_action(
            sf_object, self.config.get("action"), self._batched_records
        )
        self.logger.info(
            f"Completed {self.config.get('action')} of {len(self._batched_records)} records to {self.stream_name}"
        )

        # Refresh session to avoid timeouts.
        self._new_session()

    def _process_batch_by_action(
        self, sf_object: bulk.SFBulkType, action, batched_data
    ):
        """Handle upsert records different method"""

        sf_object_action = getattr(sf_object, action)

        try:
            sf_object_action(batched_data)
        except exceptions.SalesforceMalformedRequest as e:
            self.logger.error(
                f"Data in {action} {self.stream_name} batch does not conform to target SF {self.stream_name} Object"
            )
            raise (e)

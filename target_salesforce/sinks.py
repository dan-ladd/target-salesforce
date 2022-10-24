"""Salesforce target sink class, which handles writing streams."""

from cmath import log
from typing import Dict, List, Optional
from dataclasses import asdict, dataclass, field, fields
from typing_extensions import Self


from singer_sdk.sinks import BatchSink
from simple_salesforce import Salesforce, bulk, exceptions
from target_salesforce.session_credentials import parse_credentials, SalesforceAuth
from target_salesforce.utils.exceptions import InvalidSalesforceAction
from singer_sdk.plugin_base import PluginBase


@dataclass
class BatchedRecords:
    insert: List[dict] = field(default_factory=list)
    update: List[dict] = field(default_factory=list)
    upsert: List[dict] = field(default_factory=list)
    delete: List[dict] = field(default_factory=list)
    hard_delete: List[dict] = field(default_factory=list)


class SalesforceSink(BatchSink):
    """Salesforce target sink class."""

    valid_actions = [field.name for field in fields(BatchedRecords)]
    max_size = 2000

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
        self._batched_records: BatchedRecords

    @property
    def sf_client(self):
        if self._sf_client:
            return self._sf_client
        return self._new_session()

    def _new_session(self):
        session_creds = SalesforceAuth.from_credentials(
            parse_credentials(self.target.config),
            is_sandbox=self.target.config["is_sandbox"],
        ).login()
        self._sf_client = Salesforce(**asdict(session_creds))
        return self._sf_client

    def start_batch(self, context: dict) -> None:
        self.logger.info(f"Starting new batch")
        self._batched_records = BatchedRecords()

    def process_record(self, record: dict, context: dict) -> None:
        """Batch record based on the SF action"""

        action = record.get("_sdc_action", self.config.get("default_action")).lower()
        if action not in self.valid_actions:
            raise InvalidSalesforceAction(
                f"Invalid record action {action} for record {record}"
            )

        record.pop("_sdc_action", None)

        batch: List[dict] = getattr(self._batched_records, action)

        batch.append(record)

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written."""

        for action in self.valid_actions:
            batched_data: List[dict] = getattr(self._batched_records, action)
            if len(batched_data) == 0:
                self.logger.info(f"Skipping batch {action} as there are no records")
                continue

            sf_object: bulk.SFBulkType = getattr(self.sf_client.bulk, self.stream_name)

            self._process_batch_by_action(sf_object, action, batched_data)
            self.logger.info(
                f"Completed {action} of {len(batched_data)} records to {self.stream_name}"
            )

        # Refresh session to avoid timeouts.
        self._new_session()

    def _process_batch_by_action(self, sf_object: bulk.SFBulkType, action, batched_data):
        """Handle upsert records different method"""

        sf_object_action = getattr(sf_object, action)

        try:
            if action == "upsert":
                sf_object_action(batched_data, "Id")
            else:
                sf_object_action(batched_data)
        except exceptions.SalesforceMalformedRequest as e:
            self.logger.error(f"Data in {action} {self.stream_name} batch does not conform to target SF {self.stream_name} Object or {self.stream_name} does not exist")
            raise(e)
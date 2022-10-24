# target-salesforce

`target-salesforce` is a Singer target for Salesforce.

Build with the [Meltano Target SDK](https://sdk.meltano.com).

## Capabilities

* `about`
* `stream-maps`
* `schema-flattening`

## Configuration

### Accepted Config Options

You must authenticate with OAuth (`client_id`, `client_secret`, and `refresh_token`) or User/Pass (`username`, `password`, and `security_token`).

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| client_id           | False     | None    | OAuth client_id  |
| client_secret       | False     | None    | OAuth client_secret |
| refresh_token       | False     | None    | OAuth refresh_token |
| username            | False     | None    | User/password username |
| password            | False     | None    | User/password password |
| security_token      | False     | None    | User/password generated security token. Reset under your Account Settings |
| is_sandbox          | False     | False   | Is the Salesforce instance a sandbox |
| default_action      | False     | upsert  | How to handle incomming records by default. Will be overriden if `_sdc_action` is included in the record. |

A full list of supported settings and capabilities for this
target is available by running:

```bash
target-salesforce --about
```

### Source Authentication and Authorization

- For Oauth, you must create a connected app. See details from the [Salesforce documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_understanding_web_server_oauth_flow.htm).

## Usage

Incomming records must conform to your salesforce objects. Stream name should match the target Object (ex. Account) and no extra columns should be included other than the optional `_sdc_action` that dictates how records are written.

### Executing the Target Directly
The following will insert an Account record from `input_example.jsonl` into your Salesforce instance.

```bash
target-salesforce --version
target-salesforce --help
cat input_example.jsonl | target-salesforce --config /path/to/target-salesforce-config.json
```

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `target_salesforce/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-salesforce` CLI interface directly using `poetry run`:

```bash
poetry run target-salesforce --help
```

### Testing with [Meltano](https://meltano.com/)

_**Note:** This target will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd target-salesforce
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke target-salesforce --version
# OR run a test `elt` pipeline with the Carbon Intensity sample tap:
meltano elt tap-carbon-intensity target-salesforce
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano SDK to
develop your own Singer taps and targets.

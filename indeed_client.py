import os
import json
import logging
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def is_local_env():
    return os.getenv("ENV", "local").lower() == "local"


def access_secret_version(secret_id):
    from google.cloud import secretmanager_v1

    client = secretmanager_v1.SecretManagerServiceClient()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def load_secrets():
    if is_local_env():
        from dotenv import load_dotenv

        load_dotenv()
    else:
        secret_names = ["BRD_AUTH_TOKEN", "GCP_BRD_SA_KEY"]
        for secret_name in secret_names:
            os.environ[secret_name] = access_secret_version(secret_name)


load_secrets()

ROOT = Path(__file__).parent
BRD_URL = "https://api.brightdata.com/datasets/v3/trigger"
BRD_HEADERS = {
    "Authorization": os.getenv("BRD_AUTH_TOKEN"),
    "Content-Type": "application/json",
}
BRD_PARAMS = {
    "dataset_id": "gd_l4dx9j9sscpvs7no2",
    "include_errors": "true",
    "type": "discover_new",
    "discover_by": "keyword",
    "limit_per_input": "100",
}
EXTERNAL_STORAGE_DETAILS = {
    "type": "gcs",
    "filename": {"template": "{[snapshot_id]}", "extension": "json"},
    "bucket": "bright-data-landing",
    "credentials": {
        "client_email": "brightdata-sa@job-search-automation-456220.iam.gserviceaccount.com",
        "private_key": os.getenv("GCP_BRD_SA_KEY").replace("\\n", "\n"),
    },
    "directory": "indeed",
}

PAYLOAD_FP = ROOT / "indeed_payload.json"

if __name__ == "__main__":
    try:
        with open(PAYLOAD_FP, "r") as file:
            payload = {
                "deliver": EXTERNAL_STORAGE_DETAILS,
                "input": json.load(file),
            }
            response = requests.post(
                BRD_URL,
                headers=BRD_HEADERS,
                params=BRD_PARAMS,
                json=payload,
            )
        response.raise_for_status()
        logging.info(f"{response.status_code} {response.url} {response.text}")
    except Exception as e:
        logging.error(f"Error during Bright Data trigger: {e}")

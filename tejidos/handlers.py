import json
import logging

from datetime import datetime
from typing import Any, Dict, cast
from tejidos.util import dumps_json_s3, loads_json_from_s3

def download_handler(_event: Any, _context: Any) -> None:

    logging.info("Download handler.")

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    payload = json.dumps({"timestamp": timestamp})

    dumps_json_s3(body=payload, bucket="tejidos-data", key="input/timestamp.json")

def process_handler(event: Any, _context: Any) -> None:

    logging.info("Process handler.")

    record = event.get("Records")[0]
    s3_object = record.get("s3")
    bucket = s3_object.get("bucket").get("name")
    key = s3_object.get("object").get("key")


    data = loads_json_from_s3(bucket=bucket, key=key)
    date = datetime.fromtimestamp(cast(float, data.get("timestamp")))
    payload = json.dumps({"date": date.strftime("%m/%d/%Y, %H:%M:%S")})

    dumps_json_s3(body=payload, bucket="tejidos-data", key="output/datetime.txt")

def endpoint_handler(_event: Any, _context: Any) -> Dict:

    logging.info("Endpoint handler.")
    return {"latest_execution": "ok"}

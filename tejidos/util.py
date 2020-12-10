import json
from typing import Any, Dict
import boto3


def _create_s3_client():
    s3 = boto3.client('s3')
    return s3


def dumps_json_to_s3(body: str, bucket: str, key: str) -> None:
    s3 = _create_s3_client()
    s3.put_object(Body=body,
                  Bucket=bucket,
                  Key=key)


def loads_json_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    s3 = _create_s3_client()
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response['Body'].read())

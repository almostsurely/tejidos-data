import boto3

def my_sum(first: int, second: int) -> int:
    print("this is a test")
    return first + second

def dumps_json_s3(body: str, bucket: str, key: str) -> None:

    s3 = boto3.client('s3')
    s3.put_object(Body=body,
                  Bucket=bucket,
                  Key=key)


def loads_json_from_s3(bucket: str, key: str) -> None:

    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response['Body'].read())
import json
import unittest
from unittest.mock import patch, MagicMock

from botocore.response import StreamingBody

from tejidos.util import dumps_json_to_s3, loads_json_from_s3


class TestUtil(unittest.TestCase):

    @patch("tejidos.util._create_s3_client")
    # pylint: disable=R0201
    def test_dumps_json_to_s3(self, mock_create_s3_client) -> None:
        # given
        mock_s3_client = MagicMock()
        mock_create_s3_client.return_value = mock_s3_client
        expected_payload = json.dumps({"key": "value"})

        # when
        dumps_json_to_s3(body=expected_payload, bucket="test_bucket", key="some_key")

        # then
        mock_s3_client.put_object.assert_called_once_with(Body='{"key": "value"}',
                                                          Bucket='test_bucket',
                                                          Key='some_key')

    @patch("tejidos.util._create_s3_client")
    def test_loads_json_from_s3(self, mock_create_s3_client) -> None:
        # given
        mock_s3_client = MagicMock()
        mock_body = MagicMock(spec=StreamingBody)
        mock_body.read.return_value = '{"key": "value"}'
        mock_s3_client.get_object.return_value = {"Body": mock_body}
        mock_create_s3_client.return_value = mock_s3_client
        expected = {"key": "value"}

        # when
        actual = loads_json_from_s3(bucket="test_bucket", key="some_key")

        # then
        mock_s3_client.get_object.assert_called_once_with(Bucket='test_bucket', Key='some_key')
        self.assertDictEqual(expected, actual)

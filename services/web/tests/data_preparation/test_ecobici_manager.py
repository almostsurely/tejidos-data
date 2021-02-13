import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from tejidos.data_preparation.ecobici_manager import EcobiciManager, AccessToken


class TestSentinelManager(unittest.TestCase):

    @patch.object(EcobiciManager, "get_access_token")
    def test_instance(self, mock_get_access_token: MagicMock) -> None:
        EcobiciManager._instance = None
        client_id = "Dixon Butts"
        client_secret = "FJIE*#(&R%&"

        with patch.dict(os.environ, {"ECOBICI_CLIENT_ID": client_id,
                                     "ECOBICI_CLIENT_SECRET": client_secret}):
            EcobiciManager.instance()

            self.assertIsNotNone(EcobiciManager._instance)
            mock_get_access_token.assert_called_once_with(client_id='Dixon Butts', client_secret='FJIE*#(&R%&')

    @patch.object(EcobiciManager, "refresh_access_token")
    def test_access_token(self, mock_refresh_access_token):
        test_data = [SimpleNamespace(is_fresh=True),
                     SimpleNamespace(is_fresh=False)]
        expected_access_token = "some_access_token"
        for test in test_data:
            with self.subTest(msg="Testing refreshing"):
                token = MagicMock(spec=AccessToken)
                token.is_fresh.return_value = test.is_fresh
                token.access_token = expected_access_token
                ecobici_manager = EcobiciManager(token=token)

                actual_access_token = ecobici_manager._access_token

                self.assertTrue(actual_access_token, expected_access_token)
                if test.is_fresh:
                    mock_refresh_access_token.assert_not_called()
                else:
                    mock_refresh_access_token.assert_called_once_with()

    @patch.object(EcobiciManager, "_call_endpoint")
    def test_get_access_token(self, mock_call_endpoint):
        client_id = "Dixon Butts"
        client_secret = "FJIE*#(&R%&"
        access_token = "some_access_token"
        expire_time = 10000
        refresh_token = "some_refresh_token"
        token_type = "some_token_type"
        mock_call_endpoint.return_value = {"access_token": access_token,
                                           "expires_in": str(expire_time),
                                           "refresh_token": refresh_token,
                                           "token_type": token_type}
        expected = AccessToken(client_id=client_id,
                               client_secret=client_secret,
                               access_token=access_token,
                               expire_time=expire_time,
                               refresh_token=refresh_token,
                               token_type=token_type)

        actual = EcobiciManager.get_access_token(client_id=client_id, client_secret=client_secret)

        self.assertEqual(actual, expected)

    @patch.object(AccessToken, "is_fresh")
    @patch.object(EcobiciManager, "_call_endpoint")
    def test_refresh_access_token(self, mock_call_endpoint, mock_is_fresh):
        client_id = "Dixon Butts"
        client_secret = "FJIE*#(&R%&"
        access_token = "some_access_token"
        expire_time = 10000
        refresh_token = "some_refresh_token"
        token_type = "some_token_type"

        new_token = "other_access_token"
        new_refresh_token = "other_refresh_token"

        mock_is_fresh.return_value = True

        mock_call_endpoint.return_value = {"access_token": new_token,
                                           "expires_in": str(expire_time),
                                           "refresh_token": new_refresh_token,
                                           "token_type": token_type}

        token = AccessToken(client_id=client_id,
                            client_secret=client_secret,
                            access_token=access_token,
                            expire_time=expire_time,
                            refresh_token=refresh_token,
                            token_type=token_type)

        ecobici_manager = EcobiciManager(token=token)

        ecobici_manager.refresh_access_token()

        mock_call_endpoint.assert_called_once_with(url='https://pubsbapi-latam.smartbike.com/oauth/v2/token?{params}',
                                                   params={'client_id': 'Dixon Butts', 'client_secret': 'FJIE*#(&R%&',
                                                           'grant_type': 'refresh_token',
                                                           'refresh_token': 'some_refresh_token'})

        self.assertEqual(new_token, ecobici_manager._access_token)

    @patch.object(EcobiciManager, "_call_endpoint")
    def test_get_station_list(self, mock_call_endpoint):

        token = MagicMock(spec=AccessToken)
        token.is_fresh.return_value = True
        token.access_token = "some_access_token"
        mock_call_endpoint.return_value = {'stations': []}

        ecobici_manager = EcobiciManager(token=token)

        actual = ecobici_manager.get_station_list()

        mock_call_endpoint.assert_called_once_with(
            url='https://pubsbapi-latam.smartbike.com/api/v1/stations.json?{params}',
            params={'access_token': 'some_access_token'})
        self.assertEqual(actual, {'stations': []})

    @patch.object(EcobiciManager, "_call_endpoint")
    def test_get_station_disponibility(self, mock_call_endpoint):

        token = MagicMock(spec=AccessToken)
        token.is_fresh.return_value = True
        token.access_token = "some_access_token"
        mock_call_endpoint.return_value = {'stationsStatus': []}

        ecobici_manager = EcobiciManager(token=token)

        actual = ecobici_manager.get_station_disponibility()

        mock_call_endpoint.assert_called_once_with(
            url='https://pubsbapi-latam.smartbike.com/api/v1/stations/status.json?{params}',
            params={'access_token': 'some_access_token'})
        self.assertEqual(actual, {'stationsStatus': []})

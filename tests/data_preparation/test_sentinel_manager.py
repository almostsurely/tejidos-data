import os
import unittest
from unittest.mock import patch, MagicMock

from pandas import DataFrame, RangeIndex
from sentinelsat import SentinelAPI
from datetime import date

from tejidos.data_preparation.sentinel_manager import SentinelManager, SCIHUB_URL


class TestSentinelManager(unittest.TestCase):

    @patch("tejidos.data_preparation.sentinel_manager.SentinelAPI")
    def test_instance(self, mock_sentinel_api: MagicMock) -> None:
        SentinelManager._instance = None
        scihub_user = "Dixon Butts"
        scihub_password = "FJIE*#(&R%&"

        with patch.dict(os.environ, {"SCIHUB_USER": scihub_user,
                                     "SCIHUB_PASS": scihub_password}):
            SentinelManager.instance()
            mock_sentinel_api.assert_called_once_with(scihub_user, scihub_password, SCIHUB_URL)
            self.assertIsNotNone(SentinelManager._instance)

    def test_api_query(self) -> None:
        mock_api = MagicMock(spec=SentinelAPI)
        mock_dict_result = {}
        mock_api.query.return_value = mock_dict_result
        expected_df = DataFrame()
        mock_api.to_dataframe.return_value = expected_df
        sentinel_manager = SentinelManager(sentinel_api=mock_api)

        footprint = "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
        start_date = date(2020, 11, 1)
        end_date = date(2049, 2, 22)
        platform = "SomeSillySatellite"
        cloud_cover = (7, 86)

        actual_df = sentinel_manager.api_query(footprint=footprint,
                                               begin_date=start_date,
                                               end_date=end_date,
                                               platformname=platform,
                                               cloudcoverpercentage=cloud_cover)

        mock_api.query.assert_called_once_with(area=footprint,
                                               date=(start_date, end_date),
                                               platformname=platform,
                                               cloudcoverpercentage=cloud_cover)

        mock_api.to_dataframe.assert_called_once_with(mock_dict_result)

        self.assertTrue(DataFrame.equals(actual_df, expected_df))

    @patch("os.path.exists")
    def test_download_product(self, mock_exists) -> None:
        mock_api = MagicMock(spec=SentinelAPI)
        mock_exists.return_value = False

        mock_index = MagicMock(spec=RangeIndex)
        sentinel_manager = SentinelManager(sentinel_api=mock_api)
        title = "some_title"
        destination = "some_path"
        expected = f"{destination}/{title}.zip"
        product = DataFrame({
            'title': ("_", title)
        }, columns=["title"])

        actual = sentinel_manager.download_product(product=product, destination_path=destination)

        mock_api.download_all.assert_called_once()  # this was hard to test properly becuase pandas doesn't play nicely
                                                    # with comparisons.
        self.assertEqual(actual, expected)

    @patch("os.path.exists")
    def test_download_product_exists(self, mock_exists) -> None:
        mock_api = MagicMock(spec=SentinelAPI)
        mock_exists.return_value = True

        sentinel_manager = SentinelManager(sentinel_api=mock_api)

        title = "some_title"
        destination = "some_path"
        expected = f"{destination}/{title}.zip"
        product = DataFrame({
            'title': ("_", title)
        }, columns=["title"])

        actual = sentinel_manager.download_product(product=product, destination_path=destination)
        mock_api.download_all.assert_not_called()
        self.assertEqual(actual, expected)

    def test_last_product(self):
        latest_date = date(2000, 1, 20)
        product = DataFrame({
            'ingestiondate': [date(2000, 1, 3),
                              date(2000, 1, 9),
                              date(2000, 1, 1),
                              latest_date,
                              date(2000, 1, 17)]
        }, columns=["ingestiondate"])

        actual = SentinelManager.last_product(product)
        self.assertEqual(actual["ingestiondate"].iloc[0], latest_date)

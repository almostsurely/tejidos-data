import unittest

from tejidos.util import my_sum


class TestUtil(unittest.TestCase):

    def test_my_sum(self) -> None:

        # given
        some_number = 21
        another_number = 34
        expected = 55

        # when

        actual = my_sum(first=some_number, second=another_number)

        # then
        self.assertEqual(expected, actual)

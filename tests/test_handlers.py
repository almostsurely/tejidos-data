import unittest

from tejidos.handlers import sum_handler

@
class TestUtil(unittest.TestCase):

    @unittest.skip("Testing")
    def test_sum_handler(self) -> None:

        # given
        some_number = 21
        another_number = 34
        expected = 55
        event = {"first": some_number,
                 "second": another_number}


        # when

        actual = sum_handler(event=event, _context={})

        # then
        self.assertDictEqual({"sum": expected}, actual)

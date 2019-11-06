from unittest import TestCase
from argparse import Namespace

from main import main
from main import parse_args
from strings import DATA_PATH_ARG
from strings import DATA_PATH


class TestMain(TestCase):
    def test_can_run(self):
        argv: list = self._get_test_argv()
        main(argv)

    def test_parse_args(self):
        argv: list = self._get_test_argv()
        args: Namespace = parse_args(argv)

        self.assertEqual(args.data_path, DATA_PATH)

    @staticmethod
    def _get_test_argv() -> list:
        args: list = [
            DATA_PATH_ARG,
            DATA_PATH
        ]
        return args

import sys
import unittest

from strings import TEST_DIR, MAIN_NAME


if __name__ == MAIN_NAME:
    test_runner = unittest.TextTestRunner(verbosity=1)
    tests = unittest.TestLoader().discover(TEST_DIR)

    if not test_runner.run(tests).wasSuccessful():
        sys.exit(1)

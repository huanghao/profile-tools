import unittest

from profiletools.path import sub, esc


class PathTest(unittest.TestCase):

    def test_esc(self):
        self.assertEquals(
            '__HOME__/.ssh/config',
            esc('~/.ssh/config'))

    def test_sub(self):
        self.assertEquals(
            '~/.ssh/config',
            sub('__HOME__/.ssh/config'))

    def test_unchanged(self):
        path = '/some/normal/path'
        self.assertEquals(path, esc(path))
        self.assertEquals(path, sub(path))

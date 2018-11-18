import unittest
#import test_util.TempFilepath
from test_util.tempfile_path import TempFilepath

from linestore import Linestore

def spit(path, content):
    with open(path, "wb") as f: 
        f.write(content) 

class LinestoreTest(unittest.TestCase):

    def test_read_empty(self):
        with TempFilepath() as path:
            spit(path, "")
            store = Linestore(path)
            store.open()
            read = store.readlines(1)
            self.assertEqual(read, []);

    def test_append(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [2.0, 3])

            with open(path, "rb") as tmpfile:
                content = tmpfile.read(32)
                # start mark
                self.assertEqual(content[0:3], "\xFF\x00\xFF");
                # version 
                self.assertEqual(content[3:6], "\x01\x00\x02");
                # first value 
                self.assertEqual(content[6:12], "f\x00\x00\x00@\x1E");
                # second value 
                self.assertEqual(content[12:18], "i\x03\x00\x00\x00\x1E");
                # group end marker
                self.assertEqual(content[18:21], "\xFF\x1D\xFF");

                self.assertEqual(len(content), 21);

    def test_validate_version(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [2.0])
            store.close()
            store.open()
            result = store.readlines(2)
            self.assertEqual(result, [])

    def test_write_read_float(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [2.0, 3.2, 1./3.])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 3)

            self.assertEqual(result[0][0], 2.0)
            self.assertAlmostEqual(result[0][1], 3.2)
            self.assertAlmostEqual(result[0][2], 1./3.)

            self.assertEqual(type(result[0][0]), float)
            self.assertEqual(type(result[0][1]), float)
            self.assertEqual(type(result[0][2]), float)

    def test_write_read_int(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [5, -4, 0])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 3)
            self.assertEqual(type(result[0][0]), int)
            self.assertEqual(type(result[0][1]), int)
            self.assertEqual(type(result[0][2]), int)
            self.assertEqual(result, [[5,-4,0]])

    def test_write_read_long(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [9223372036854775807L, -4L, 0L])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 3)
            self.assertEqual(type(result[0][0]), long)
            self.assertEqual(type(result[0][1]), long)
            self.assertEqual(type(result[0][2]), long)
            self.assertEqual(result, [[9223372036854775807L, -4L, 0L]])

    def test_write_read_mixed(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [9223372036854775807L, 3.1415, 12])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 3)
            self.assertEqual(type(result[0][0]), long)
            self.assertEqual(type(result[0][1]), float)
            self.assertEqual(type(result[0][2]), int)

            self.assertEqual(result[0][0], 9223372036854775807L)
            self.assertAlmostEqual(result[0][1], 3.1415)
            self.assertEqual(result[0][2], 12)

    def test_write_read_multiple_lines(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [23, 1.23])
            store.append(1, [24, 2.151])
            store.append(1, [5, 0.0014])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(len(result[0]), 2)
            self.assertEqual(len(result[1]), 2)
            self.assertEqual(len(result[2]), 2)

            self.assertEqual(result[0][0], 23)
            self.assertAlmostEqual(result[0][1], 1.23)

            self.assertEqual(result[1][0], 24)
            self.assertAlmostEqual(result[1][1], 2.151, 4)

            self.assertEqual(result[2][0], 5)
            self.assertAlmostEqual(result[2][1], 0.0014, 5)



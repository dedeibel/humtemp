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

    def test_ignores_garbage_at_the_beginning(self):
        with TempFilepath() as path:
            spit(path, "deadbeef"+
                    b'\xFF\x00\xFF'+ # start group
                    b'\x01\x00\x02'+ # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    b'\xFF\x1D\xFF' # end group
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3]])

    def test_ignores_garbage_at_the_end(self):
        with TempFilepath() as path:
            spit(path, 
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    Linestore.GROUP_END + # end group
                    'deadbeef'
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3]])

    def test_ignores_garbage_between_entries(self):
        with TempFilepath() as path:
            spit(path, 
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    b'\xFF\x1D\xFF'+ # end group
                    'deadbeef' +
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x04\x00\x00\x00' + Linestore.FIELD_END + # value 4
                    Linestore.GROUP_END
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3], [4]])

    def test_ignores_garbage_between_entries_similar_to_separators(self):
        with TempFilepath() as path:
            spit(path, 
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    Linestore.GROUP_END +
                    b'\xFF\x00\xEF'+ # GARBAGE similar to start grp
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x04\x00\x00\x00' + Linestore.FIELD_END + # value 4
                    Linestore.GROUP_END
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3], [4]])

    def test_ignores_entries_with_different_version_in_between(self):
        with TempFilepath() as path:
            spit(path, 
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    Linestore.GROUP_END +
                    Linestore.GROUP_START +
                    b'\x02\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x06\x00\x00\x00' + Linestore.FIELD_END + # value 6
                    Linestore.GROUP_END +
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x04\x00\x00\x00' + Linestore.FIELD_END + # value 4
                    Linestore.GROUP_END
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3], [4]])

    def test_ignores_entries_with_illegal_termination_are_ignored(self):
        with TempFilepath() as path:
            spit(path, 
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                    Linestore.GROUP_END +
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x06\x00\x00\x00' + Linestore.FIELD_END + # value 6
                    b"\xFF\x1D\xFE" +  # GARBAGE GROUP END
                    Linestore.GROUP_START +
                    b'\x01\x00' + Linestore.VERSION_STMT_END + # version
                    b'i\x04\x00\x00\x00' + Linestore.FIELD_END + # value 4
                    Linestore.GROUP_END
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3], [4]])

    def test_truncate(self):
        with TempFilepath() as path:
            spit(path,  Linestore.GROUP_START +
                        b'\x01\x00' + Linestore.VERSION_STMT_END +
                        b'i\x03\x00\x00\x00' + Linestore.FIELD_END + # value 3
                        Linestore.GROUP_END
            );

            store = Linestore(path)
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[3]])
            store.close()

            store.truncate()

            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [])
            store.close()


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
            store.append(1, [2.0, 3.0])

            with open(path, "rb") as tmpfile:
                content = tmpfile.read(32)
                # start mark
                self.assertEqual(content[0:3], "\xFF\x00\xFF");
                # version 
                self.assertEqual(content[3:6], "\x01\x00\x02");
                # first value 
                self.assertEqual(content[6:11], "\x00\x00\x00@\x1E");
                # second value 
                self.assertEqual(content[11:16], "\x00\x00@@\x1E");
                # group end marker
                self.assertEqual(content[16:19], "\xFF\x1D\xFF");

                self.assertEqual(len(content), 19);

    def test_validate_version(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [2.0])
            store.close()
            store.open()
            result = store.readlines(2)
            self.assertEqual(result, [])

    def test_read(self):
        with TempFilepath() as path:
            store = Linestore(path)
            store.open()
            store.append(1, [2.0, 3.0])
            store.close()
            store.open()
            result = store.readlines(1)
            self.assertEqual(result, [[2.0, 3.0]])


#    def test_read_floats(self):
#        with TempFilepath() as path:
#            spit(path, "1\t2.0\t3.4\n"+
#                       "1\t4.2\t5.3\n")
#            store = Linestore(path)
#            store.open()
#            read = store.readlines(1)
#            self.assertEqual(read, [[1.0,2.0,3.4],[1.0,4.2,5.3]]);
#
#    def test_read_int(self):
#        with TempFilepath() as path:
#            spit(path, "1\t2\t3\n"+
#                       "1\t4\t5\n")
#            store = Linestore(path)
#            store.open()
#            read = store.readlines(1)
#            self.assertEqual(read, [[1.0,2.0,3.4],[1.0,4.2,5.3]]);
#

import tempfile
import os

class TempFilepath():
    def __enter__(self):
        self.path = tempfile.mkstemp()[1]
        return self.path

    def __exit__(self, type, value, traceback):
        os.remove(self.path)


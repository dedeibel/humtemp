import os
from struct import pack, unpack

# tab sep floats
class Linestore:
    CHUNK_SIZE=128

    def __init__(self, filepath):
        self.filepath = filepath

    def open(self):
        self.fp = open(self.filepath, 'r+b')

    def close(self):
        self.fp.close()

    def append(self, version, data):
        # xFFx00xFF start of entry
        # hx1E version statement
        # x1E separator of fields RS
        # xFFx1DxFF end of group / data entry GS
        # Min size 9 bytes
        self.fp.seek(0, os.SEEK_END)
        self.fp.write("\xFF\x00\xFF" + pack("H", version) + "\x02")
        for val in data:
            self.fp.write(pack("f", val) + "\x1E")
        self.fp.write("\xFF\x1D\xFF")
        self.fp.flush()
        # gibt version aus
        # fuer alle eintraege
        # gib typ praefix aus
        # gib daten aus
        # gib newline aus

    def readlines(self, version):
        self.fp.seek(0)
        results = []
        found_version = None

        while True:
            chunk = self.fp.read(Linestore.CHUNK_SIZE)
            print("chunk len: " + str(len(chunk)))
            print("to read: "+ ''.join('%02x'%ord(i) for i in chunk))
            if chunk == "":
                break
            elif len(chunk) < 9:
                # minmum size vor a valid entry
                break

            index = 0
            if chunk[index:index + 3] == "\xFF\x00\xFF":
                index += 3
                try:
                    print("idx read: "+ ''.join('%02x'%ord(i) for i in chunk[index:index+2]))
                    found_version = unpack("H", chunk[index:index+2])[0]
                    parsed_version = int(found_version)
                    if parsed_version != version:
                        break

                    index += 2

                    if chunk[index:index + 1] != "\x02":
                        print("version not properly terminated")
                        break

                    index += 1
                except Exception as e:
                    print("illegal version found: " + str(e))
                    break

            current_entry = []
            entry_index = index
            while entry_index < len(chunk):
                print("chunk size: "+ str(len(chunk)) +" index: " + str(index) + " entry_idx: "+ str(entry_index))

                if chunk[entry_index:entry_index + 3] == "\xFF\x1D\xFF":
                    results.append(current_entry)
                    current_entry = []
                    entry_index += 3
                    continue

                # no float to read
                if (len(chunk) - entry_index) < 4:
                    break

                print("to read: "+ ''.join('%02x'%ord(i) for i in chunk[entry_index:entry_index + 4]))

                print("val: "+ str(float(unpack('f', chunk[entry_index:entry_index + 4])[0])))

                unpacked = float(unpack('f', chunk[entry_index:entry_index + 4])[0])
                entry_index += 4

                if chunk[entry_index:entry_index + 1] != "\x1E":
                    print("entry not properly terminated")
                    break

                entry_index += 1

                current_entry.append(unpacked)


            # search for version (buffer 2)
            # read entries, split at RS
            # stop at GS
            #parsed_group = self._parse_group(line)
            #results.append(parsed_group)

        return results

    def _parse_line(self, line):
        return map(float, line.split("\t"))


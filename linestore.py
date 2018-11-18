import os
from struct import pack, unpack, calcsize

def _hex(data):
    return ''.join(("%02x" % ord(i)) for i in data)

def _starts(buff, search):
    slen = len(search)
    if len(buff) < slen:
        return False

    return buff[:slen] == search

# tab sep floats
class Linestore:
    CHUNK_SIZE=128

    def __init__(self, filepath):
        self.filepath = filepath
        self._create_file()

    def _create_file(self):
        db_file = open(self.filepath, 'a')
        db_file.close()

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
        # SEEK_END = 2
        self.fp.seek(0, 2)
        self.fp.write(b"\xFF\x00\xFF")
        self.fp.write(pack("H", version))
        self.fp.write(b"\x02")
        for val in data:
            if type(val) == float:
                self.fp.write('f')
                self.fp.write(pack("f", val))
                self.fp.write(b'\x1E')
            elif type(val) == int:
                self.fp.write('i')
                self.fp.write(pack("i", val))
                self.fp.write(b'\x1E')
            elif type(val) == long:
                self.fp.write('l')
                self.fp.write(pack("l", val))
                self.fp.write(b'\x1E')
            else:
                print('ERR unsupported type: ' + str(type(val)))
        self.fp.write(b"\xFF\x1D\xFF")
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
            #print("chunk len: " + str(len(chunk)))
            #print("to read: " + _hex(chunk))

            if chunk == b"":
                break
            elif len(chunk) < 9:
                # minmum size vor a valid entry
                break

            index = 0
            while index < len(chunk):
                if _starts(chunk[index:], b'\xFF\x00\xFF'):
                    index += 3
                    try:
                        #print("idx read: "+ _hex(chunk[index:index+2]))
                        found_version = unpack("H", chunk[index:index+2])[0]
                        parsed_version = int(found_version)
                        if parsed_version != version:
                            break

                        index += 2

                        if not _starts(chunk[index:], b"\x02"):
                            print("version not properly terminated")
                            break

                        index += 1
                    except Exception as e:
                        print("illegal version found: " + str(e))
                        break
                else:
                    # keep seaching for the start
                    index += 1
                    continue

                current_entry = []
                entry_index = index

                while entry_index < len(chunk):
                    #print("chunk size: "+ str(len(chunk)) +" index: " + str(index) + " entry_idx: "+ str(entry_index))

                    if _starts(chunk[entry_index:], b"\xFF\x1D\xFF"):
                        results.append(current_entry)
                        current_entry = []
                        entry_index += 3
                        break

                    # no data plus markers to read
                    if (len(chunk) - entry_index) < 4:
                        break

                    data_type = chunk[entry_index:entry_index + 1]
                    #print("type: "+ _hex(data_type))

                    entry_index += 1

                    #print("to read: " + _hex(chunk[entry_index:]))

                    unpacked_data = None
                    if data_type == 'f':
                        unpacked_data = float(unpack('f', chunk[entry_index:entry_index + calcsize('f')])[0])
                        entry_index += calcsize('f')
                    elif data_type == 'i':
                        unpacked_data = int(unpack('i', chunk[entry_index:entry_index + calcsize('i')])[0])
                        entry_index += calcsize('i')
                    elif data_type == 'l':
                        unpacked_data = long(unpack('l', chunk[entry_index:entry_index + calcsize('l')])[0])
                        entry_index += calcsize('l')
                    else:
                        print('ERR unsupported type: ' + _hex(data_type))

                    #print("val: "+ str(unpacked_data))

                    if not _starts(chunk[entry_index:], b"\x1E"):
                        print("entry not properly terminated")
                        break
                    entry_index += 1

                    current_entry.append(unpacked_data)

                # search for version (buffer 2)
                # read entries, split at RS
                # stop at GS
                #parsed_group = self._parse_group(line)
                #results.append(parsed_group)

        return results

    def _parse_line(self, line):
        return map(float, line.split("\t"))


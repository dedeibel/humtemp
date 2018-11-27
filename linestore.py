import os
from struct import pack, unpack, unpack_from, calcsize

def _hex(data):
    return ''.join(("%02x" % ord(i)) for i in data)

def _starts_with(buff, search):
    slen = len(search)
    if len(buff) < slen:
        return False

    return buff[:slen] == search

# tab sep floats
class Linestore:
    GROUP_START = b'\xFF\x00\xFF'
    GROUP_START_LEN = 3
    GROUP_END = b"\xFF\x1D\xFF"
    GROUP_END_LEN = 3
    VERSION_STMT_END = b'\x02' # Start of text
    VERSION_STMT_END_LEN = 1
    FIELD_END = b'\x1E'
    FIELD_END_LEN = 1
    FLOAT_MARK = 'f'
    INT_MARK = 'i'
    LONG_MARK = 'l'
    MIN_VALID_SIZE = 15
    SIZE_i = calcsize('i')
    SIZE_l = calcsize('l')
    SIZE_f = calcsize('f')
    SIZE_H = calcsize('H')
    
    SEEK_END = 2
    
    CHUNK_SIZE = 128

    TYPES = [
        {
            'type': float,
            'mark': 'f',
            'pack': lambda fp, val: fp.write(pack('f', val)),
            'unpack': lambda buff: float(unpack_from('f', buff)[0]),
            'size': calcsize('f'),
        },
        {
            'type': int,
            'mark': 'i',
            'pack': lambda fp, val: fp.write(pack('i', val)),
            'unpack': lambda buff: int(unpack_from('i', buff)[0]),
            'size': calcsize('i'),
        },
        {
            'type': long,
            'mark': 'l',
            'pack': lambda fp, val: fp.write(pack('l', val)),
            'unpack': lambda buff: long(unpack_from('l', buff)[0]),
            'size': calcsize('l'),
        },
    ]

    def __init__(self, filepath):
        self.filepath = filepath
        self._create_file()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _create_file(self):
        db_fp = open(self.filepath, 'a')
        db_fp.close()

    def open(self):
        self.fp = open(self.filepath, 'r+b')

    def close(self):
        self.fp.close()
        self.fp = None

    def truncate(self):
        db_fp = open(self.filepath, 'w')
        db_fp.close()

    # version: unsiged short
    # data: [ int | long | float ]
    def append(self, version, data):
        self.fp.seek(0, Linestore.SEEK_END) 

        self.fp.write(Linestore.GROUP_START)

        self.fp.write(pack("H", version)) # unsiged short
        self.fp.write(Linestore.VERSION_STMT_END)

        for val in data:
            found_type = False
            for typ in Linestore.TYPES:
                if typ['type'] == type(val):
                    self.fp.write(typ['mark'])
                    typ['pack'](self.fp, val)
                    self.fp.write(Linestore.FIELD_END)
                    found_type = True

            if not found_type:
                print('ERR unsupported type: ' + str(type(val)))

        self.fp.write(Linestore.GROUP_END)
        self.fp.flush()

    def readlines(self, version):
        self.fp.seek(0)
        results = []
        found_version = None

        while True:
            chunk = self.fp.read(Linestore.CHUNK_SIZE)
            #print("chunk len: " + str(len(chunk)))
            #print("to read: " + _hex(chunk))

            if len(chunk) < 9:
                # minmum size vor a valid entry
                break

            index = 0
            while index < len(chunk):
                if _starts_with(chunk[index:], Linestore.GROUP_START):
                    index += Linestore.GROUP_START_LEN
                    try:
                        #print("idx read: "+ _hex(chunk[index:index+2]))
                        found_version = unpack('H', chunk[index:index + Linestore.SIZE_H])[0]
                        parsed_version = int(found_version)
                        if parsed_version != version:
                            print("version missmatch, ignoring")
                            continue

                        index += Linestore.SIZE_H

                        if not _starts_with(chunk[index:], Linestore.VERSION_STMT_END):
                            print("version not properly terminated")
                            continue

                        index += Linestore.VERSION_STMT_END_LEN
                    except Exception as e:
                        print("illegal version found: " + str(e))
                        continue
                else:
                    # keep seaching for the start
                    index += 1
                    continue

                current_entry = []
                entry_index = index

                while entry_index < len(chunk):
                    #print("chunk size: "+ str(len(chunk)) +" index: " + str(index) + " entry_idx: "+ str(entry_index))

                    if _starts_with(chunk[entry_index:], Linestore.GROUP_END):
                        results.append(current_entry)
                        current_entry = []
                        entry_index += Linestore.GROUP_END_LEN
                        break

                    # no data plus markers to read
                    if (len(chunk) - entry_index) < 4:
                        break

                    data_type = chunk[entry_index:entry_index + 1]
                    #print("type: "+ _hex(data_type))
                    entry_index += 1

                    #print("to read: " + _hex(chunk[entry_index:]))

                    unpacked_data = None

                    found_type = False
                    for typ in Linestore.TYPES:
                        if typ['mark'] == data_type:
                            unpacked_data = typ['unpack'](chunk[entry_index:])
                            entry_index += typ['size']
                            found_type = True

                    if not found_type:
                        print('ERR unsupported type: ' + _hex(data_type))
                        break

                    #print("val: "+ str(unpacked_data))

                    if not _starts_with(chunk[entry_index:], Linestore.FIELD_END):
                        print("entry not properly terminated")
                        break
                    entry_index += Linestore.FIELD_END_LEN

                    current_entry.append(unpacked_data)

        return results


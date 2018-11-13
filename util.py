
def to_hex_str(data):
    return ''.join(("%02x" % ord(i) if type(i) == str else i) for i in data)


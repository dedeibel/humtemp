
def pprint(obj):
    return repr(obj)

def to_hex_str(data):
    return ''.join("{0:x}".format(b) for b in data)


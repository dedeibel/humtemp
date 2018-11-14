#!/usr/bin/python
import argparse
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description='Combine python files into one')
parser.add_argument('infile', help='start to search modules from here')
parser.add_argument('outfile')

imports = {}
has_overspecific_import = False

def match_import(line):
    match = re.match('\s*from\s+([^ ]+)\s+import\s+(.+)', line)
    if match:
        return (match, match.group(1), match.group(2))
    else:
        return (False, None, None)

def gather_imports(infile, filename, depth):
    for line in infile:
        match = match_import(line)
        if match[0]:
            on_import(filename, match[1], match[2], depth)

def test_for_specific_imports(filename, module, imports):
    if imports != '*':
        sys.stderr.write('{}: module "{}" can only import all symbols using "*"\n'.format(filename, module))
        global has_overspecific_import
        has_overspecific_import = True

def module_filename(module):
    return module + '.py'

def is_local_module_file(filename):
    return Path(filename).is_file()

def on_import(filename, module, imports, depth):
    subfilename = module_filename(module)

    if not is_local_module_file(subfilename):
        return

    test_for_specific_imports(filename, module, imports)
        
    is_new = note_import_use(module, depth)

    with open(subfilename, "r") as subfile:
        gather_imports(subfile, subfilename, depth + 1)

def import_already_known(module):
    return module in imports

def note_import_use(module, depth):
    global imports
    if module in imports:
        imports[module] = max(depth, imports[module])
        return False
    else:
        imports[module] = depth
        return True

def print_import(outfile, import_list):
    if len(import_list) <= 0:
        return

    with open(import_list[0], 'r') as infile:
        for line in infile:
            # TODO optimize local import recognition
            match = match_import(line)
            if match[0]:
                subfilename = module_filename(match[1])
                if is_local_module_file(subfilename):
                    continue
            outfile.write(line)

    print_import(outfile, import_list[1:])

def concat(infile, outfile, import_list):
    concat_done = False
    for line in infile:
        match = match_import(line)
        if match[0]:
            subfilename = module_filename(match[1])
            if is_local_module_file(subfilename):
                if not concat_done:
                    print_import(outfile, import_list)
                    concat_done = True
                continue
        outfile.write(line)

def main():
    args = parser.parse_args()
    
    with open(args.infile, "r") as infile:
        gather_imports(infile, args.infile, 0)

    if has_overspecific_import:
        sys.stderr.write('cannot combine files, please use only "*" imports\n')
        sys.exit()

    import_list = imports.items();
    import_list.sort(lambda x,y: cmp(y[1], x[1]))
    import_list = list(map(lambda entry: entry[0] + '.py', import_list))

    with open(args.infile, "r") as infile:
        with open(args.outfile, "w") as outfile:
            concat(infile, outfile, import_list)

main()

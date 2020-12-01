import sys
import os
import time
from baseconv import base2
from pathlib import Path
import pprint
pp = pprint.PrettyPrinter(indent=4)

def main(asm_file):
    with open(asm_file, 'r') as f:
        result = translate_instructions(f.readlines())

    filepath = Path(asm_file).resolve()
    filelocation = filepath.parent
    hack_file = asm_file.replace(".asm", ".hack").split("/")[-1]
    newfilepath = filelocation / hack_file 

    output = "\n".join([l for l in result if l]) 
    with open(newfilepath, 'w') as f:
        for i in output:
            f.write(i)

def strip(raw):
    to_translate = []
    for i in raw:
        stripped_line = i.strip()
        if stripped_line:
            if not stripped_line.startswith("//"):
                if "//" in stripped_line:
                    to_translate.append(stripped_line.split("//")[0].strip())
                else:
                    to_translate.append(stripped_line)
    return to_translate

def translate_instructions(lines_to_translate):
    binary_list = []
    lines = strip(lines_to_translate)
    for i in lines:
        if i[0] == '@':
            try:
                new_i = base2.encode(int(i[1:]))
                binary_list.append(new_i)
            except:
                pass
    return binary_list

start = time.time()
main(sys.argv[1])

end = time.time()
print(f'the execution took {end-start:.4f} seconds')
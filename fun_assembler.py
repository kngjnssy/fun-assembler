import sys
import time
from baseconv import base2
from pathlib import Path

# 1. open file and read lines into a list 
start = time.time()
asm_file = sys.argv[1]
with open(asm_file, 'r') as f:
    all_lines = f.readlines()

# 2. filter out empty lines and anything but addresses from the list 
no_empty_lines = tuple(filter(lambda x: x != '', all_lines))
to_translate = tuple(filter(lambda x: x[0] == '@', no_empty_lines))

# 3. define function for converting to binary and map it to the filtered list
def convert_to_binary(line):
    binary_code = base2.encode(int(line[1:]))
    return binary_code

binaries = tuple(map(convert_to_binary, to_translate))

# 4. create output file and write the lines to it
filepath = Path(asm_file).resolve()
filelocation = filepath.parent
hack_file = asm_file.replace(".asm", ".hack").split("/")[-1]
newfilepath = filelocation / hack_file 

output = "\n".join([l for l in binaries if l]) 

with open(newfilepath, 'w') as f:
    for i in output:
        f.write(i)

# +1. time the process 
end = time.time()
print(f'the execution took {end-start:.4f} seconds')
import sys
import os
import time
from baseconv import base2
from pathlib import Path

start = time.time()

# 1. open the asm file and read it by lines
asm_file = sys.argv[1]
filepath = Path(asm_file).resolve()
filelocation = filepath.parent
hack_file = asm_file.replace(".asm", ".hack").split("/")[-1]
newfilepath = filelocation / hack_file

asm_file = open(sys.argv[1])
raw_lines = asm_file.readlines()
lines_arr = []
for i in raw_lines:
    i = i.strip()
    lines_arr.append(i)

# 2. create a symbol table/dictionary & add predefined symbols
symbol_table = {'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6,'R7':7, 'R8':8, 'R9':9, 'R10':10, 'R11':11, 'R12':12, 'R13':13, 'R14':14, 'R15':15, 'SCREEN':16384, 'KBD':24576, 'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4}

# create lines arr
clean_lines_arr = []

# 3. check lines and find symbols?
index = 0
count_labels = 0
count_variable_symbol = 16

# ------- 0th pass - clean lines from unnecessary stuff-------
for i in lines_arr:
    try:
        if i[0] == '/':
            lines_arr.pop(i)
        if i:
            clean_lines_arr.append(i)
    except:
        pass

# ------- first pass - save (LABELS) to symbol table -------
for i in clean_lines_arr:
    if i[0] == '(':
            index = clean_lines_arr.index(i)
            # value will be the next line after (label), but we start counting from 0
            symbol_table[i] = index - count_labels 
            count_labels += 1
            # clean_lines_arr.pop(i)

# ------- second pass - ADD variable symbols from 16 on -------
for i in clean_lines_arr:
    if i[0] == '@':
        i_without_at = i.replace('@','') #check what comes after @
        # if it is already in the symbol table
        if i_without_at in symbol_table:
            pass
        if i_without_at not in symbol_table:
        # or if it is not, save it
            symbol_table[i_without_at] = count_variable_symbol
            count_variable_symbol += 1  

# ------- third? pass  convert @variable_symbols to their value at symbol_table
for k in clean_lines_arr:
    if k[0] == '@':
        k = k.replace('@','')
        try:
            k = int(k)
        except:    
            k_new = '@' + str(symbol_table[k])
            for i in range(len(clean_lines_arr)):
                clean_lines_arr[i].replace(k, k_new)

lines_without_labels = []
for line in clean_lines_arr:
    if line[0] != '(':
        lines_without_labels.append(line)

final_lines_no_symbols = []
for line in lines_without_labels:
    if line[0] == '@':
        line = line.replace('@','')
        label = '(' + line + ')'
        if label in symbol_table:
            new_line = '@' + str(symbol_table[label])
            final_lines_no_symbols.append(new_line)
        elif line in symbol_table:
            new_line = '@' + str(symbol_table[line])
            final_lines_no_symbols.append(new_line)
    else:
        final_lines_no_symbols.append(line)

# ------- convert to binary -------
binary_list = []

# 1. convert C-instructions
for k in final_lines_no_symbols.copy():
    if k[0] != '@':
        k = k + ' '
        k_new = '111' # add 111 at the beginning
        # add comp bits
        if '=0' in k or '0;' in k:
            k_new += '0101010'
        if '=1' in k or '1;' in k:
            k_new += '0111111'
        if '=-1' in k or '-1;' in k:
            k_new += '0111010'
        if '=D ' in k or 'D;' in k:
            k_new += '0001100'
        if '=A ' in k or 'A;' in k:
            k_new += '0110000'
        if '=!D ' in k or '!D;' in k:
            k_new += '0001101'
        if '=!A ' in k or '!A;' in k:
            k_new += '0110001'
        if '=-D ' in k or '-D;' in k:
            k_new += '0001111'
        if '=-A ' in k or '-A;' in k:
            k_new += '0110011'
        if 'D+1' in k:
            k_new += '0011111'
        if 'A+1' in k:
            k_new += '0110111'
        if 'D-1' in k:
            k_new += '0001110'
        if 'A-1' in k:
            k_new += '0110010'
        if 'D+A' in k:
            k_new += '0000010'
        if 'D-A' in k:
            k_new += '0010011'
        if 'A-D' in k:
            k_new += '0000111'
        if 'D&A' in k:
            k_new += '0000000'
        if 'D|A' in k:
            k_new += '0010101' 
        if '=M ' in k or 'M;' in k:
            k_new += '1110000'
        if '=!M ' in k or '!M;' in k:
            k_new += '1110001'
        if '=-M ' in k or '-M;' in k:
            k_new += '1110011'
        if 'M+1' in k:
            k_new += '1110111'
        if 'M-1' in k:
            k_new += '1110010'
        if 'D+M' in k:
            k_new += '1000010'
        if 'D-M' in k:
            k_new += '1010011'
        if 'M-D' in k:
            k_new += '1000111'
        if 'D&M' in k:
            k_new += '1000000'
        if 'D|M' in k:
            k_new += '1010101'  

        # add destination bits
        if '=' not in k:
            k_new += '000'
        if 'AMD=' in k:
            k_new += '111'
        if 'MD=' in k and 'AMD' not in k:
            k_new += '011'
        if 'AM=' in k:
            k_new += '101'
        if 'AD=' in k:
            k_new += '110'
        if 'A=' in k:
            k_new += '100'
        if 'M=' in k and 'AM' not in k:
            k_new += '001'
        if 'D=' in k and 'AD' not in k and 'MD' not in k and 'AMD' not in k:
            k_new += '010'

        # add jump bits
        if ';' not in k:
            k_new += '000'
        if 'JGT' in k:
            k_new += '001'
        if 'JEQ' in k:
            k_new += '010'
        if 'JGE' in k:
            k_new += '011'
        if 'JLT' in k:
            k_new += '100'
        if 'JNE' in k:
            k_new += '101'
        if 'JLE' in k:
            k_new += '110'
        if 'JMP' in k:
            k_new += '111'

    if k[0] == '@':
        k_new = k.replace('@','')
        try:
            k_new = base2.encode(int(k_new))
        except:
            pass
        while len(k_new) < 16:
            k_new = '0' + k_new 

    binary_list.append(k_new)

# 2. convert A-instructions
for k in final_lines_no_symbols.copy():
    if k[0] == '@':
        k_new = k.replace('@','')
        try:
            k_new = base2.encode(int(k_new))
        except:
            pass
        while len(k_new) < 16:
            k_new = '0' + k_new 


# 5. write .hack file
with open(newfilepath, "w+") as file:
    for i in binary_list:
        i = i + '\n'
        file.write(i)

end = time.time()
print(f'with loops the execution took: {end-start:.4f} seconds')


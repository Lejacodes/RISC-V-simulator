#read bin   ok
#check sign    ok
#funct decode   ok
#main   ok

#!/usr/bin/env python3

import sys
import struct 

def main():
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <binary_file>")
        sys.exit(1)

    instructions = read_bin(sys.argv[1])
    for idx, instr in enumerate(instructions):
        hex_instr = "{:08x}".format(instr)
        assembly = decode_inst(instr)
        print("inst " + str(idx) + ": " + hex_instr + " " + assembly)

def read_bin(filename):
    f = open(filename, 'rb')
    data = f.read()
    f.close()
    # convert binary data into a list of little endians (32 bits int) then each list stores 4 bites every time
    return [struct.unpack('<I', data[i:i+4])[0] for i in range(0, len(data), 4)]


def sign_extend(value, bits): #check sign bit
    if (value >> (bits - 1)) & 1:
        return value - (1 << bits)
    return value

def decode_inst(inst):
 
    code = inst & 0x7f
    reg_dest = (inst >> 7) & 0x1f
    func3 = (inst >> 12) & 0x7
    reg1 = (inst >> 15) & 0x1f
    reg2 = (inst >> 20) & 0x1f
    func7 = (inst >> 25) & 0x7f

    #register instructions R
    if code == 0x33:
        ops = {
            (0x0, 0x00): 'add',
            (0x0,0x20): 'sub',
            (0x1, 0x00): 'sll',
            (0x2,0x00): 'slt',
            (0x3, 0x00): 'sltu',
            (0x4, 0x00): 'xor',
            (0x5, 0x00): 'srl',
            (0x5, 0x20): 'sra',
            (0x6, 0x00): 'or',
            (0x7, 0x00): 'and'
        }

        # if not found
        inst = ops.get((func3, func7), 'unknown')
        return f"{inst} x{reg_dest}" + ", x" + str(reg1) + ", x" + str(reg2)

    #immediate instructions I
    elif code == 0x13 or code == 0x03:

        imm = sign_extend((inst >> 20), 12)

        if code == 0x03:
            # for load
            types = {0x0: 'lb', 0x1: 'lh', 0x2: 'lw',
         0x4: 'lbu', 0x5: 'lhu'}
            return types.get(func3, 'unknown') + " x" + str(reg_dest) + ", " + str(imm) + "(x" + str(reg1) + ")"
        else:
            ops = {
                0x0: 'addi',
                0x1: 'slli',
                0x2: 'slti',
                0x3: 'sltiu',
                0x4: 'xori',
                0x5: 'srai' if func7 == 0x20 else 'srli',
                0x6: 'ori',
                0x7: 'andi'
            }
            return ops.get(func3, 'unknown') + " x" + str(reg_dest) + ", x" + str(reg1) + ", " + str(imm)

    # store instructions S
    elif code == 0x23:
        imm = ((inst >> 25) << 5) | ((inst >> 7) & 0x1f)
        imm = sign_extend(imm, 12)

        stores = {
            0x0: 'sb',
            0x1: 'sh',
            0x2: 'sw'
        }

        return stores.get(func3, 'unknown') + " x" + str(reg2) + ", " + str(imm) + "(x" + str(reg1) + ")"

    #branch instructions B
    elif code == 0x63:
        #combine immediate parts and sign extend to 13 bits
        imm = ((inst >> 31) << 12) | ((inst >> 7 & 0x1e) << 11) | \
              ((inst >> 25 & 0x3f) << 5) | ((inst >> 8 & 0xf) << 1)
        imm = sign_extend(imm, 13)
        types = {
            0x0: 'beq',
            0x1: 'bne',
            0x4: 'blt',
            0x5: 'bge',
            0x6: 'bltu',
            0x7: 'bgeu'
        }
        return types.get(func3, 'unknown') + " x" + str(reg1) + ", x" + str(reg2) + ", " + str(imm)

    #lui/auipc instructions U
    elif code in [0x37, 0x17]:
        imm = inst & 0xfffff000
        return ("lui" if code == 0x37 else "auipc") + " x" + str(reg_dest) + ", " + str(imm >> 12)

    # jal instructions J
    elif code == 0x6f:
        imm = ((inst >> 31) & 0x1) << 20
        imm |= ((inst >> 12) & 0xff) << 12
        imm |= ((inst >> 20) & 0x1) << 11
        imm |= ((inst >> 21) & 0x3ff) << 1
        imm = sign_extend(imm, 21)

        return f"jal x{reg_dest}, {imm}"

    # JALR instruction
    elif code == 0x67:
        imm = sign_extend((inst >> 20), 12)
        return "jalr x" + str(reg_dest) + ", " + str(imm) + "(x" + str(reg1) + ")"

    #if nothing matched then return unknown
    return "unknown instruction"

if __name__ == "__main__":
    main()

# RISC-V Disassembler

A Python-based disassembler that converts RISC-V 32-bit binary machine code into human-readable assembly instructions.

## Features

- Supports all base RISC-V instruction formats: R, I, S, B, U, J
- Handles signed immediate extraction and sign-extension
- Implements instruction decoding including:
  - Arithmetic operations (ADD, SUB, XOR, OR, AND)
  - Control flow (JAL, JALR, branches)
  - Memory access (LW, SW, LB, etc.)
  - System instructions
- Output matches reference implementation specifications

## Usage

```bash
# to run the disassembler directly with Python
python3 riscv-sim.py <binary_file>

# to make it executable and run 
chmod +x riscv-sim
./riscv-sim <binary_file>
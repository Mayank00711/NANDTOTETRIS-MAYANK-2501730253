"""
Hack assembler: turns a Hack assembly program (.asm) into machine code (.hack).

Usage:   python assembler.py Prog.asm      ->  writes Prog.hack next to it

How it works (two readings of the file):
  First reading : remove comments and blank lines, and remember the
                  instruction number of every label like (LOOP).
  Second reading: translate each instruction into 16 bits.  New variables
                  get RAM addresses 16, 17, 18, ... in the order they appear.

Extra feature (K = 53, K mod 3 = 2):
  If the same label is written twice, a warning is printed.
"""

import sys

# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

# Symbols that exist before the program is read: R0..R15 and the named ones.
PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for i in range(16):
    PREDEFINED["R" + str(i)] = i

# comp field: 7 bits = a-bit + 6 ALU control bits (a=1 means "use M instead of A")
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}

# dest field: 3 bits = which of A, D, M receive the result
DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

# jump field: 3 bits = jump if (result < 0), (result = 0), (result > 0)
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_line(line):
    """Remove the comment and ALL spaces from one line of assembly."""
    if "//" in line:
        line = line.split("//")[0]
    return "".join(line.split())


def translate_a_instruction(line, symbols, next_variable):
    """'@xxx' -> 16 bits. Returns (binary_text, next_free_variable_address)."""
    name = line[1:]
    if name.isdigit():
        value = int(name)
    else:
        if name not in symbols:               # a brand-new variable
            symbols[name] = next_variable
            next_variable += 1
        value = symbols[name]
    return format(value, "016b"), next_variable


def translate_c_instruction(line):
    """'dest=comp;jump' -> '111' + comp + dest + jump."""
    dest = ""
    jump = ""
    comp = line
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


# ---------------------------------------------------------------------------
# The two readings
# ---------------------------------------------------------------------------

def first_reading(lines):
    """Return (instructions, symbols).

    instructions : the cleaned instruction lines, with labels removed
    symbols      : predefined symbols + every label -> its instruction number
    """
    symbols = dict(PREDEFINED)
    instructions = []
    label_lines = {}          # label -> file line number where it was first written

    for line_number, raw in enumerate(lines, start=1):
        line = clean_line(raw)
        if line == "":
            continue                                   # blank or comment-only line
        if line.startswith("("):                       # a label like (LOOP)
            label = line[1:-1]
            if label in label_lines:
                # EXTRA FEATURE (K mod 3 = 2): warn when a label is written twice.
                # We keep the first definition so the output stays predictable.
                print("Warning: line " + str(line_number) + ": label (" + label
                      + ") was already written on line " + str(label_lines[label])
                      + " - keeping the first one")
            else:
                label_lines[label] = line_number
                symbols[label] = len(instructions)     # the NEXT instruction's number
        else:
            instructions.append(line)

    return instructions, symbols


def second_reading(instructions, symbols):
    """Translate every instruction into a 16-character string of 0s and 1s."""
    output = []
    next_variable = 16

    for line in instructions:
        if line.startswith("@"):
            binary, next_variable = translate_a_instruction(line, symbols, next_variable)
        else:
            binary = translate_c_instruction(line)
        output.append(binary)

    return output


def assemble(lines):
    """Assemble a list of asm lines. Returns the list of 16-bit strings."""
    instructions, symbols = first_reading(lines)
    return second_reading(instructions, symbols)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        return

    asm_path = sys.argv[1]
    with open(asm_path) as f:
        lines = f.read().splitlines()

    binary_lines = assemble(lines)

    hack_path = asm_path[:-4] + ".hack"
    with open(hack_path, "w") as f:
        f.write("\n".join(binary_lines) + "\n")

    print("Wrote " + str(len(binary_lines)) + " instructions to " + hack_path)


if __name__ == "__main__":
    main()

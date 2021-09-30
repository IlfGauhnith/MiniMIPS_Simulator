from operator import xor

class AssemblyInstruction:
    def __init__(self, operation, reg_first=None, reg_second=None, reg_dest=None, constant=None, shamt=None):
        self.operation = operation
        self.first_reg = reg_first
        self.second_reg = reg_second
        self.dest_reg = reg_dest
        self.constant = constant
        self.shamt = shamt

    def __str__(self):
        address_access_instructions = ["lb", "lbu", "sb", "lw", "sw"]
        representation = f"{self.operation}"
        if representation in address_access_instructions:
            if self.first_reg is not None:
                representation = representation + f" ${self.first_reg.code},"

            if self.constant is not None:
                representation = representation + f" {self.constant}"

            if self.second_reg is not None:
                representation = representation + f"(${self.second_reg.code})"

        else:
            if self.dest_reg is not None:
                representation = representation + f" ${self.dest_reg.code},"

            if self.first_reg is not None:
                representation = representation + f" ${self.first_reg.code},"

            if self.second_reg is not None:
                representation = representation + f" ${self.second_reg.code},"

            if self.shamt is not None:
                representation = representation + f" {self.shamt},"

            if self.constant is not None:
                representation = representation + f" {self.constant}"

        if representation[-1] == ',':
            representation = representation[:-1]

        return representation

class MIPS:

    class Register:
        def __init__(self, assembly_name, code, preserve_value, reserved):
            self.assembly_name = assembly_name
            self.code = code
            self.value = 0
            self.preserveValue = preserve_value
            self.reserved = reserved

        def __str__(self):
            representation = f"${self.code}={self.value}"
            return representation

    def __init__(self):
        self.Reg_dict = {
            "00000": MIPS.Register("zero", 0, None, False),
            "00001": MIPS.Register("at", 1, False, False),
            "00010": MIPS.Register("v0", 2, False, False),
            "00011": MIPS.Register("v1", 3, False, False),
            "00100": MIPS.Register("a0", 4, False, False),
            "00101": MIPS.Register("a1", 5, False, False),
            "00110": MIPS.Register("a2", 6, False, False),
            "00111": MIPS.Register("a3", 7, False, False),
            "01000": MIPS.Register("t0", 8, False, False),
            "01001": MIPS.Register("t1", 9, False, False),
            "01010": MIPS.Register("t2", 10, False, False),
            "01011": MIPS.Register("t3", 11, False, False),
            "01100": MIPS.Register("t4", 12, False, False),
            "01101": MIPS.Register("t5", 13, False, False),
            "01110": MIPS.Register("t6", 14, False, False),
            "01111": MIPS.Register("t7", 15, False, False),
            "10000": MIPS.Register("s0", 16, True, False),
            "10001": MIPS.Register("s1", 17, True, False),
            "10010": MIPS.Register("s2", 18, True, False),
            "10011": MIPS.Register("s3", 19, True, False),
            "10100": MIPS.Register("s4", 20, True, False),
            "10101": MIPS.Register("s5", 21, True, False),
            "10110": MIPS.Register("s6", 22, True, False),
            "10111": MIPS.Register("s7", 23, True, False),
            "11000": MIPS.Register("t8", 24, False, False),
            "11001": MIPS.Register("t9", 25, False, False),
            "11010": MIPS.Register("k0", 26, False, True),
            "11011": MIPS.Register("k1", 27, False, True),
            "11100": MIPS.Register("gp", 28, True, False),
            "11101": MIPS.Register("sp", 29, True, False),
            "11110": MIPS.Register("fp", 30, True, False),
            "11111": MIPS.Register("ra", 31, False, False),
            "HI": MIPS.Register("hi", None, True, True),
            "LO": MIPS.Register("lo", None, True, True)
        }
        self.assembly_instructions = []
        self.memory = [0 for i in range(0, 127)]
        self.memory_pointer = 0
        self.program_counter = 0

    R_fcode_dict = {
        "100000": "add",
        "100010": "sub",
        "101010": "slt",
        "100100": "and",
        "100101": "or",
        "100110": "xor",
        "100111": "nor",
        "010000": "mfhi",
        "010010": "mflo",
        "100001": "addu",
        "100011": "subu",
        "011000": "mult",
        "011001": "multu",
        "011010": "div",
        "011011": "divu",
        "000000": "sll",
        "000010": "srl",
        "000011": "sra",
        "000100": "sllv",
        "000110": "srlv",
        "000111": "srav",
        "001000": "jr",
        "001100": "syscall"
    }

    I_opcode_dict = {
        "001111": "lui",
        "001000": "addi",
        "001010": "slti",
        "001100": "andi",
        "001101": "ori",
        "001110": "xori",
        "100011": "lw",
        "101011": "sw",
        "000001": "bltz",
        "000100": "beq",
        "000101": "bne",
        "001001": "addiu",
        "100000": "lb",
        "100100": "lbu",
        "101000": "sb",
    }

    J_opcode_dict = {
        "000010": "j",
        "000011": "jal"
    }

    def __str__(self):
        representation = "MEM"
        representation = representation + str([f"{i}:{v}" for i, v in enumerate(self.memory) if v != 0 and not isinstance(v, AssemblyInstruction)]).replace(",", ";") + "\n"
        representation = representation + "REGS["

        for key in self.Reg_dict.keys():
            if key in ["HI", "LO"]:
                continue
            representation = representation + f"{self.Reg_dict[key]};"

        representation = representation[:-1]
        representation = representation + "]"

        return representation

    def hex_to_binary_instructions(self, path):
        # Este método retorna uma lista de strings com bits representando a conversão das instruções em hexadecimal do
        # arquivo.

        file = open(path, "r")
        binary_instructions = file.read().splitlines()
        file.close()

        for i, instruction in enumerate(binary_instructions):
            decimal_representation = int(instruction, 16)
            binary_representation = bin(decimal_representation)
            binary_representation = binary_representation[2:]

            # Completar os bits menos significativos.
            if len(binary_representation) < 32:
                offset = 32 - len(binary_representation)
                binary_representation = ("0" * offset) + binary_representation

            binary_instructions[i] = binary_representation

        return binary_instructions

    def binary_to_assembly(self, b_instructions):
        for bin in b_instructions:
            if bin[:6] == "000000":
                self.assembly_instructions.append(self.translate_R_instruction(bin))
            elif bin[:6] == "000010" or bin[:6] == "000011":
                self.assembly_instructions.append(self.translate_J_instruction(bin))
            else:
                self.assembly_instructions.append(self.translate_I_instruction(bin))

    def translate_J_instruction(self, b_instruction):
        assembly_instruction = AssemblyInstruction(MIPS.J_opcode_dict[b_instruction[0:6]])
        assembly_instruction.constant = int(b_instruction[7:32], 2)

        return assembly_instruction

    def translate_I_instruction(self, b_instruction):
        address_access_instructions = ["lb", "lbu", "sb", "lw", "sw"]
        conditional_instructions = ["bltz", "beq", "bne"]

        assembly_instruction = AssemblyInstruction(MIPS.I_opcode_dict[b_instruction[0:6]])

        if assembly_instruction.operation in address_access_instructions:
            #rs
            if b_instruction[11:16] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[11:16]]

            #rt
            if b_instruction[6:11] != "00000":
                assembly_instruction.second_reg = self.Reg_dict[b_instruction[6:11]]

            # immediate operand
            if b_instruction[16:32] != "00000":
                assembly_instruction.constant = int(b_instruction[16:32], 2)

        elif assembly_instruction.operation in conditional_instructions:
            # rs
            if b_instruction[6:11] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[6:11]]

            # rt
            if b_instruction[11:16] != "00000":
                assembly_instruction.second_reg = self.Reg_dict[b_instruction[11:16]]

            # immediate operand
            if b_instruction[16:32] != "00000":
                assembly_instruction.constant = int(b_instruction[16:32], 2)

        else:
            # rt (destination)
            if b_instruction[11:16] != "00000":
                assembly_instruction.dest_reg = self.Reg_dict[b_instruction[11:16]]

            # rs
            if b_instruction[6:11] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[6:11]]

            # immediate operand
            if b_instruction[16:32] != "00000":
                assembly_instruction.constant = int(b_instruction[16:32], 2)

        return assembly_instruction

    def translate_R_instruction(self, b_instruction):
        shift_with_regs_instructions = ["sllv", "srlv", "srav"]
        shift_with_shamt = ["sll", "srl", "sra"]
        assembly_instruction = AssemblyInstruction(MIPS.R_fcode_dict[b_instruction[26:32]])

        if assembly_instruction.operation in shift_with_regs_instructions:
            # rd
            if b_instruction[16:21] != "00000":
                assembly_instruction.dest_reg = self.Reg_dict[b_instruction[16:21]]

            # rt
            if b_instruction[11:16] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[11:16]]

            # rs
            if b_instruction[6:11] != "00000":
                assembly_instruction.second_reg = self.Reg_dict[b_instruction[6:11]]
        elif assembly_instruction.operation in shift_with_shamt:
            # rd
            if b_instruction[16:21] != "00000":
                assembly_instruction.dest_reg = self.Reg_dict[b_instruction[16:21]]

            # rs
            if b_instruction[6:11] != "00000":
                assembly_instruction.second_reg = self.Reg_dict[b_instruction[6:11]]

            # rt
            if b_instruction[11:16] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[11:16]]

            # sa
            if b_instruction[21:26] != "00000":
                assembly_instruction.shamt = int(b_instruction[21:26], 2)

        else:
            # rd
            if b_instruction[16:21] != "00000":
                assembly_instruction.dest_reg = self.Reg_dict[b_instruction[16:21]]

            # rs
            if b_instruction[6:11] != "00000":
                assembly_instruction.first_reg = self.Reg_dict[b_instruction[6:11]]

            # rt
            if b_instruction[11:16] != "00000":
                assembly_instruction.second_reg = self.Reg_dict[b_instruction[11:16]]

            # sa
            if b_instruction[21:26] != "00000":
                assembly_instruction.shamt = int(b_instruction[21:26], 2)

        return assembly_instruction

    def write_in_memory(self, value, address=None):
        if address is None:
            self.memory[self.memory_pointer] = value
            self.memory_pointer += 1
        else:
            self.memory[address] = value

    def simulate(self, input_path, output_path):
        binary = self.hex_to_binary_instructions(input_path)
        self.binary_to_assembly(binary)
        file = open(output_path, "w")

        for instruction in self.assembly_instructions:
            self.write_in_memory(instruction)

        while isinstance(self.memory[self.program_counter], AssemblyInstruction):
            instruction:AssemblyInstruction = self.memory[self.program_counter]
            file.write(str(instruction)+"\n")

            if instruction.operation == "add":
                self.add(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "sub":
                self.sub(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "slt":
                self.slt(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "and":
                self.AND(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "or":
                self.OR(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "xor":
                self.XOR(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "nor":
                self.NOR(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "mfhi":
                self.mfhi(instruction.dest_reg)
            elif instruction.operation == "mflo":
                self.mflo(instruction.dest_reg)
            elif instruction.operation == "addu":
                self.addu(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "subu":
                self.subu(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "mult":
                self.mult(instruction.first_reg, instruction.second_reg)
            elif instruction.operation == "multu":
                self.multu(instruction.first_reg, instruction.second_reg)
            elif instruction.operation == "div":
                self.div(instruction.first_reg, instruction.second_reg)
            elif instruction.operation == "divu":
                self.divu(instruction.first_reg, instruction.second_reg)
            elif instruction.operation == "sll":
                self.sll(instruction.first_reg, instruction.dest_reg, instruction.shamt)
            elif instruction.operation == "srl":
                self.srl(instruction.first_reg, instruction.dest_reg, instruction.shamt)
            elif instruction.operation == "sra":
                self.sra(instruction.first_reg, instruction.dest_reg, instruction.shamt)
            elif instruction.operation == "sllv":
                self.sllv(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "srlv":
                self.srlv(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "srav":
                self.srav(instruction.first_reg, instruction.second_reg, instruction.dest_reg)
            elif instruction.operation == "addi":
                self.addi(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "slti":
                self.slti(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "andi":
                self.andi(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "ori":
                self.ori(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "xori":
                self.xori(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "addiu":
                self.addiu(instruction.first_reg, instruction.constant, instruction.dest_reg)
            elif instruction.operation == "jr":
                self.jr(instruction.first_reg)
            elif instruction.operation == "lui":
                self.lui(instruction.dest_reg, instruction.constant)
            elif instruction.operation == "lw":
                self.lw(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "sw":
                self.sw(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "bltz":
                self.bltz(instruction.first_reg, instruction.constant)
            elif instruction.operation == "beq":
                self.beq(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "bne":
                self.bne(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "lb":
                self.lb(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "sb":
                self.sb(instruction.first_reg, instruction.second_reg, instruction.constant)
            elif instruction.operation == "j":
                self.j(instruction.constant)
            elif instruction.operation == "jal":
                self.jal(instruction.constant)

            else:
                self.program_counter += 1
                continue

            self.program_counter += 1
            file.write(str(self)+"\n")

    def add(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value + second_reg.value

    def sub(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value - second_reg.value

    def slt(self, first_reg, second_reg, dest_reg):
        if first_reg.value < second_reg.value:
            dest_reg.value = 0
        else:
            dest_reg.value = 0

    def AND(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value & second_reg.value

    def OR(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value | second_reg.value

    def XOR(self, first_reg, second_reg, dest_reg):
        dest_reg.value = xor(first_reg.value, second_reg.value)

    def NOR(self, first_reg, second_reg, dest_reg):
        dest_reg.value = ~(first_reg.value|second_reg.value)

    def mfhi(self, dest_reg):
        dest_reg.value = self.Reg_dict["HI"].value

    def mflo(self, dest_reg):
        dest_reg.value = self.Reg_dict["LO"].value

    def addu(self, first_reg, second_reg, dest_reg):
        dest_reg.value = abs(first_reg.value) + abs(second_reg.value)

    def subu(self, first_reg, second_reg, dest_reg):
        dest_reg.value = abs(first_reg.value) - abs(second_reg.value)

    def mult(self, first_reg, second_reg):
        res = '{:064b}'.format(first_reg.value * second_reg.value)
        hi, lo = res[0:32], res[32:65]

        self.Reg_dict['HI'].value = int(hi, 2)
        self.Reg_dict['LO'].value = int(lo, 2)

    def multu(self, first_reg, second_reg):
        res = '{:064b}'.format(abs(first_reg.value * second_reg.value))
        hi, lo = res[0:32], res[32:65]

        self.Reg_dict['HI'].value = int(hi, 2)
        self.Reg_dict['LO'].value = int(lo, 2)

    def div(self, first_reg, second_reg):
        quotient = 0 if second_reg.value == 0 else first_reg.value//second_reg.value
        remainder = 0 if second_reg.value == 0 else first_reg.value % second_reg.value

        self.Reg_dict['HI'].value = remainder
        self.Reg_dict['LO'].value = quotient

    def divu(self, first_reg, second_reg):
        quotient = 0 if second_reg.value == 0 else abs(first_reg.value // second_reg.value)
        remainder = 0 if second_reg.value == 0 else abs(first_reg.value) % abs(second_reg.value)

        self.Reg_dict['HI'].value = remainder
        self.Reg_dict['LO'].value = quotient

    def sll(self, first_reg, dest_reg, shamt):
        dest_reg.value = first_reg.value << shamt

    def srl(self, first_reg, dest_reg, shamt):
        dest_reg.value = first_reg.value >> shamt

    def sra(self, first_reg, dest_reg, shamt):
        dest_reg.value = first_reg.value >> shamt

    def sllv(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value << second_reg.value

    def srlv(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value >> second_reg.value

    def srav(self, first_reg, second_reg, dest_reg):
        dest_reg.value = first_reg.value >> second_reg.value

    def addi(self, first_reg, constant, dest_reg):
        dest_reg.value = first_reg.value + constant

    def slti(self, first_reg, constant, dest_reg):
        if first_reg.value < constant:
            dest_reg.value = 1
        else:
            dest_reg.value = 0

    def andi(self, first_reg, constant, dest_reg):
        dest_reg.value = first_reg.value & constant

    def ori(self, first_reg, constant, dest_reg):
        dest_reg.value = first_reg.value | constant

    def xori(self, first_reg, constant, dest_reg):
        dest_reg.value = xor(first_reg.value, constant)

    def addiu(self, first_reg, constant, dest_reg):
        dest_reg.value = abs(first_reg.value) + abs(constant)

    def jr(self, first_reg):
        self.program_counter = first_reg.value

    def lui(self, dest_reg, constant):
        word = '{:016b}'.format(constant) + '{:016b}'.format(0)
        dest_reg.value = int(word, 2)

    def lw(self, first_reg, second_reg, constant):
        first_reg.value = self.memory[second_reg.value + constant]

    def sw(self, first_reg, second_reg, constant):
        self.memory[second_reg.value + constant] = first_reg.value

    def bltz(self, first_reg, constant):
        if first_reg.value < 0:
            self.program_counter += constant

    def beq(self, first_reg, second_reg, constant):
        if first_reg.value == second_reg.value:
            self.program_counter += constant

    def bne(self, first_reg, second_reg, constant):
        if first_reg.value != second_reg.value:
            self.program_counter += constant

    def lb(self, first_reg, second_reg, constant):
        word = ""
        upper_byte = '{:032b}'.format(self.memory[second_reg.value+constant])[0:8]
        if upper_byte[0] == "1":
            word = '{:024b}'.format(1).replace('0', '1') + upper_byte
        else:
            word = '{:024b}'.format(0) + upper_byte

        first_reg.value = int(word, 2)

    def sb(self, first_reg, second_reg, constant):
        word = ""
        upper_byte = '{:032b}'.format(self.memory[first_reg.value+constant])[0:8]

        if upper_byte[0] == "1":
            word = '{:024b}'.format(1).replace('0', '1') + upper_byte
        else:
            word = '{:024b}'.format(0) + upper_byte

        self.memory[second_reg.value + constant] = word

    def j(self, constant):
        self.program_counter = constant

    def jal(self, constant):
        self.Reg_dict["11111"].value = self.program_counter + 1
        self.program_counter = constant

if __name__ == '__main__':
    mips = MIPS()
    mips.simulate("input/input.txt", "output/output.txt")
    print(mips)
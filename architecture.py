"""Namespace for all CPU instruction set and architectural related information"""

from csmstructs import AddressingMode, Instruction, Register

class instructions:
    """Namespace for all instruction related data"""

    HLT: Instruction  =   Instruction("HLT",    0,    0)
    ADD: Instruction  =   Instruction("ADD",    1,    2)
    SUB: Instruction  =   Instruction("SUB",    2,    2)
    STA: Instruction  =   Instruction("STA",    3,    2)
    NOP: Instruction  =   Instruction("NOP",    4,    0)
    LDA: Instruction  =   Instruction("LDA",    5,    2)
    BRA: Instruction  =   Instruction("BRA",    6,    2)
    BRZ: Instruction  =   Instruction("BRZ",    7,    2)
    BRP: Instruction  =   Instruction("BRP",    8,    2)
    INP: Instruction  =   Instruction("INP",    9,    1)
    OUT: Instruction  =   Instruction("OUT",   10,    1)
    OUTC: Instruction =  Instruction("OUTC",   11,    1)
    OUTB: Instruction =  Instruction("OUTB",   12,    1)
    AND: Instruction  =   Instruction("AND",   13,    2) 
    OR: Instruction   =    Instruction("OR",   14,    2) 
    NOT: Instruction  =   Instruction("NOT",   15,    2) 
    XOR: Instruction  =   Instruction("XOR",   16,    2) 
    LSL: Instruction  =   Instruction("LSL",   17,    2) 
    LSR: Instruction  =   Instruction("LSR",   18,    2) 
    ASL: Instruction  =   Instruction("ASL",   19,    2) 
    ASR: Instruction  =   Instruction("ASR",   20,    2) 
    CSL: Instruction  =   Instruction("CSL",   21,    2) 
    CSR: Instruction  =   Instruction("CSR",   22,    2) 
    CSLC: Instruction =  Instruction("CSLC",   23,    2) 
    CSRC: Instruction =  Instruction("CSRC",   24,    2) 
    CALL: Instruction =  Instruction("CALL",   25,    1)
    RET: Instruction  =   Instruction("RET",   26,    0)

    INSTRUCTION_SET: list[Instruction] = [HLT, ADD, SUB, STA, NOP, LDA, BRA, BRZ,
                                          BRP, INP, OUT, OUTC, OUTB, AND, OR,
                                          NOT, XOR, LSL, LSR, ASL, ASR, CSL, CSR,
                                          CSLC, CSRC, CALL, RET]

    NON_IMMEDIATE_MODE_INSTRUCTIONS: list[Instruction] = [STA, BRA, BRZ, BRP, CALL]

    NUMBER_INSTRUCTIONS: int = 27

    @staticmethod
    def get_instruction(instruction: str) -> Instruction | None:
        """Will return the instruction related data for a given instruction
           Will return None if the argument supplied isn't a valid instruction"""

        for i in instructions.INSTRUCTION_SET:

            if i.mnemonic == instruction:

                return i
        
        return None

    # Unique instruction-like keyword
    DAT: str = "DAT"

class registers:
    """Namespace for all register related data"""

    #                                                "Register",     (Variations)      Offset
    # The offset is needed when calculating the opcode of a register relative to the GPR opcodes
    ACCUMULATOR: Register     =  Register("ACC", ["ACC", "ACCUMULATOR"],    1)
    PROGRAM_COUNTER: Register =  Register("PC",  ["PC", "PROGRAMCOUNTER"],    2)
    RETURN_REGISTER: Register =  Register("RR",  ["RR", "RETURNREGISTER"],  3)
    FLAGS_REGISTER: Register  =  Register("FR",  ["FR", "FLAGSREGISTER"],   4)

    SPR: list[Register] = [ACCUMULATOR, PROGRAM_COUNTER, RETURN_REGISTER, FLAGS_REGISTER]

    # General Purpose Register
    GPR: Register = Register("REG", ["REG", "R", "REGISTER"], 0)

    NUMBER_SPRS: int = 4

    @staticmethod
    def get_spr(register: str) -> Register | None:
        """Will return the register related data for a given register
           Will return None if the argument supplied isn't a valid register variant"""

        for r in registers.SPR:

            if register in r.variants:

                return r

        return None

class addressingmodes:
    """Namespace for all addressing mode related data"""

    REGISTER: AddressingMode  = AddressingMode('%', ['%', "REGISTER"], 0)
    DIRECT: AddressingMode    = AddressingMode('@', ['@', "DIRECT"], 1)
    INDIRECT: AddressingMode  = AddressingMode('>', ['>', "INDIRECT"], 2)
    IMMEDIATE: AddressingMode = AddressingMode('#', ['#', "IMMEDIATE"], 3)

    NUMBER_MODES: int = 4

    ADDRESSING_MODES: list[AddressingMode] = [REGISTER, DIRECT, INDIRECT, IMMEDIATE]

    @staticmethod
    def get_addressing_mode(addressing_mode: str) -> AddressingMode | None:
        """Will return the addressing mode related data for a given addressing mode
           Will return None if the argument supplied isn't a valid addressing mode variant"""

        for am in addressingmodes.ADDRESSING_MODES:

            if addressing_mode in am.variants:

                return am

        return None

"""Namespace for all CPU instruction set and architectural related information"""

from csmstructs import AddressingMode, Instruction, Register
from meta import namespace

class instructions(metaclass=namespace):
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

    INSTRUCTION_SET: dict[str, Instruction] = {
        HLT.mnemonic: HLT,
        ADD.mnemonic: ADD,
        SUB.mnemonic: SUB,
        STA.mnemonic: SUB,
        NOP.mnemonic: NOP,
        LDA.mnemonic: LDA,
        BRA.mnemonic: BRA,
        BRZ.mnemonic: BRZ,
        BRP.mnemonic: BRP,
        INP.mnemonic: INP,
        OUT.mnemonic: OUT,
        OUTC.mnemonic: OUTC,
        OUTB.mnemonic: OUTB,
        AND.mnemonic: AND,
        OR.mnemonic: OR,
        NOT.mnemonic: NOT,
        XOR.mnemonic: XOR,
        LSL.mnemonic: LSL,
        LSR.mnemonic: LSR,
        ASL.mnemonic: ASL,
        ASR.mnemonic: ASR,
        CSL.mnemonic: CSL,
        CSR.mnemonic: CSR,
        CSLC.mnemonic: CSLC,
        CSRC.mnemonic: CSRC,
        CALL.mnemonic: CALL,
        RET.mnemonic: RET,
    }

    NON_IMMEDIATE_MODE_INSTRUCTIONS: list[Instruction] = [STA, BRA, BRZ, BRP, CALL]

    NUMBER_INSTRUCTIONS: int = len(INSTRUCTION_SET)

    # Unique instruction-like keyword
    DAT: str = "DAT"

class registers(metaclass=namespace):
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

    NUMBER_SPRS: int = len(SPR)

    SPECIAL_PURPOSE_REGISTERS: dict[str, Register] = {
        ACCUMULATOR.variants[0]: ACCUMULATOR,
        ACCUMULATOR.variants[1]: ACCUMULATOR,
        PROGRAM_COUNTER.variants[0]: PROGRAM_COUNTER,
        PROGRAM_COUNTER.variants[1]: PROGRAM_COUNTER,
        RETURN_REGISTER.variants[0]: RETURN_REGISTER,
        RETURN_REGISTER.variants[1]: RETURN_REGISTER,
        FLAGS_REGISTER.variants[0]: FLAGS_REGISTER,
        FLAGS_REGISTER.variants[1]: FLAGS_REGISTER,
    }

class addressingmodes(metaclass=namespace):
    """Namespace for all addressing mode related data"""

    REGISTER: AddressingMode  = AddressingMode('%', ['%', "REGISTER"], 0)
    DIRECT: AddressingMode    = AddressingMode('@', ['@', "DIRECT"], 1)
    INDIRECT: AddressingMode  = AddressingMode('>', ['>', "INDIRECT"], 2)
    IMMEDIATE: AddressingMode = AddressingMode('#', ['#', "IMMEDIATE"], 3)

    NUMBER_MODES: int = 4

    ADDRESSING_MODES: dict[str, AddressingMode] = {
        REGISTER.variants[0]: REGISTER,
        REGISTER.variants[1]: REGISTER,
        DIRECT.variants[0]: DIRECT,
        DIRECT.variants[1]: DIRECT,
        INDIRECT.variants[0]: INDIRECT,
        INDIRECT.variants[1]: INDIRECT,
        IMMEDIATE.variants[0]: IMMEDIATE,
        IMMEDIATE.variants[1]: IMMEDIATE,
    }

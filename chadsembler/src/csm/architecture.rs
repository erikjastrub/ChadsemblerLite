use crate::csm::structs::{Instruction, Register, AddressingMode};

/// Namespace for all instruction related data
pub mod instructions {

    use super::*;

    pub const HLT: Instruction  =  Instruction{  mnemonic:  "HLT",   opcode:  0,  operands: 0  };
    pub const ADD: Instruction  =  Instruction{  mnemonic:  "ADD",   opcode:  1,  operands: 2  };
    pub const SUB: Instruction  =  Instruction{  mnemonic:  "SUB",   opcode:  2,  operands: 2  };
    pub const STA: Instruction  =  Instruction{  mnemonic:  "STA",   opcode:  3,  operands: 2  };
    pub const NOP: Instruction  =  Instruction{  mnemonic:  "NOP",   opcode:  4,  operands: 0  };
    pub const LDA: Instruction  =  Instruction{  mnemonic:  "LDA",   opcode:  5,  operands: 2  };
    pub const BRA: Instruction  =  Instruction{  mnemonic:  "BRA",   opcode:  6,  operands: 2  };
    pub const BRZ: Instruction  =  Instruction{  mnemonic:  "BRZ",   opcode:  7,  operands: 2  };
    pub const BRP: Instruction  =  Instruction{  mnemonic:  "BRP",   opcode:  8,  operands: 2  };
    pub const INP: Instruction  =  Instruction{  mnemonic:  "INP",   opcode:  9,  operands: 1  };
    pub const OUT: Instruction  =  Instruction{  mnemonic:  "OUT",   opcode: 10,  operands: 1  };
    pub const OUTC: Instruction =  Instruction{  mnemonic:  "OUTC",  opcode: 11,  operands: 1  };
    pub const OUTB: Instruction =  Instruction{  mnemonic:  "OUTB",  opcode: 12,  operands: 1  };
    pub const AND: Instruction  =  Instruction{  mnemonic:  "AND",   opcode: 13,  operands: 2  };
    pub const OR: Instruction   =  Instruction{  mnemonic:  "OR",    opcode: 14,  operands: 2  };
    pub const NOT: Instruction  =  Instruction{  mnemonic:  "NOT",   opcode: 15,  operands: 2  };
    pub const XOR: Instruction  =  Instruction{  mnemonic:  "XOR",   opcode: 16,  operands: 2  };
    pub const LSL: Instruction  =  Instruction{  mnemonic:  "LSL",   opcode: 17,  operands: 2  };
    pub const LSR: Instruction  =  Instruction{  mnemonic:  "LSR",   opcode: 18,  operands: 2  };
    pub const ASL: Instruction  =  Instruction{  mnemonic:  "ASL",   opcode: 19,  operands: 2  };
    pub const ASR: Instruction  =  Instruction{  mnemonic:  "ASR",   opcode: 20,  operands: 2  };
    pub const CSL: Instruction  =  Instruction{  mnemonic:  "CSL",   opcode: 21,  operands: 2  };
    pub const CSR: Instruction  =  Instruction{  mnemonic:  "CSR",   opcode: 22,  operands: 2  };
    pub const CSLC: Instruction =  Instruction{  mnemonic:  "CSLC",  opcode: 23,  operands: 2  };
    pub const CSRC: Instruction =  Instruction{  mnemonic:  "CSRC",  opcode: 24,  operands: 2  };
    pub const CALL: Instruction =  Instruction{  mnemonic:  "CALL",  opcode: 25,  operands: 1  };
    pub const RET: Instruction  =  Instruction{  mnemonic:  "RET",   opcode: 26,  operands: 0  };

    pub const NUMBER_INSTRUCTIONS: usize = INSTRUCTION_SET.len();

    pub const INSTRUCTION_SET: phf::Map<&str, &Instruction> = phf::phf_map!{

        "HLT"   =>  &HLT, 
        "ADD"   =>  &ADD, 
        "SUB"   =>  &SUB, 
        "STA"   =>  &STA, 
        "NOP"   =>  &NOP, 
        "LDA"   =>  &LDA, 
        "BRA"   =>  &BRA, 
        "BRZ"   =>  &BRZ,
        "BRP"   =>  &BRP, 
        "INP"   =>  &INP, 
        "OUT"   =>  &OUT, 
        "OUTC"  =>  &OUTC, 
        "OUTB"  =>  &OUTB, 
        "AND"   =>  &AND, 
        "OR"    =>  &OR,
        "NOT"   =>  &NOT, 
        "XOR"   =>  &XOR, 
        "LSL"   =>  &LSL, 
        "LSR"   =>  &LSR, 
        "ASL"   =>  &ASL, 
        "ASR"   =>  &ASR, 
        "CSL"   =>  &CSL, 
        "CSR"   =>  &CSR,
        "CSLC"  =>  &CSLC, 
        "CSRC"  =>  &CSRC, 
        "CALL"  =>  &CALL, 
        "RET"   =>  &RET
    };

    pub const NON_IMMEDIATE_MODE_INSTRUCTIONS: phf::Set<&str> = phf::phf_set!{"STA", "BRA", "BRZ", "BRP", "CALL"};

    /// Unique instruction-like keyword
    pub const DAT: &str = "DAT";

}

/// Namespace for all register related data
pub mod registers {

    use super::*;

    // The offset is needed when calculating the opcode of a register relative to the GPR opcodes
    pub const ACCUMULATOR: Register     =  Register { register: "ACC",  offset: 1 };
    pub const PROGRAM_COUNTER: Register =  Register { register: "PC",   offset: 2 };
    pub const RETURN_REGISTER: Register =  Register { register: "RR",   offset: 3 };
    pub const FLAGS_REGISTER: Register  =  Register { register: "FR",   offset: 4 };

    pub const NUMBER_SP_REGISTERS: usize = 4;

    pub const GPR_VARIANTS: phf::Set<&str> = phf::phf_set!{"REG", "R", "REGISTER"};

    pub const SP_REGISTERS: phf::Map<&str, &Register> = phf::phf_map!{

        "ACC"             =>  &ACCUMULATOR,
        "ACCUMULATOR"     =>  &ACCUMULATOR,
        "PC"              =>  &PROGRAM_COUNTER,
        "PROGRAMCOUNTER"  =>  &PROGRAM_COUNTER,
        "RR"              =>  &RETURN_REGISTER,
        "RETURNREGISTER"  =>  &RETURN_REGISTER,
        "FR"              =>  &FLAGS_REGISTER,
        "FLAGSREGISTER"   =>  &FLAGS_REGISTER
    };
}

/// Namespace for all addressing mode related data
pub mod addressingmodes {

    use super::*;

    pub const REGISTER: AddressingMode = AddressingMode { symbol: "%",  opcode: 0 };
    pub const DIRECT: AddressingMode = AddressingMode { symbol: "@",    opcode: 1 };
    pub const INDIRECT: AddressingMode = AddressingMode { symbol: ">",  opcode: 2 };
    pub const IMMEDIATE: AddressingMode = AddressingMode { symbol: "#", opcode: 3 };

    pub const NUMBER_MODES: usize = 4;

    pub const ADDRESSING_MODES: phf::Map<&str, &AddressingMode> = phf::phf_map!{
        "%"          =>  &REGISTER, 
        "REGISTER"   =>  &REGISTER, 
        "@"          =>  &DIRECT,
        "DIRECT"     =>  &DIRECT, 
        ">"          =>  &INDIRECT,
        "INDIRECT"   =>  &INDIRECT,
        "#"          =>  &IMMEDIATE, 
        "IMMEDIATE"  =>  &IMMEDIATE
    };
}
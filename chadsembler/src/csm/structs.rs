use std::{{collections::HashMap}, process};
use crate::csm::binarystring;
use crate::csm::tokens::TypedToken;
use crate::csm::defaults::{SymbolTypes, sysdefaults};

/// mnemonic: The symbol that represents a machine code operation
/// opcode: the integer value the mnemonic is encoded to
/// operands: the number of values an instruction can operate on at most
pub struct Instruction {

    pub mnemonic: &'static str,
    pub opcode: isize,
    pub operands: isize
}

impl PartialEq for Instruction {

    fn eq(&self, other: &Self) -> bool {
        
        self.opcode == other.opcode
    }
}

/// register: the key symbol that represents a register
/// offset: a constant value used when determining the registers address
pub struct Register {

    pub register: &'static str,
    pub offset: usize
}

/// symbol: a character that represents the addressing mode
/// opcode: the integer value the addressing mode is encoded to
pub struct AddressingMode {

    pub symbol: &'static str,
    pub opcode: usize
}

/// value: the memory address the symbol points to
/// type: what type of data the symbol value is pointing to
pub struct Symbol {

    pub symbol_value: isize,
    pub symbol_type: SymbolTypes
}

/// tokens: the lexemes that were generated for a particular scope
/// symbol_table: a dictionary storing the local symbols of a scope
/// number_instructions: the amount of instructions within the scope
/// number_variables: the amount of variables within the scope
pub struct Scope<'a> {

    pub tokens: Vec<&'a TypedToken>,
    pub symbol_table: HashMap<&'a String, Symbol>,
    pub num_instructions: usize,
    pub num_variables: usize
}

/// addressing_mode: how the operand value should be interpreted
/// value: the value of the operand
pub struct Operand<'a> {

    pub addressing_mode: &'a TypedToken,
    pub operand_value: &'a TypedToken
}

/// Allows for a secure way to manipulate a pool of memory
pub struct Memory {

    number_registers: usize,
    architecture: usize,
    memory_pool: Vec<String>,
    memory_pool_length: usize
}

impl Memory {

    /// Constructor for a 'Memory' object
    pub fn new(number_registers: usize, architecture: usize, operand_bits: usize) -> Self {

        let default_value = "0".repeat(architecture as usize);
        
        //                                            Number Memory Addresses + Number Registers
        let memory_pool_length = 2usize.pow(operand_bits as u32-1) + number_registers;
        let memory_pool = vec![default_value; memory_pool_length as usize];

        Memory {

            number_registers,
            architecture,
            memory_pool,
            memory_pool_length
        }
    }

    /// Calculate the underlying address an abstract address corresponds to
    fn calculate_address(&self, address: isize) -> usize {

        let pointer = self.number_registers as isize + address;

        if pointer > -1 && pointer < self.memory_pool_length as isize {

            return pointer as usize;
        }

        eprintln!("Segmentation Fault: Attempted to access memory address {address}");
        process::exit(sysdefaults::EXIT_CODE);
    }

    /// Get the value at a given memory address
    pub fn get(&self, address: isize) -> String{

        self.memory_pool[self.calculate_address(address)].to_owned()
    }

    /// Place a binary string into a given memory address
    pub fn insert_binary(&mut self, address: isize, value: String) {

        let address = self.calculate_address(address);
        self.memory_pool[address] = value;
    }

    /// Place a value (converted to a binary string) into a given memory address
    pub fn insert_value(&mut self, address: isize, value: isize) {

        let address = self.calculate_address(address);

        self.memory_pool[address] = binarystring::signed_int(value, self.architecture as isize);
        
    }
}

/// address: the address in memory the value is located in
/// bits: the binary string equivalent of the value
/// value: the actual value
pub struct MemoryValue {

    pub address: isize, 
    pub bits: String,
    pub value: isize
}
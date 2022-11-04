#![allow(non_snake_case, unused_variables)]

use std::io::{self, Write};
use std::process::exit;

use crate::csm::binarystring;
use crate::csm::structs::{Memory, MemoryValue};
use crate::csm::architecture::registers;
use crate::csm::defaults::sysdefaults;

const ZERO: isize = '0' as isize;

pub struct MachineOperations<'a> {

    // PUBLIC so Memory can still be accessed while borrowed by the object
    pub memory: &'a mut Memory,

    program_counter_address: isize,
    flags_register_address: isize,
    return_register_address: isize,

    buffer: String,
    stdin: io::Stdin,
    stdout: io::Stdout    
}

impl<'a> MachineOperations<'a> {

    /// Constructor for a 'MachineOperations' object
    pub fn new(memory: &'a mut Memory, gprs: usize) -> Self {

        MachineOperations {
            memory,
            program_counter_address: (registers::PROGRAM_COUNTER.offset + gprs) as isize * -1,
            flags_register_address:  (registers::FLAGS_REGISTER.offset  + gprs) as isize * -1,
            return_register_address: (registers::RETURN_REGISTER.offset + gprs) as isize * -1,

            // Fields used for caching
            buffer: String::new(),
            stdin: io::stdin(),
            stdout: io::stdout()
        }
    }

    /// 0 Operands
    /// Suspends the execution of the program
    fn HLT(&mut self, source: MemoryValue, destination: MemoryValue) {

        std::process::exit(sysdefaults::EXIT_CODE);
    }

    /// 2 Operands
    /// Add the value in the source operand onto the value in the destination operand
    fn ADD(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_value(destination.address, destination.value + source.value);
    }

    /// 2 Operands
    /// Subtract the value in the source operand from the value in the destination operand
    fn SUB(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_value(destination.address, destination.value - source.value);
    }

    /// 2 Operands
    /// Store the value in the destination operand into the source operand
    fn STA(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(source.address, destination.bits);
    }

    /// 0 Operands
    /// Perform an empty operation, do nothing - wastes a clock cycle
    fn NOP(&mut self, source: MemoryValue, destination: MemoryValue) {

        // Performs no operation(s)
    }

    /// 2 Operands
    /// Load the value in the source operand onto the destination operand
    fn LDA(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(destination.address, source.bits);
    }

    /// 2 Operands
    /// Always branch to the address in the source operand, regardless what value is in the destination operand
    fn BRA(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_value(self.program_counter_address, source.address);
    }

    /// 2 Operands
    /// Branch to the address in the source operand if the value in the destination operand == 0
    fn BRZ(&mut self, source: MemoryValue, destination: MemoryValue) {

        if destination.value == 0 {
            
            self.memory.insert_value(self.program_counter_address, source.address);
        }
    }

    /// 2 Operands
    /// Branch to the address in the source operand if the value in the destination operand >= 0
    fn BRP(&mut self, source: MemoryValue, destination: MemoryValue) {

        if destination.value >= 0 {
            
            self.memory.insert_value(self.program_counter_address, source.address);
        }
    }

    /// 1 Operand
    /// Get and store integer input in address in the source operand
    fn INP(&mut self, source: MemoryValue, destination: MemoryValue) {
        
        self.buffer.clear();

        print!(">>>");

        // Flush the buffer to synchronise the output and ensure it is sequential
        self.stdout.flush().expect("Runtime Error: Failed to display output");

        if self.stdin.read_line(&mut self.buffer).is_err() {

            eprintln!("Runtime Error: Failed to get input");
            exit(sysdefaults::EXIT_CODE);
        }

        let value = match self.buffer.trim().parse() {

            Ok(v) => v,
            Err(_) => {

                eprintln!("Runtime Error: Input could not be interpreted as an integer");
                exit(sysdefaults::EXIT_CODE);
            }
        };

        self.memory.insert_value(source.address, value);
    }

    /// 1 Operand
    /// Output the value in source the source operand
    fn OUT(&mut self, source: MemoryValue, destination: MemoryValue) {

        println!("{}", source.value);

        // Flush the buffer to synchronise the output and ensure it is sequential
        self.stdout.flush().expect("Runtime Error: Failed to display output");
    }

    /// 1 Operand
    /// Output the value in the source operand encoded as a character
    fn OUTC(&mut self, source: MemoryValue, destination: MemoryValue) {

        print!("{}", source.value as u8 as char);

        // Flush the buffer to synchronise the output and ensure it is sequential
        self.stdout.flush().expect("Runtime Error: Failed to display output");
    }

    /// 1 Operand
    /// Output the bits in the source operand
    fn OUTB(&mut self, source: MemoryValue, destination: MemoryValue) {

        println!("{}", source.bits);

        // Flush the buffer to synchronise the output and ensure it is sequential
        self.stdout.flush().expect("Runtime Error: Failed to display output");
    }

    /// 2 Operands
    /// Bitwise AND on the destination operand with a mask of the source operand
    fn AND(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(destination.address, 
                                  binarystring::bitwise_and(&source.bits, &destination.bits))
    }

    /// 2 Operands
    /// Bitwise OR on the destination operand with a mask of the source operand
    fn OR(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(destination.address, 
                                  binarystring::bitwise_or(&source.bits, &destination.bits))
    }

    /// 2 Operands
    /// Bitwise NOT on the source operand with the result stored in the destination operand
    fn NOT(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(destination.address, 
                                  binarystring::bitwise_not(&source.bits));
    }

    /// 2 Operands
    /// Bitwise XOR on the destination operand with a mask of the source operand
    fn XOR(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(destination.address, 
                                  binarystring::bitwise_xor(&source.bits, &destination.bits))
    }

    /// 2 Operands
    /// Bitwise Logical Left Shift on the destination operand N times where N is the value in the source operand
    fn LSL(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some((carry, shift)) = binarystring::logical_shift_left(&destination.bits, source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Logical Right Shift on the destination operand N times where N is the value in the source operand
    fn LSR(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some((carry, shift)) = binarystring::logical_shift_right(&destination.bits, source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Arithmetic Left Shift on the destination operand N times where N is the value in the source operand
    fn ASL(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some((carry, shift)) = binarystring::arithmetic_shift_left(&destination.bits, source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Arithmetic Right Shift on the destination operand N times where N is the value in the source operand
    fn ASR(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some((carry, shift)) = binarystring::arithmetic_shift_right(&destination.bits, source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Circular Left Shift on the destination operand N times where N is the value in the source operand
    fn CSL(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some(shift) = binarystring::circular_shift_left(&destination.bits, source.value) {

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Circular Right Shift on the destination operand N times where N is the value in the source operand
    fn CSR(&mut self, source: MemoryValue, destination: MemoryValue) {

        if let Some(shift) = binarystring::circular_shift_right(&destination.bits, source.value) {

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Circular Left Shift with Carry on the destination operand N times where N is the value in the source operand
    fn CSLC(&mut self, source: MemoryValue, destination: MemoryValue) {

        let flags = self.memory.get(self.flags_register_address);


        if let Some((carry, shift)) = binarystring::circular_shift_left_carry(&destination.bits, &flags[flags.len()..], source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 2 Operands
    /// Bitwise Circular Right Shift with Carry on the destination operand N times where N is the value in the source operand
    fn CSRC(&mut self, source: MemoryValue, destination: MemoryValue) {

        let flags = self.memory.get(self.flags_register_address);


        if let Some((carry, shift)) = binarystring::circular_shift_right_carry(&destination.bits, &flags[flags.len()..], source.value) {

            self.memory.insert_value(self.flags_register_address, carry as isize - ZERO);

            self.memory.insert_binary(destination.address, shift);
        }
    }

    /// 1 Operand - Invoke the address held in the source operand
    // The RR is updated to store the current address
    fn CALL(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(self.return_register_address, 
                                  self.memory.get(self.program_counter_address));

        self.memory.insert_value(self.program_counter_address, source.address);
    }

    /// 0 Operands
    /// Returns from a procedure by setting the PC to the value in the RR
    fn RET(&mut self, source: MemoryValue, destination: MemoryValue) {

        self.memory.insert_binary(self.program_counter_address, 
                                  self.memory.get(self.return_register_address));
    }

    /// Will perform the operation associated with a given opcode and on the source and destination values
    pub fn execute(&mut self, opcode: usize, source: MemoryValue, destination: MemoryValue) {

        let machine_operations = [
            MachineOperations::HLT,  MachineOperations::ADD,  MachineOperations::SUB, MachineOperations::STA,
            MachineOperations::NOP,  MachineOperations::LDA,  MachineOperations::BRA, MachineOperations::BRZ,
            MachineOperations::BRP,  MachineOperations::INP,  MachineOperations::OUT, MachineOperations::OUTC,
            MachineOperations::OUTB, MachineOperations::AND,  MachineOperations::OR,  MachineOperations::NOT,
            MachineOperations::XOR,  MachineOperations::LSL,  MachineOperations::LSR, MachineOperations::ASL,
            MachineOperations::ASR,  MachineOperations::CSL,  MachineOperations::CSR, MachineOperations::CSLC,
            MachineOperations::CSRC, MachineOperations::CALL, MachineOperations::RET
        ];

        // Each instruction takes a source and destination operand regardless how many operands they use
        // This uniformity allows for each the instructions to be looked up and instantly executed
        //      without a need to check for edge cases
        machine_operations[opcode](self, source, destination);
    }
}

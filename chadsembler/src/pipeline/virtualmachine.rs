use std::collections::HashMap;
use crate::csm::binarystring;
use crate::csm::defaults::sysdefaults;
use crate::csm::structs::{Memory, MemoryValue};
use crate::csm::architecture::{registers, addressingmodes};
use crate::csm::machineoperations::MachineOperations;
use std::{time, thread::sleep};

/// Generate the introduction prompt for the Chadsembler which outlines the system and other useful information
#[inline]
fn intro_prompt(bits: &(usize, usize, usize, usize), number_gprs: usize) -> String {

    let (machine_operation_bits, addressing_mode_bits, operand_bits, architecture) = *bits;

    let max_operand_value = 2usize.pow(operand_bits as u32 -1) - 1;
    let max_address_value = 2usize.pow(architecture as u32 -1) - 1;
    let number_addresses  = 2usize.pow(operand_bits as u32 -1);

    let machine_code_format = format!("{a} {b} {c} {c}", a = "0".repeat(machine_operation_bits), b = "0".repeat(addressing_mode_bits), c = "0".repeat(operand_bits));

    format!(
"Chadsembly Version `{}`
{} bit operand, {} bit address bus,
Instruction Format: {}
Values -{}..{} in an Operand, Values -{}..{} in an address
{} (0..{}) memory addresses, {} (1..{}) GPRs
",
sysdefaults::CSM_VERSION, operand_bits, architecture, machine_code_format, max_operand_value, max_operand_value, 
max_address_value, max_address_value, number_addresses, number_addresses-1, number_gprs, number_gprs)
}

/// Return the address, bits and value an operand points to
fn resolve_operand(addressing_mode_opcode: usize, operand: &str, memory: &Memory, architecture: isize) -> MemoryValue {

    let operand_value = binarystring::read_signed_int(operand).unwrap();

    let mut binary_at_operand = memory.get(operand_value);
    let value_at_operand = binarystring::read_signed_int(&binary_at_operand).unwrap();

    if addressing_mode_opcode == addressingmodes::INDIRECT.opcode {

        binary_at_operand = memory.get(value_at_operand);

        MemoryValue {

            address: value_at_operand,
            value: binarystring::read_signed_int(&binary_at_operand).unwrap(),
            bits: binary_at_operand
        }
    
    } else if addressing_mode_opcode == addressingmodes::IMMEDIATE.opcode {

        MemoryValue {

            address: operand_value,
            bits: binarystring::signed_int(operand_value, architecture),
            value: operand_value
        }
    
    } else {

        MemoryValue {

            address: operand_value,
            bits: binary_at_operand,
            value: value_at_operand
        }
    } 
}

/// Split an instruction into its subparts and execute it
fn handle_instruction(machine_code: &str, memory: &Memory, bits: &(usize, usize, usize, usize)) -> (usize, MemoryValue, MemoryValue) {

    let (mut lower, mut upper) = (0, bits.0);
    let opcode = binarystring::read_unsigned_int(&machine_code[lower..upper]).unwrap() as usize;

    (lower, upper) = (upper, upper+bits.1);
    let addressing_mode = binarystring::read_unsigned_int(&machine_code[lower..upper]).unwrap() as usize;

    (lower, upper) = (upper, upper+bits.2);
    let source_operand = &machine_code[lower..upper];

    (lower, upper) = (upper, upper+bits.2);
    let destination_operand = &machine_code[lower..upper];

    (
        opcode,
        resolve_operand(addressing_mode, source_operand, memory, bits.3 as isize),
        resolve_operand(addressingmodes::REGISTER.opcode, destination_operand, memory, bits.3 as isize)
    )
}

/// Run the VirtualMachine
pub fn run(config_table: &HashMap<String, usize>, memory: &mut Memory, bits: &(usize, usize, usize, usize)) {

    let number_gprs = config_table[sysdefaults::REGISTERS_CONFIG.0];
    let clock_speed = config_table[sysdefaults::CLOCK_CONFIG.0];

    let program_counter_address = (registers::PROGRAM_COUNTER.offset + number_gprs) as isize * -1;
    let mut machine_operations = MachineOperations::new(memory, number_gprs);

    let mut program_counter = 0;
    let mut machine_code;

    let time = time::Duration::from_millis(clock_speed as u64);

    println!("{}", intro_prompt(bits, number_gprs));

    loop {

        machine_code = machine_operations.memory.get(program_counter);
        machine_operations.memory.insert_binary(program_counter_address, binarystring::unsigned_int(program_counter+1, bits.3 as isize));

        let (opcode, source_operand, destination_operand) = handle_instruction(&machine_code, &machine_operations.memory, bits);

        sleep(time);

        machine_operations.execute(opcode, source_operand, destination_operand);

        program_counter = binarystring::read_unsigned_int(&machine_operations.memory.get(program_counter_address)).unwrap();
    }
}

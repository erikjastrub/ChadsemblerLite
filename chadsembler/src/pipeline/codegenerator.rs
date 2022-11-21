use std::collections::HashMap;
use crate::csm::structs::{Scope, Symbol, Operand, Instruction, Memory};
use crate::csm::defaults::{sysdefaults, SymbolTypes};
use crate::csm::tokens::{TokenTypes, TypedToken};
use crate::csm::binarystring;
use crate::csm::architecture::{instructions, addressingmodes, registers};

/// Update all global scope related symbols
fn update_global_symbols<'a>(global_scope: &mut Scope<'a>, procedure_scopes: &mut HashMap<&'a String, Scope>) {

    let mut offset = global_scope.num_instructions + global_scope.num_variables;

    for (identifier, scope) in procedure_scopes {

        let symbol = global_scope.symbol_table.get_mut(identifier).unwrap();
        symbol.symbol_value = offset as isize;
        offset += scope.num_instructions + scope.num_variables;
    }
}

/// Return the value an operand points to
fn resolve_operand(operand: &Operand, scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, number_gprs: usize) -> isize {

    match operand.operand_value.token_type {

        TokenTypes::Label => {

            if let Some(s) = scope_symbol_table.get(&operand.operand_value.token_value) { 
                
                s.symbol_value 
            
            } else { 
                
                // If the symbol isn't in the local scope then it is in the global scope
                global_symbol_table[&operand.operand_value.token_value].symbol_value
            }
        },
        
        TokenTypes::Value => {

            operand.operand_value.token_value.parse().unwrap()
        },

        TokenTypes::Register => {

            if let Some(spr) = registers::SP_REGISTERS.get(&operand.operand_value.token_value) {
                
                (number_gprs + spr.offset) as isize * -1
                
            } else {
                
                // GPR Zero cannot be accessible so the value must be wrapped between 1..n (inclusive)
                sysdefaults::wrap_bound(1, (number_gprs) as isize, 
                                     operand.operand_value.token_value.parse::<isize>().unwrap())  * -1 
            }
        },

        _ => unreachable!()
    }
}

/// Generate the machine code (bits) that would represent a low level CPU instruction
fn generate_machine_operation(instruction: &Instruction, source_operand: &Operand, destination_operand: &Operand,
                              scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, number_gprs: usize,
                              machine_operation_bits: usize, addressing_mode_bits: usize, operand_bits: usize) -> String {

    let instruction_binary = binarystring::unsigned_int(instruction.opcode as isize, machine_operation_bits as isize);

    let addressing_mode_binary = binarystring::unsigned_int(addressingmodes::ADDRESSING_MODES[&source_operand.addressing_mode.token_value].opcode as isize, addressing_mode_bits as isize);
                            
    let source_operand_binary = binarystring::signed_int(resolve_operand(source_operand, scope_symbol_table, global_symbol_table, number_gprs), operand_bits as isize);
                            
    let destination_operand_binary = binarystring::signed_int(resolve_operand(destination_operand, scope_symbol_table, global_symbol_table, number_gprs), operand_bits as isize);
                            
    [instruction_binary, addressing_mode_binary, source_operand_binary, destination_operand_binary].concat()
}

/// Update any local symbols and prematurely place any variables into the memory pool
fn update_local_symbols(index: &mut usize, offset: &mut usize, scope: &mut Scope, memory: &mut Memory, total_bits: usize) {

    // The offset is where the variables should be placed in memory
    *offset += scope.num_instructions as usize;

    // Update the local symbols
    for symbol in scope.symbol_table.values_mut() {

        if symbol.symbol_type == SymbolTypes::Branch {

            //  Update address to be relative to its position in memory instead of its position in the scope
            symbol.symbol_value += *index as isize
        
        } else if symbol.symbol_type == SymbolTypes::Variable {

            //  Place variables at the end of the instructions
            memory.insert_binary(*offset as isize, binarystring::signed_int(symbol.symbol_value, total_bits as isize));
            symbol.symbol_value = *offset as isize;
            *offset += 1;
        }
    }
}

/// Generate the code for a given scope
fn generate_code(index: &mut usize, offset: &mut usize, scope_tokens: &Vec<&TypedToken>, scope_symbol_table: &HashMap<&String, Symbol>, 
                 global_symbol_table: &HashMap<&String, Symbol>, memory: &mut Memory,
                 number_gprs: usize, machine_operation_bits: usize, addressing_mode_bits: usize, operand_bits: usize) {

    let (mut current_source, mut current_destination);
    let default_operand = Operand {

        addressing_mode: &TypedToken {
            token_type: TokenTypes::AddressingMode,
            token_value: addressingmodes::REGISTER.symbol.to_owned(),
            row: 0,
            column: 0
        },

        operand_value: &TypedToken {
            token_type: TokenTypes::Value,
            token_value: sysdefaults::OPERAND_VALUE.to_owned(),
            row: 0,
            column: 0
        },
    };

    // Generate the machine code for each instruction
    for (i, token) in scope_tokens.iter().enumerate() {

        if token.token_type == TokenTypes::Instruction {

            let instruction = instructions::INSTRUCTION_SET[&token.token_value];

            let source_operand = if instruction.operands > 0 {

                current_source = Operand{ addressing_mode: scope_tokens[i+1], operand_value: scope_tokens[i+2] };
                &current_source
            
            } else {

                &default_operand
            };

            let destination_operand = if instruction.operands > 1 {

                current_destination = Operand{ addressing_mode: scope_tokens[i+4], operand_value: scope_tokens[i+5] };
                &current_destination
            
            } else {

                &default_operand
            };

            memory.insert_binary(*index as isize, generate_machine_operation(&instruction, source_operand, destination_operand, scope_symbol_table, global_symbol_table, number_gprs, machine_operation_bits, addressing_mode_bits, operand_bits));
            *index += 1;
        }
    }

    *index = *offset;
}

/// Run the CodeGenerator
/// Will return the memory and the bits used by each part of the machine code
pub fn run<'a>(global_scope: &mut Scope<'a>, procedure_scopes: &mut HashMap<&'a String, Scope>, config_table: &HashMap<String, usize>) -> (Memory, usize, usize, usize) {

    let machine_operation_bits = binarystring::number_bits(instructions::NUMBER_INSTRUCTIONS - 1);
    let addressing_mode_bits = binarystring::number_bits(addressingmodes::NUMBER_MODES - 1);

    let number_gprs = config_table[sysdefaults::REGISTERS_CONFIG.0];
    let number_registers = number_gprs + registers::NUMBER_SP_REGISTERS;

    let number_memory_addresses = config_table[sysdefaults::MEMORY_CONFIG.0] as usize;

    let operand_bits = if number_registers > number_memory_addresses
                            { binarystring::number_bits(number_registers) }
                            else { binarystring::number_bits(number_memory_addresses) } + 1;

    let total_bits = machine_operation_bits + addressing_mode_bits + 2*operand_bits;

    let (mut index, mut offset) = (0, 0);

    let mut memory = Memory::new(number_registers, total_bits, operand_bits);

    update_global_symbols(global_scope, procedure_scopes);

    update_local_symbols(&mut index, &mut offset, global_scope, &mut memory, total_bits);
    generate_code(&mut index, &mut offset, &global_scope.tokens, &global_scope.symbol_table, &global_scope.symbol_table, &mut memory, number_gprs, machine_operation_bits, addressing_mode_bits, operand_bits);

    for scope in procedure_scopes.values_mut() {

        update_local_symbols(&mut index, &mut offset, scope, &mut memory, total_bits);
        generate_code(&mut index, &mut offset, &scope.tokens, &scope.symbol_table, &global_scope.symbol_table, &mut memory, number_gprs, machine_operation_bits, addressing_mode_bits, operand_bits)
    }

    (memory, machine_operation_bits, addressing_mode_bits, operand_bits)
}

use std::collections::HashMap;
use crate::csm::structs::{Scope, Symbol, Operand};
use crate::csm::tokens::{TypedToken, TokenTypes};
use crate::csm::errors::{Errors, errormessages};
use crate::csm::defaults::sysdefaults;
use crate::csm::architecture::{instructions, addressingmodes};

/// Return the number of operands found for an instruction in the token stream
fn count_operands(mut index: usize, tokens: &Vec<&TypedToken>) -> isize {

    let mut operands = 0;

    while tokens[index].token_type != TokenTypes::End {

        if matches!(tokens[index].token_type, TokenTypes::Value | TokenTypes::Label | TokenTypes::Register) {

            operands += 1;
        }

        index += 1;
    }

    operands
}

/// Verify the semantic validity of the addressing mode of an operand
fn analyse_addressing_mode(operand: &Operand, errors: &mut Errors) {

    if operand.addressing_mode.token_value == addressingmodes::REGISTER.symbol &&
       operand.operand_value.token_type != TokenTypes::Register {

        errors.record_error(operand.operand_value.row, operand.operand_value.column, errormessages::REGISTER_MODE_MISMATCH.error_type, errormessages::REGISTER_MODE_MISMATCH.error_message);
    
    } else if operand.addressing_mode.token_value != addressingmodes::REGISTER.symbol &&
              operand.operand_value.token_type == TokenTypes::Register {

        errors.record_error(operand.operand_value.row, operand.operand_value.column, errormessages::REGISTER_OPERAND_MISMATCH.error_type, errormessages::REGISTER_OPERAND_MISMATCH.error_message);
    }
}

/// Verify the semantic validity of the value of an operand
fn analyse_operand_value(operand: &Operand, scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, errors: &mut Errors) {


    if operand.operand_value.token_type == TokenTypes::Label &&
       !global_symbol_table.contains_key(&operand.operand_value.token_value) &&
       !scope_symbol_table.contains_key(&operand.operand_value.token_value) {

        errors.record_error(operand.operand_value.row, operand.operand_value.column, errormessages::UNDECLARED_LABEL.error_type, errormessages::UNDECLARED_LABEL.error_message);

    } else if operand.operand_value.token_type == TokenTypes::Register &&
              operand.operand_value.token_value == "0" {

        errors.record_error(operand.operand_value.row, operand.operand_value.column, errormessages::GPR_ZERO.error_type, errormessages::GPR_ZERO.error_message);
    }              
}

/// Verify the semantic validity of an operand as a whole
#[inline]
fn analyse_operand(operand: &Operand, scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, errors: &mut Errors) {

    analyse_addressing_mode(operand, errors);

    analyse_operand_value(operand, scope_symbol_table, global_symbol_table, errors);
}

/// Get the operand of an instruction
// Will insert a default operand into the token stream if not present
// index: int -> the beginning index of the operand (NOT the beginning index of the instruction)
fn get_operand<'a>(mut index: usize, tokens: &mut Vec<&'a TypedToken>, 
                   default_operands: &(&'a TypedToken, &'a TypedToken, &'a TypedToken, &'a TypedToken)) -> Operand<'a> {

    let (default_acc, default_register, default_direct, default_separator) = *default_operands;

    let token = tokens[index];

    if token.token_type == TokenTypes::Separator {

        return get_operand(index+1, tokens, default_operands);

    } else if token.token_type == TokenTypes::End {

        tokens.insert(index, default_acc);

        tokens.insert(index, default_register);

        if matches!(tokens[index-1].token_type, TokenTypes::Register | TokenTypes::Label | TokenTypes::Value) {

            tokens.insert(index, default_separator);

            index += 1;
        }
    
    } else if token.token_type == TokenTypes::Register {

        tokens.insert(index, default_register);
    
    } else if matches!(token.token_type, TokenTypes::Label | TokenTypes::Value) {

        tokens.insert(index, default_direct);
    }

    Operand {
        addressing_mode: tokens[index],
        operand_value: tokens[index+1]
    }
}

/// Verify the semantic validity of an instruction
fn analyse_instruction<'a>(index: usize, tokens: &mut Vec<&'a TypedToken>, scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, 
                           default_operands: &(&'a TypedToken, &'a TypedToken, &'a TypedToken, &'a TypedToken), errors: &mut Errors) {

    let token = tokens[index];
    let instruction = instructions::INSTRUCTION_SET[&token.token_value];
    let number_operands = count_operands(index, tokens);

    if number_operands > instruction.operands {

        errors.record_error(token.row, token.column, errormessages::EXCESS_OPERANDS.error_type, errormessages::EXCESS_OPERANDS.error_message);

    } else if instruction.operands > 1 &&
              tokens[index+1].token_type == TokenTypes::End {

        errors.record_error(token.row, token.column, errormessages::NO_SOURCE_OPERAND.error_type, errormessages::NO_SOURCE_OPERAND.error_message);

    } else {

        if instruction.operands > 0 {

            let source_operand = get_operand(index+1, tokens, default_operands);
            analyse_operand(&source_operand, scope_symbol_table, global_symbol_table, errors);

            // Various Semantic Checks
            if instruction == &instructions::INP &&
               source_operand.addressing_mode.token_value != addressingmodes::REGISTER.symbol {

                errors.record_error(token.row, token.column, errormessages::NON_REGISTER_INP_OPERAND.error_type, errormessages::NON_REGISTER_INP_OPERAND.error_message);
            }

            if instructions::NON_IMMEDIATE_MODE_INSTRUCTIONS.contains(instruction.mnemonic) &&
               source_operand.addressing_mode.token_value == addressingmodes::IMMEDIATE.symbol {

                errors.record_error(token.row, token.column, errormessages::IMMEDIATE_MODE.error_type, errormessages::IMMEDIATE_MODE.error_message);
            }
            //

            if instruction.operands > 1 {

                let destination_operand = get_operand(index+3, tokens, default_operands);
                analyse_operand(&destination_operand, scope_symbol_table, global_symbol_table, errors);

                // Various Semantic Checks
                if destination_operand.addressing_mode.token_value != addressingmodes::REGISTER.symbol {

                    errors.record_error(token.row, token.column, errormessages::NON_REGISTER_DESTINATION_OPERAND.error_type, errormessages::NON_REGISTER_DESTINATION_OPERAND.error_message);
                }
                //
            }
        }
    }
}

/// Semantically analyse a scope
#[inline]
fn semantic_analyse<'a>(tokens: &mut Vec<&'a TypedToken>, scope_symbol_table: &HashMap<&String, Symbol>, global_symbol_table: &HashMap<&String, Symbol>, 
                        default_operands: &(&'a TypedToken, &'a TypedToken, &'a TypedToken, &'a TypedToken), errors: &mut Errors) {

    let mut index = 0;

    while index < tokens.len() {

        if tokens[index].token_type == TokenTypes::Instruction {

            analyse_instruction(index, tokens, scope_symbol_table, global_symbol_table, default_operands, errors);
        }

        index += 1;
    }
}

/// Run the SemanticAnalyser
pub fn run<'a>(global_scope: &mut Scope<'a>, procedure_scopes: &mut HashMap<&String, Scope<'a>>,
               default_operands: &(&'a TypedToken, &'a TypedToken, &'a TypedToken, &'a TypedToken)) {

    let mut errors = Errors::new();

    semantic_analyse(&mut global_scope.tokens, &global_scope.symbol_table, &global_scope.symbol_table, default_operands, &mut errors);

    for scope in procedure_scopes.values_mut() {

        semantic_analyse(&mut scope.tokens, &scope.symbol_table, &global_scope.symbol_table, default_operands, &mut errors)
    }

    errors.get_errors(sysdefaults::SEMANTIC_ANALYSER_ERRORS_HEADER);
}

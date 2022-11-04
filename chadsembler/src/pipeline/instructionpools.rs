use std::collections::HashMap;

use crate::csm::structs::{Scope, Symbol};
use crate::csm::tokens::{TypedToken, TokenTypes};
use crate::csm::errors::{Errors, errormessages};
use crate::csm::defaults::{sysdefaults, SymbolTypes};

/// Accumulate all tokens encountered in the scope
fn get_scope<'a>(tokens: &'a Vec<TypedToken>, index: &mut usize) -> Vec<&'a TypedToken> {

    let (mut token, mut scope_tokens) = (&tokens[*index], Vec::new());

    while token.token_type != TokenTypes::RightBrace {

        scope_tokens.push(token);
        *index += 1;
        token = &tokens[*index];
    }

    *index += 1;
    scope_tokens
}

/// Find and accumulate all scopes found within the token stream
fn get_scopes<'a>(tokens: &'a Vec<TypedToken>, index: &mut usize, global_scope: &mut Scope<'a>, procedure_scopes: &mut HashMap<&'a String, Scope<'a>>) {

    let length = tokens.len();
    let mut token;

    while *index < length {

        token = &tokens[*index];

        if token.token_type == TokenTypes::LeftBrace {

            // Pop garbage tokens out of the global scope
            let mut procedure_token = global_scope.tokens.pop().unwrap();

            if procedure_token.token_type == TokenTypes::End {

                procedure_token = global_scope.tokens.pop().unwrap();
            }

            *index += 2;

            procedure_scopes.insert(&procedure_token.token_value, Scope {
                tokens: get_scope(tokens, index),
                symbol_table: HashMap::new(),
                num_instructions: 0,
                num_variables: 0
            });
        
        } else {

            global_scope.tokens.push(token);
        }

        *index += 1;
    }
}

/// Append all procedure identifiers to the global scope
/// This allows them to be called from the global scope
fn update_global_scope<'a>(global_scope: &mut Scope<'a>, procedure_scopes: &mut HashMap<&'a String, Scope<'a>>) {

    for identifier in procedure_scopes.keys() {

        global_scope.symbol_table.insert(identifier, Symbol {
            symbol_value: 0,
            symbol_type: SymbolTypes::Procedure
        });
    }
}

/// Verify the validity of a symbol
fn handle_symbol(symbol: &Symbol, current_token: &TypedToken, next_token: &TypedToken, errors: &mut Errors) {

    // Branch Label
    if next_token.token_type == TokenTypes::Instruction {

        match symbol.symbol_type {

            SymbolTypes::Procedure => {

                errors.record_error(current_token.row, current_token.column, errormessages::PROC_TO_BRANCH_REDECL.error_type, errormessages::PROC_TO_BRANCH_REDECL.error_message);
            },

            SymbolTypes::Branch => {

                errors.record_error(current_token.row, current_token.column, errormessages::DUPLICATE_BRANCH.error_type, errormessages::DUPLICATE_BRANCH.error_message);
            },
            
            SymbolTypes::Variable => {

                errors.record_error(current_token.row, current_token.column, errormessages::VAR_TO_BRANCH_REDECL.error_type, errormessages::VAR_TO_BRANCH_REDECL.error_message);
            }
        }

    // Variable Label
    } else if next_token.token_type == TokenTypes::AssemblyDirective {

        match symbol.symbol_type {

            SymbolTypes::Procedure => {

                errors.record_error(current_token.row, current_token.column, errormessages::PROC_TO_VAR_REDECL.error_type, errormessages::PROC_TO_VAR_REDECL.error_message);
            },

            SymbolTypes::Branch => {

                errors.record_error(current_token.row, current_token.column, errormessages::BRACH_TO_VAR_REDECL.error_type, errormessages::PROC_TO_BRANCH_REDECL.error_message);
            },
            
            SymbolTypes::Variable => {

                errors.record_error(current_token.row, current_token.column, errormessages::DUPLICATE_VAR.error_type, errormessages::DUPLICATE_VAR.error_message);
            }
        }
    }
}

/// Remove the tokens representing a variable from the token stream
#[inline]
fn remove_variable(scope: &mut Scope, index: usize) {

    while !scope.tokens.is_empty() &&
          scope.tokens[index].token_type != TokenTypes::End {

        scope.tokens.remove(index);
    }
}

/// Verify and update the symbol table accordingly for a given label
fn handle_label(scope: &mut Scope, index: usize, statements: usize, errors: &mut Errors) {

    let first_token = scope.tokens[index]; // The label token
    let second_token = scope.tokens[index+1]; // Either a directive, instruction or end token
    let third_token = scope.tokens[index+2]; // Either an END or VALUE token

    if scope.symbol_table.contains_key(&first_token.token_value) {

        let symbol = &scope.symbol_table[&first_token.token_value];

        handle_symbol(symbol, first_token, second_token, errors);
    
    } else {

        let mut symbol = Symbol { 
            symbol_value: 0, 
            symbol_type: SymbolTypes::Variable 
        };

        if second_token.token_type == TokenTypes::AssemblyDirective {

            // Label inferred to be a variable declaration
            symbol.symbol_value = if third_token.token_type == TokenTypes::Value
                                  { third_token.token_value.parse().unwrap() }
                                  else { sysdefaults::VARIABLE_VALUE };

            remove_variable(scope, index);
            scope.num_variables += 1;

        } else if second_token.token_type == TokenTypes::Instruction {

            // Label inferred to be a branch declaration
            symbol.symbol_type  = SymbolTypes::Branch;
            symbol.symbol_value = statements as isize;
        }

        scope.symbol_table.insert(&first_token.token_value, symbol);
    }
}

/// Update the symbol table with its labels for a given scope
fn update_symbol_table(scope: &mut Scope, errors: &mut Errors) {

    let (mut index, mut statements) = (0, 0);

    // The length of the tokens can change so its length must be recalculated on each iteration
    while index < scope.tokens.len() {

        if scope.tokens[index].token_type == TokenTypes::Label &&
           matches!(scope.tokens[index+1].token_type, TokenTypes::Instruction | TokenTypes::AssemblyDirective) {

            handle_label(scope, index, statements, errors)
        
        } else if scope.tokens[index].token_type == TokenTypes::Instruction {

            statements += 1;
        }

        index += 1;
    }

    scope.num_instructions = statements;
}

/// Run the InstructionPools class
/// Will return the global and procedure scopes
pub fn run(tokens: &Vec<TypedToken>) -> (Scope, HashMap<&String, Scope>) {

    let (mut index, mut errors) = (0, Errors::new());

    let mut global_scope = Scope {
        tokens: Vec::new(),
        symbol_table: HashMap::new(),
        num_instructions: 0,
        num_variables: 0
    };

    let mut procedure_scopes = HashMap::new();

    get_scopes(tokens, &mut index, &mut global_scope, &mut procedure_scopes);

    update_global_scope(&mut global_scope, &mut procedure_scopes);

    update_symbol_table(&mut global_scope, &mut errors);

    for scope in procedure_scopes.values_mut() {

        update_symbol_table(scope, &mut errors);
    }

    errors.get_errors(sysdefaults::INSTRUCTION_POOL_ERRORS_HEADER);
    
    (global_scope, procedure_scopes)
}

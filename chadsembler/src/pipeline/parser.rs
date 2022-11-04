use std::process;
use crate::csm::tokens::{TypedToken, TokenTypes};
use crate::csm::defaults::sysdefaults;

// Specify what Tokens can be found after certain Token Types
const END: [TokenTypes; 5] = [TokenTypes::End, TokenTypes::Instruction, TokenTypes::Label, TokenTypes::RightBrace, TokenTypes::LeftBrace];
const INSTRUCTION: [TokenTypes; 6] = [TokenTypes::End, TokenTypes::AddressingMode, TokenTypes::Value, TokenTypes::Register, TokenTypes::Label, TokenTypes::RightBrace];
const ADDRESSING_MODE: [TokenTypes; 3] = [TokenTypes::Value, TokenTypes::Register, TokenTypes::Label];
const OPERAND: [TokenTypes; 4] = [TokenTypes::End, TokenTypes::Separator, TokenTypes::RightBrace, TokenTypes::LeftBrace];
const LABEL: [TokenTypes; 6] = [TokenTypes::End, TokenTypes::Separator, TokenTypes::Instruction, TokenTypes::RightBrace, TokenTypes::LeftBrace, TokenTypes::AssemblyDirective];
const SEPARATOR: [TokenTypes; 4] = [TokenTypes::AddressingMode, TokenTypes::Value, TokenTypes::Register, TokenTypes::Label];
const SCOPE: [TokenTypes; 1] = [TokenTypes::End];
const ASSEMBLY_DIRECTIVE: [TokenTypes; 2] = [TokenTypes::End, TokenTypes::Value];

/// Append a tuple containing the syntactically invalid tokens
fn record_error<'a>(first_token: &'a TypedToken, second_token: &'a TypedToken, errors: &mut Vec<(&'a TypedToken, &'a TypedToken)>) {

    errors.push( (first_token, second_token) );
}

/// If there are errors, will output all errors and exit the program
fn get_errors(errors: &Vec<(&TypedToken, &TypedToken)>) {

    if !errors.is_empty() {

        eprintln!("{}", sysdefaults::PARSER_ERRORS_HEADER);

        for (first, second) in errors {

            match (&first.token_type, &second.token_type) {

                (TokenTypes::LeftBrace, TokenTypes::LeftBrace) => {

                    eprintln!("Invalid Syntax Error {}:{} -> Block scope was opened but never closed", first.row, first.column);
                },

                (TokenTypes::RightBrace, TokenTypes::RightBrace) => {

                    eprintln!("Invalid Syntax Error {}:{} -> Block scope was opened but never closed", first.row, first.column);
                },

                (TokenTypes::End, _) => {

                    eprintln!("Invalid Syntax Error {}:{} -> Statement cannot begin with a {}", second.row, second.column, TokenTypes::type_to_str(&second.token_type));
                },

                (_, TokenTypes::End) => {

                    eprintln!("Invalid Syntax Error {}:{} -> Statement cannot end with a {}", first.row, first.column, TokenTypes::type_to_str(&first.token_type));
                },

                _ => {

                    eprintln!("Invalid Syntax Error {}:{} -> {} was found after {}", second.row, second.column, TokenTypes::type_to_str(&second.token_type), TokenTypes::type_to_str(&first.token_type));
                }
            }
        }

        process::exit(sysdefaults::EXIT_CODE);
    }
}

/// Return the expected tokens that should come after a given token
fn possible_tokens(token: &TypedToken) -> &[TokenTypes] {

    match token.token_type {

        TokenTypes::End => &END[..],
        TokenTypes::Instruction => &INSTRUCTION[..],
        TokenTypes::AddressingMode => &ADDRESSING_MODE[..],
        TokenTypes::Value | TokenTypes::Register => &OPERAND[..],
        TokenTypes::Label => &LABEL[..],
        TokenTypes::Separator => &SEPARATOR[..],
        TokenTypes::RightBrace | TokenTypes::LeftBrace => &SCOPE[..],
        TokenTypes::AssemblyDirective => &ASSEMBLY_DIRECTIVE[..]
    }  
}

/// Verify a block scope is valid
fn validate_scope<'a>(token: &'a TypedToken, previous_scope: &mut Option<&'a TypedToken>, errors: &mut Vec<(&'a TypedToken, &'a TypedToken)>) {

    if token.token_type == TokenTypes::LeftBrace {

        if previous_scope.is_none() {

            *previous_scope = Some(token);
        
        } else {

            record_error(token, token, errors);
        }

    } else {

        if previous_scope.is_none() {

            record_error(token, token, errors);
        
        } else {

            *previous_scope = None;
        }
    }
}

/// Verify the tokens match the syntax of the language
fn parse<'a>(tokens: &'a Vec<TypedToken>, previous_scope: &mut Option<&'a TypedToken>, errors: &mut Vec<(&'a TypedToken, &'a TypedToken)>) {

    // Last token is always an END Token
    // Initialise with END token to open the start of a new statement
    let mut previous = tokens.last().unwrap();

    for token in tokens {

        if token.token_type == TokenTypes::LeftBrace ||
           token.token_type == TokenTypes::RightBrace {

            validate_scope(token, previous_scope, errors)
        }

        if !possible_tokens(previous).contains(&token.token_type) {

            record_error(previous, token, errors);
        }

        previous = token;
    }

    // Ensure there is no unclosed block scope
    if let Some(left_brace) = previous_scope {

        record_error(left_brace, left_brace, errors);
    }
}

/// Run the Parser
pub fn run(tokens: &Vec<TypedToken>) {

    let (mut previous_scope, mut errors) = (None, Vec::new());

    parse(tokens, &mut previous_scope, &mut errors);
    get_errors(&errors);
}
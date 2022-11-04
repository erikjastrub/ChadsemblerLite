use crate::csm::tokens::{PositionToken, TypedToken, TokenTypes};
use crate::csm::errors::{Errors, errormessages};
use crate::csm::defaults::{sysdefaults, lexerdefaults};
use crate::csm::architecture::{instructions, addressingmodes, registers};

/// Tokenise the source code, ignoring any comments and directives
fn skip_line(source_code: &str, index: &mut usize) {

    let length = source_code.len();

    // Only iterate while the next character is not a line-breaking character
    // Check the next index is indexable to ensure no over-increment occurs
    while *index+1 < length &&
            !lexerdefaults::LINE_BREAK_CHARS.contains(source_code.as_bytes()[*index] as char) {

        *index += 1;
    }
}

/// Read the current token at the current index held
fn get_token(source_code: &str, index: &mut usize, directive_prefix: char, comment_prefix: char) -> String {

    let (lower, length) = (*index, source_code.len());

    // Iterate until the beginning of another possible token
    while *index < length &&
            source_code.as_bytes()[*index] as char != comment_prefix &&
            source_code.as_bytes()[*index] as char != directive_prefix &&
            source_code.as_bytes()[*index] as char != lexerdefaults::SEPARATOR &&
            !lexerdefaults::WHITESPACE_CHARS.contains(source_code.as_bytes()[*index] as char) &&
            !lexerdefaults::LINE_BREAK_CHARS.contains(source_code.as_bytes()[*index] as char) &&
            !lexerdefaults::SCOPE_CHARS.contains(source_code.as_bytes()[*index] as char) &&
            !addressingmodes::ADDRESSING_MODES.contains_key(&source_code[*index..*index+1]) {

        *index += 1;
    }

    // Default-casing to standardise how tokens are processed
    sysdefaults::default_casing(&source_code[lower..*index])
}

/// Check if a token is a General Purpose Register - GPR
/// If the token isn't a GPR then None is returned
/// If it is then a string containing the GPR number is returned
fn is_gpr(token: &str) -> Option<String> {

    // The syntax for a GPR can look like: "REG5"
    // To extract the digits at the end, a pointer to the end of the token is initialised
    // and then decremented until the beginning of the digits is found
    // The digits can then be extracted as a substring

    let mut lower = token.len();

    while (token.as_bytes()[lower-1] as char).is_numeric() {

        lower -= 1;
    }

    let (register, digits) = (&token[..lower], &token[lower..]);

    if registers::GPR_VARIANTS.contains(&register) {

        Some(digits.to_owned())

    }  else {

        None
    }
}

// Will determine and return the token type of a given token
fn get_type(token: &str) -> TokenTypes {

    if instructions::INSTRUCTION_SET.contains_key(token) {

        TokenTypes::Instruction

    } else if registers::SP_REGISTERS.contains_key(token) {

        TokenTypes::Register

    } else if addressingmodes::ADDRESSING_MODES.contains_key(token) {

        TokenTypes::AddressingMode

    } else if token == instructions::DAT {

        TokenTypes::AssemblyDirective

    } else {

        // A label token can be inferred if no special-cases are matched
        TokenTypes::Label
    }
}

/// Will verify the validity of a value token, recording errors if invalid
fn handle_value(mut token: &str, position: &mut PositionToken, errors: &mut Errors) {

    if lexerdefaults::VALUE_SIGNS.contains(token.as_bytes()[0] as char) {

        token = &token[1..];
    }

    if token.chars().any(|c| !lexerdefaults::VALUE_CHARS.contains(c)) {

        errors.record_error(
            position.row, 
            position.column, 
            errormessages::INVALID_VALUE.error_type, 
            errormessages::INVALID_VALUE.error_message
        );
    }
}

/// Will verify the validity of a label token, recording errors if invalid
fn handle_label(token: &str, position: &mut PositionToken, errors: &mut Errors) {

    if token.chars().any(|c| !lexerdefaults::LABEL_CHARS.contains(c)) {

        errors.record_error(
            position.row, 
            position.column, 
            errormessages::INVALID_LABEL.error_type, 
            errormessages::INVALID_LABEL.error_message
        );
    }
}

/// Will determine the token type and call the appropriate methods to verify the validity of the token
fn handle_token(source_code: &str, index: &mut usize, directive_prefix: char, comment_prefix: char, 
                position: &mut PositionToken, errors: &mut Errors) -> TypedToken {

    let mut token_value = get_token(source_code, index, directive_prefix, comment_prefix);

    if lexerdefaults::VALUE_BEGIN_CHARS.contains(token_value.as_bytes()[0] as char) {

        handle_value(&token_value, position, errors);
        return TypedToken {

            token_type: TokenTypes::Value,
            token_value,
            row: position.row,
            column: position.column
        };
    }

    if let Some(digits) = is_gpr(&token_value) {

        return TypedToken {

            token_type: TokenTypes::Register,
            token_value: digits,
            row: position.row,
            column: position.column
        };
    }

    let token_type = get_type(&token_value);

    if token_type == TokenTypes::AddressingMode {

        token_value = addressingmodes::ADDRESSING_MODES[&token_value].symbol.to_owned();
    
    } else if token_type == TokenTypes::Label {

        handle_label(&token_value, position, errors);
    }

    TypedToken { 
        
        token_type, 
        token_value, 
        row: position.row, 
        column: position.column 
    }
}

/// Will iterate over and split the source code into its lexemes
/// Comments and directives are ignored
fn tokenise(source_code: &str, index: &mut usize, directive_prefix: char, comment_prefix: char, 
            position: &mut PositionToken, errors: &mut Errors) -> Vec<TypedToken> {

    let  (mut tokens, length) = (Vec::new(), source_code.len());
    let mut current_char;

    while *index < length {

        current_char = source_code.as_bytes()[*index] as char;

        if current_char == directive_prefix ||
            current_char == comment_prefix {

            skip_line(source_code, index);
            tokens.push(TypedToken {
                token_type: TokenTypes::End,
                token_value: lexerdefaults::LINE_BREAK_CHARS.to_owned(),
                row: position.row,
                column: position.column
            });

        } else if lexerdefaults::LINE_BREAK_CHARS.contains(current_char) &&
                    !tokens.is_empty() &&  // Avoid appending unnecessary duplicate END tokens
                    tokens[tokens.len()-1].token_type != TokenTypes::End {

            tokens.push(TypedToken {
                token_type: TokenTypes::End,
                token_value: lexerdefaults::LINE_BREAK_CHARS.to_owned(),
                row: position.row,
                column: position.column
            });
        
        } else if lexerdefaults::LEFT_SCOPE.contains(current_char) {

            tokens.push(TypedToken {
                token_type: TokenTypes::LeftBrace,
                token_value: lexerdefaults::LEFT_SCOPE.to_owned(),
                row: position.row,
                column: position.column
            });

        } else if lexerdefaults::RIGHT_SCOPE.contains(current_char) {

            tokens.push(TypedToken {
                token_type: TokenTypes::RightBrace,
                token_value: lexerdefaults::RIGHT_SCOPE.to_owned(),
                row: position.row,
                column: position.column
            });

        } else if current_char == lexerdefaults::SEPARATOR {

            tokens.push(TypedToken {
                token_type: TokenTypes::Separator,
                token_value: lexerdefaults::SEPARATOR.to_string(),
                row: position.row,
                column: position.column
            });

        } else if addressingmodes::ADDRESSING_MODES.contains_key(unsafe{std::str::from_utf8_unchecked(&[current_char as u8])}) {

            tokens.push(TypedToken {
                token_type: TokenTypes::AddressingMode,
                token_value: current_char.to_string(),
                row: position.row,
                column: position.column
            });
        
        } else if !lexerdefaults::WHITESPACE_CHARS.contains(current_char) {

            let token = handle_token(source_code, index, directive_prefix, comment_prefix, position, errors);

            // Compensate for over-increment
            *index -= 1;
            position.column += token.token_value.len() - 1;

            tokens.push(token);
        }

        position.advance_position(source_code.as_bytes()[*index] as char, 1);
        *index += 1;
    }   
    
    tokens.push(TypedToken {
        token_type: TokenTypes::End,
        token_value: lexerdefaults::LINE_BREAK_CHARS.to_owned(),
        row: position.row,
        column: position.column
    });
    
    tokens
}

// Run the Lexer
// Will return the generated tokens from the source code
pub fn run(source_code: &str, directive_prefix: char, comment_prefix: char) -> Vec<TypedToken> {

    let mut index = 0;
    let mut position = PositionToken { row: 1, column: 1 };
    let mut errors = Errors::new();

    let tokens = tokenise(source_code, &mut index, directive_prefix, comment_prefix, &mut position, &mut errors);

    errors.get_errors(sysdefaults::LEXER_ERRORS_HEADER);

    tokens
}

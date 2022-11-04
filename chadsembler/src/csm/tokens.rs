use std::collections::HashMap;
use crate::csm::defaults::{sysdefaults, lexerdefaults};
use crate::csm::errors::{Errors, errormessages};

/// Stores the positional related data for a given item
/// Can be thought of as a 2d coordinate
pub struct PositionToken {

    pub row: usize,
    pub column: usize
}

impl PositionToken {

    /// Given the current_char, will update the row and column attributes accordingly
    /// Will reset the column attribute to the reset_value if a line break char is encountered
    pub fn advance_position(&mut self, current_char: char, reset_value: usize) {

        if lexerdefaults::LINE_BREAK_CHARS.contains(current_char) {

            self.row += 1;
            self.column = reset_value;

        }

        else {

            self.column += 1;
        }
    }
}

/// Stores both positional related data and a token_value for a given item
pub struct UntypedToken {

    pub token_value: String,
    pub row: usize,
    pub column: usize
}


/// Stores the positional related data, token_value and token_type for a given item
pub struct TypedToken {

    pub token_type: TokenTypes,
    pub token_value: String,
    pub row: usize,
    pub column: usize
}

/// Namespace for all token types that can be used in conjunction with the TypedToken class
#[derive(PartialEq)]
pub enum TokenTypes {
    End,
    Instruction,
    AddressingMode,
    Value,
    Register,
    Label,
    Separator,
    LeftBrace,
    RightBrace,
    AssemblyDirective,
}

impl TokenTypes {

    /// Returns the stringified token
    pub fn type_to_str(token_type: &TokenTypes) -> &str {

        match token_type {

            Self::End => "End Of Statement",
            Self::Instruction => "Instruction",
            Self::AddressingMode => "Addressing Mode",
            Self::Value => "Value",
            Self::Register => "Register",
            Self::Label => "Label",
            Self::Separator => "Operand Separator",
            Self::LeftBrace => "Left Curly Brace",
            Self::RightBrace => "Right Curly Brace",
            Self::AssemblyDirective => "Assembly Directive"
        }
    }
}

/// namespace for all token parsing functionality
pub mod tokenutils {

    use super::*;

    /// tokenise a string into its individual components, separating on the delimiter and ignoring the prefix
    pub fn tokenise(text: &str, prefix: char, delimiter: char, position: &mut PositionToken) -> Vec<UntypedToken> {

        let mut tokens = Vec::new();
        let length: usize = text.len();
        let mut current_index: usize = 0;
        let mut lower_index: usize;

        if length > 0 && text.starts_with(prefix) {

            current_index += 1;
            position.column += 1;
        }

        while current_index < length {

            if !lexerdefaults::WHITESPACE_CHARS.contains(text.as_bytes()[current_index] as char) &&
               text.as_bytes()[current_index] as char != delimiter {

                lower_index = current_index;

                while current_index < length &&
                      !lexerdefaults::WHITESPACE_CHARS.contains(text.as_bytes()[current_index] as char) &&
                      text.as_bytes()[current_index] as char != delimiter {

                        current_index += 1;
                        position.column += 1;
                }

                tokens.push(UntypedToken {
                    token_value: sysdefaults::default_casing(&text[lower_index..current_index]),
                    row: position.row,
                    // Subtract the length of the token from the current position to get the starting position of the token
                    column: position.column - (current_index - lower_index)
                })
               
            } else {

                current_index += 1;
                position.column += 1
            }
        }

    position.column -= 1;

    tokens
    }

    /// Verify the amount of tokens generated
    pub fn valid_number_tokens(tokens: &Vec<UntypedToken>, errors: &mut Errors) -> bool {

        if tokens.len() == 2 {

            return true;

        } else if !tokens.is_empty() {

            errors.record_error(tokens[0].row, tokens[0].column, errormessages::SINGLE_KEY_VALUE_PAIR.error_type, errormessages::SINGLE_KEY_VALUE_PAIR.error_message);
        }

        false
    }

    /// Verify the validity of the config option
    pub fn valid_config_option(option: &UntypedToken, config_table: &HashMap<String, usize>, errors: &mut Errors) -> bool {

        if config_table.contains_key(&option.token_value) {

            true

        } else {

            errors.record_error(option.row, option.column, errormessages::UNKNOWN_CONFIG_OPTION.error_type, errormessages::UNKNOWN_CONFIG_OPTION.error_message);
            false
        }
    }

    /// Verify the config value has no sign (+ or -)
    pub fn contains_no_sign(value: &UntypedToken, errors: &mut Errors) -> bool {

        if lexerdefaults::VALUE_SIGNS.contains(value.token_value.as_bytes()[0] as char) {

            errors.record_error(value.row, value.column, errormessages::SIGN_SPECIFIED.error_type, errormessages::SIGN_SPECIFIED.error_message);
            false            
        
        } else {

            true
        }
    }

    /// Verify the validity of the config value
    pub fn valid_config_value(value: &UntypedToken, errors: &mut Errors) -> bool {

        for c in value.token_value.chars() {

            if !c.is_digit(10) {

                errors.record_error(value.row, value.column, errormessages::INVALID_CONFIG_VALUE.error_type, errormessages::INVALID_CONFIG_VALUE.error_message);
                return false;
            }
        }

        true
    }

    /// Update the config table if the option and value are valid
    pub fn update_config_table(option: &UntypedToken, value: &UntypedToken, config_table: &mut HashMap<String, usize>, errors: &mut Errors) -> bool {

        // Previous checks will ensure this can always be converted to an int
        let value_int = value.token_value.parse::<usize>().unwrap();
        let mut minimum = 0;
        
        // Previous checks will ensure this will always correspond to a valid option
        for (key, default) in [sysdefaults::CLOCK_CONFIG, sysdefaults::REGISTERS_CONFIG, sysdefaults::MEMORY_CONFIG] {

            if key == option.token_value {

                minimum = default
            }
        }

        if value_int < minimum {

            errors.record_error(value.row, value.column, errormessages::MINIMUM_VALUE.error_type, errormessages::MINIMUM_VALUE.error_message);
            false

        } else {

            config_table.insert(option.token_value.to_owned(), value_int);
            true
        }
    }

    /// Convenience method, wrapping all other methods together
    #[allow(unused_must_use)]
    pub fn parse(tokens: &Vec<UntypedToken>, config_table: &mut HashMap<String, usize>, errors: &mut Errors) {

        valid_number_tokens(tokens, errors) &&
        valid_config_option(&tokens[0], config_table, errors) &&
        contains_no_sign(&tokens[1], errors) &&
        valid_config_value(&tokens[1], errors) &&
        update_config_table(&tokens[0], &tokens[1], config_table, errors);
    }
}

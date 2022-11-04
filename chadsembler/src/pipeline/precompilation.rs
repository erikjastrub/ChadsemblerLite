use std::collections::HashMap;
use crate::csm::tokens::{PositionToken, tokenutils};
use crate::csm::errors::Errors;
use crate::csm::defaults::{sysdefaults, lexerdefaults};

/// Tokenise, parse and validate the command line arguments passed into the program
pub mod argumentprocessor {

    use super::*;

    /// Run the ArgumentProcessor
    pub fn run(arguments: &[String], directive_prefix: char, delimiter: char, config_table: &mut HashMap<String, usize>) {

        let mut position = PositionToken { row: 1, column: 1 };
        let mut errors = Errors::new();

        for arg in arguments {

            let tokens = tokenutils::tokenise(arg, directive_prefix, delimiter, &mut position);

            tokenutils::parse(&tokens, config_table, &mut errors);

            position.row += 1;
            position.column = 1;
        }

        errors.get_errors(sysdefaults::ARGUMENT_PROCESSOR_ERRORS_HEADER)
    }
}

/// Tokenise, parse and validate all directives in a source code file without modifying the source code
pub mod preprocessor {

    use super::*;

    /// Iterate over and ignore a Chadsembly comment in a source code file
    fn skip_comment(source_code: &str, index: &mut usize) {

        let length = source_code.len();

        while *index+1 < length &&
              !lexerdefaults::LINE_BREAK_CHARS.contains( source_code.as_bytes()[*index] as char )  {

            *index += 1;
        }
    }

    /// Get the directive from the source code without removing it
    fn get_directive<'a>(source_code: &'a str, index: &mut usize, directive_prefix: char, comment_prefix: char) -> &'a str {

        let (lower, length) = (*index, source_code.len());
        *index += 1;

        while *index < length &&
              !lexerdefaults::WHITESPACE_CHARS.contains( source_code.as_bytes()[*index] as char ) &&
              source_code.as_bytes()[*index] as char != directive_prefix &&
              source_code.as_bytes()[*index] as char != comment_prefix {

            *index += 1;
        }

        let directive = &source_code[lower..*index];
        *index -= 1;
        
        directive
    }

    /// Apply all validation checks over tokens generated from a directive
    #[inline(always)]
    fn handle_directive(source_code: &str, index: &mut usize, directive_prefix: char, comment_prefix: char, delimiter: char, 
                        config_table: &mut HashMap<String, usize>, position: &mut PositionToken, errors: &mut Errors) {

        let directive = get_directive(source_code, index, directive_prefix, comment_prefix);
        let tokens = tokenutils::tokenise(directive, directive_prefix, delimiter, position);

        tokenutils::parse(&tokens, config_table, errors);
    }

    /// Run the Preprocessor
    pub fn run(source_code: &str, directive_prefix: char, comment_prefix: char, delimiter: char, config_table: &mut HashMap<String, usize>) {

        let (mut index, length) = (0, source_code.len());
        let mut position = PositionToken { row: 1, column: 1 };
        let mut errors = Errors::new();

        while index < length {

            let c = source_code.as_bytes()[index] as char;

            // dbg!(c);
            
            if c == comment_prefix {

                skip_comment(source_code, &mut index);
            
            } else if c == directive_prefix {

                handle_directive(source_code, &mut index, directive_prefix, comment_prefix, delimiter, config_table, &mut position, &mut errors);
            }

            if lexerdefaults::LINE_BREAK_CHARS.contains(source_code.as_bytes()[index] as char) {

                position.row += 1;
                position.column = 0;
            }
            
            index += 1;
            position.column += 1;
        }

        errors.get_errors(sysdefaults::PREPROCESSOR_ERRORS_HEADER);
    }
}

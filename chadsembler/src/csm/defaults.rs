pub mod sysdefaults {

    /// Ensure a value falls between the specified lower and upper limits (inclusive)
    /// Follows 2s complement bounds wrapping rules
    pub fn wrap_bound(lower: isize, upper: isize, value: isize) -> isize {

        lower + (value - lower) % (upper + 1 - lower)
    }

    /// Apply default casing to a string
    pub fn default_casing(uncased_string: &str) -> String {

        uncased_string.to_uppercase()
    }

    //                                           "KEY"   , Minimum Value
    pub const MEMORY_CONFIG: (&str, usize)    = ("MEMORY",    100);
    pub const REGISTERS_CONFIG: (&str, usize) = ("REGISTERS",   3);
    pub const CLOCK_CONFIG: (&str, usize)     = ("CLOCK",       0);

    pub const DIRECTIVE_PREFIX: char = '!';
    pub const COMMENT_PREFIX: char   = ';';
    pub const DELIMITER: char        = '=';

    pub const VARIABLE_VALUE: isize = 0;
    pub const OPERAND_VALUE: &str   = "0";

    pub const EXIT_CODE: i32 = 0;

    pub const CSM_VERSION: &str   = "Rust 1.0";
    pub const CSM_EXTENSION: &str = ".csm";

    pub const ARGUMENT_PROCESSOR_ERRORS_HEADER: &str = "Argument Processor Errors:";
    pub const PREPROCESSOR_ERRORS_HEADER: &str       = "Preprocessor Errors:";
    pub const LEXER_ERRORS_HEADER: &str              = "Lexer Errors:";
    pub const PARSER_ERRORS_HEADER: &str             = "Parser Errors:";
    pub const INSTRUCTION_POOL_ERRORS_HEADER: &str   = "Instruction Pool Errors:";
    pub const SEMANTIC_ANALYSER_ERRORS_HEADER: &str  = "Semantic Analyser Errors:";

}

/// Namespace for all default values relating to the Lexer
pub mod lexerdefaults {

    pub const SEPARATOR: char = ',';

    pub const LEFT_SCOPE: &str  = "{";
    pub const RIGHT_SCOPE: &str = "}";
    pub const SCOPE_CHARS: &str = "{}";

    // pub const SPACING_CHARS: &str    = " \t"; // Currently Unused
    pub const LINE_BREAK_CHARS: &str = "\n";
    pub const WHITESPACE_CHARS: &str = " \t\n";

    // pub const LABEL_BEGIN_CHARS: &str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"; // Currently Unused
    pub const LABEL_CHARS: &str       = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890";

    pub const VALUE_BEGIN_CHARS: &str = "+-1234567890";
    pub const VALUE_CHARS: &str       = "1234567890";
    pub const VALUE_SIGNS : &str      = "+-";
}

/// Enum containing the possible types of symbols
#[derive(PartialEq)]
pub enum SymbolTypes {

    Branch,
    Variable,
    Procedure
}
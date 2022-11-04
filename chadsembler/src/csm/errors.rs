use std::{fmt, process};
use crate::csm::defaults::sysdefaults;

/// An error that can be found at a specific position
struct Error {

    row: usize,
    column: usize,
    error_type: &'static str,
    error_message: &'static str
}

impl fmt::Display for Error {

    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        
        write!(f, "{} {}:{} -> {}", self.error_type, self.row, self.column, self.error_message)
    }
}

/// Allows for errors to be accumulated and outputted all in one go in a compiler-like fashion
pub struct Errors {

    errors:Vec<Error>
}

impl Errors {

    /// Constructor for an 'Errors' object
    pub fn new() -> Self {

        Errors { errors: Vec::new() }
    }

    /// Append an Error object to the list of errors
    pub fn record_error(&mut self, row: usize, column: usize, error_type: &'static str, error_message: &'static str) {

        self.errors.push(Error { row, column, error_type, error_message })
    }

    /// If there are errors, will output all errors and exit the program
    pub fn get_errors(&self, header: &str) {

        if !self.errors.is_empty() {

            eprintln!("{header}");

            for error in &self.errors {

                eprintln!("{error}");
            }

            process::exit(sysdefaults::EXIT_CODE);
        }
    }
}

/// Dataclass grouping all error message related data
pub struct ErrorMessage {

    pub error_type: &'static str,
    pub error_message: &'static str
}

/// Namespace for all error messages which consist of an error type and the error message itself
pub mod errormessages {

    use crate::csm::errors::ErrorMessage;

    /// Namespace for all error types that an error message can contain
    pub mod errortypes {

        pub const SYNTAX: &str                  = "Syntax Error";
        pub const UNKNOWN_OPTION: &str          = "Unknown Option Error";
        pub const INVALID_VALUE: &str           = "Invalid Value Error";
        pub const MINIMUM_VALUE: &str           = "Minimum Value Error";
        pub const INVALID_LABEL: &str           = "Invalid Label Error";
        pub const BRANCH_LABEL: &str            = "Branch Label Error";
        pub const VARIABLE_LABEL: &str          = "Variable Label Error";
        pub const INVALID_OPERANDS: &str        = "Invalid Operands Error";
        pub const INVALID_ADDRESSING_MODE: &str = "Invalid Addressing Mode Error";
        pub const INVALID_REGISTER: &str        = "Invalid Register Error";
    }

    // Precompilation Errors:
    pub const SINGLE_KEY_VALUE_PAIR: ErrorMessage = ErrorMessage { error_type: errortypes::SYNTAX        , error_message: "Should contain a single key : value pair" };
    pub const UNKNOWN_CONFIG_OPTION: ErrorMessage = ErrorMessage { error_type: errortypes::UNKNOWN_OPTION, error_message: "Unknown configuration option" };
    pub const SIGN_SPECIFIED: ErrorMessage        = ErrorMessage { error_type: errortypes::INVALID_VALUE , error_message: "Don't specify the sign of a configuration value" };
    pub const INVALID_CONFIG_VALUE: ErrorMessage  = ErrorMessage { error_type: errortypes::INVALID_VALUE , error_message: "Configuration value must contain digits only" };
    pub const MINIMUM_VALUE: ErrorMessage         = ErrorMessage { error_type: errortypes::MINIMUM_VALUE , error_message: "Value is below its minimum" };

    // Lexer Errors:
    pub const INVALID_VALUE: ErrorMessage = ErrorMessage { error_type: errortypes::INVALID_VALUE, error_message: "A value can only contain digits" };
    pub const INVALID_LABEL: ErrorMessage = ErrorMessage { error_type: errortypes::INVALID_LABEL, error_message: "A Label can only contain letters, digits and underscores" };

    // Instruction Pool Errors:
    pub const PROC_TO_BRANCH_REDECL: ErrorMessage   = ErrorMessage { error_type: errortypes::BRANCH_LABEL  , error_message: "Attempting to redeclare a procedure label to a branch label" };
    pub const DUPLICATE_BRANCH: ErrorMessage        = ErrorMessage { error_type: errortypes::BRANCH_LABEL  , error_message: "Duplicate branch label found" };
    pub const DUPLICATE_VAR: ErrorMessage           = ErrorMessage { error_type: errortypes::VARIABLE_LABEL, error_message: "Duplicate variable label found"};
    pub const VAR_TO_BRANCH_REDECL: ErrorMessage    = ErrorMessage { error_type: errortypes::BRANCH_LABEL  , error_message: "Attempting to redeclare a variable label to a branch label" };
    pub const PROC_TO_VAR_REDECL: ErrorMessage      = ErrorMessage { error_type: errortypes::VARIABLE_LABEL, error_message: "Attempting to redeclare a procedure label to a variable label" };
    pub const BRACH_TO_VAR_REDECL: ErrorMessage     = ErrorMessage { error_type: errortypes::VARIABLE_LABEL, error_message: "Attempting to redeclare a branch label to a variable label" };

    // Semantic Analyser Errors:    
    pub const EXCESS_OPERANDS: ErrorMessage                  = ErrorMessage { error_type: errortypes::INVALID_OPERANDS       , error_message: "Too many operands supplied for the given instruction" };
    pub const REGISTER_MODE_MISMATCH: ErrorMessage           = ErrorMessage { error_type: errortypes::INVALID_ADDRESSING_MODE, error_message: "Non-register paired with register addressing mode" };
    pub const REGISTER_OPERAND_MISMATCH: ErrorMessage        = ErrorMessage { error_type: errortypes::INVALID_ADDRESSING_MODE, error_message: "register paired with non-register addressing mode" };
    pub const UNDECLARED_LABEL: ErrorMessage                 = ErrorMessage { error_type: errortypes::INVALID_LABEL          , error_message: "Attempting to use an undeclared label" };
    pub const GPR_ZERO: ErrorMessage                         = ErrorMessage { error_type: errortypes::INVALID_REGISTER       , error_message: "Cannot access GPR 0" };
    pub const NO_SOURCE_OPERAND: ErrorMessage                = ErrorMessage { error_type: errortypes::INVALID_OPERANDS       , error_message: "The source operand for a double operand instruction must be specified" };
    pub const NON_REGISTER_INP_OPERAND: ErrorMessage         = ErrorMessage { error_type: errortypes::INVALID_OPERANDS       , error_message: "INP instruction operand must be a register" };
    pub const IMMEDIATE_MODE: ErrorMessage                   = ErrorMessage { error_type: errortypes::INVALID_OPERANDS       , error_message: "Source operand of target instruction cannot be addressed in immediate mode" };
    pub const NON_REGISTER_DESTINATION_OPERAND: ErrorMessage = ErrorMessage { error_type: errortypes::INVALID_OPERANDS       , error_message: "Destination operand must be a register" };
}

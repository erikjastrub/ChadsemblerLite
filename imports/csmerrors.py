"""Namespace for all error related functinality"""

from dataclasses import dataclass
from meta import namespace

@dataclass(slots=True)
class Error:
    """An error that can be found at a specific position"""

    row: int
    column: int
    type: str
    message: str

class Errors:
    """Allows for errors to be accumulated and outputted all in one go in a compiler-like fashion"""

    def __init__(self):
        """Constructor for an 'Errors' object"""

        self.__errors: list[Error] = []

    def record_error(self, row: int, column: int, type: str, message: str) -> None:
        """Append an Error object to the list of errors"""

        self.__errors.append( Error(row, column, type, message) )

    def get_errors(self, header: str):
        """If there are errors, will output all errors and exit the program"""

        if self.__errors:

            print(header)

            for error in self.__errors:

                print(f"{error.type} {error.row}:{error.column} -> {error.message}")

            exit(-1)

@dataclass(slots=True)
class ErrorMessage:

    type: str
    message: str

class errormessages(metaclass=namespace):
    """Namespace for all error messages which consist of an error type and the error message itself"""

    class errortypes(metaclass=namespace):

        SYNTAX: str                  = "Syntax Error"
        UNKNOWN_OPTION: str          = "Unknown Option Error"
        INVALID_VALUE: str           = "Invalid Value Error"
        MINIMUM_VALUE: str           = "Minimum Value Error"
        INVALID_LABEL: str           = "Invalid Label Error"
        BRANCH_LABEL: str            = "Branch Label Error"
        VARIABLE_LABEL: str          = "Variable Label Error"
        INVALID_OPERANDS: str        = "Invalid Operands Error"
        INVALID_ADDRESSING_MODE: str = "Invalid Addressing Mode Error"
        INVALID_REGISTER: str        = "Invalid Register Error"

    # Precompilation Errors:
    SINGLE_KEY_VALUE_PAIR: ErrorMessage = ErrorMessage(errortypes.SYNTAX        , "Should contain a single key : value pair")
    UNKNOWN_CONFIG_OPTION: ErrorMessage = ErrorMessage(errortypes.UNKNOWN_OPTION, "Unknown configuration option")
    SIGN_SPECIFIED: ErrorMessage        = ErrorMessage(errortypes.INVALID_VALUE , "Don't specify the sign of a configuration value")
    INVALID_CONFIG_VALUE: ErrorMessage  = ErrorMessage(errortypes.INVALID_VALUE , "Configuration value must contain digits only")
    MINIMUM_VALUE: ErrorMessage         = ErrorMessage(errortypes.MINIMUM_VALUE , "Value is below its minimum")

    # Lexer Errors:
    INVALID_VALUE: ErrorMessage = ErrorMessage(errortypes.INVALID_VALUE, "Value contains non-value character")
    INVALID_LABEL: ErrorMessage = ErrorMessage(errortypes.INVALID_LABEL, "Label contains non-label character")

    # Instruction Pool Errors:
    PROC_TO_BRANCH_REDECL: ErrorMessage   = ErrorMessage(errortypes.BRANCH_LABEL  , "Attempting to redeclare a procedure label to a branch label")
    DUPLICATE_BRANCH: ErrorMessage        = ErrorMessage(errortypes.BRANCH_LABEL  , "Duplicate branch error found")
    DUPLICATE_VAR: ErrorMessage           = ErrorMessage(errortypes.VARIABLE_LABEL, "Duplicate variable label found")
    VAR_TO_BRANCH_REDECL: ErrorMessage    = ErrorMessage(errortypes.BRANCH_LABEL  , "Attempting to redeclare a variable label to a branch label")
    PROC_TO_VAR_REDECL: ErrorMessage      = ErrorMessage(errortypes.VARIABLE_LABEL, "Attempting to redeclare a procedure label to a variable label")
    BRANCH_TO_VAR_REDECL: ErrorMessage     = ErrorMessage(errortypes.VARIABLE_LABEL, "Attempting to redeclare a branch label to a variable label")

    # Code Generator Errors:    
    EXCESS_OPERANDS: ErrorMessage                  = ErrorMessage(errortypes.INVALID_OPERANDS, "Too many operands supplied for the given instruction")
    EXPLICIT_OPERAND: ErrorMessage                 = ErrorMessage(errortypes.INVALID_OPERANDS, "Operand must be explicitly stated for the given instruction")
    REGISTER_MODE_MISMATCH: ErrorMessage           = ErrorMessage(errortypes.INVALID_ADDRESSING_MODE, "Non-register paired with register addressing mode")
    REGISTER_OPERAND_MISMATCH: ErrorMessage        = ErrorMessage(errortypes.INVALID_ADDRESSING_MODE, "register paired with non-register addressing mode")
    UNDECLARED_LABEL: ErrorMessage                 = ErrorMessage(errortypes.INVALID_LABEL, "Attempting to use an undeclared label")
    GPR_ZERO: ErrorMessage                         = ErrorMessage(errortypes.INVALID_REGISTER, "Cannot access GPR 0")
    NO_SOURCE_OPERAND: ErrorMessage                = ErrorMessage(errortypes.INVALID_OPERANDS, "The source operand for a double operand instruction must be specified")
    NON_REGISTER_INP_OPERAND: ErrorMessage         = ErrorMessage(errortypes.INVALID_OPERANDS, "INP instruction operand must be a register")
    IMMEDIATE_MODE: ErrorMessage                   = ErrorMessage(errortypes.INVALID_OPERANDS, "Source operand of target instruction cannot be addressed in immediate mode")
    NON_REGISTER_DESTINATION_OPERAND: ErrorMessage = ErrorMessage(errortypes.INVALID_OPERANDS, "Destination operand must be a register")

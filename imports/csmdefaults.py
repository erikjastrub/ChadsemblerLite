from meta import namespace

class defaults(metaclass=namespace):
    """Namespace for all system wide default values and functionlity"""

    def wrap_bounds(lower: int, upper: int, value: int) -> int:
        """Ensure a value falls between the specified lower and upper limits (inclusive)
           Follows 2s complement bounds wrapping rules"""

        return (lower + (value - lower) % (upper + 1 - lower))

    def default_casing(uncased_string: str) -> str: 
            
        return uncased_string.upper()

    #                                        "KEY" , Minimum Value
    MEMORY_CONFIG: tuple[str, int]    =    "MEMORY",  100
    REGISTERS_CONFIG: tuple[str, int] = "REGISTERS",    3
    CLOCK_CONFIG: tuple[str, int]     =     "CLOCK",    0

    DIRECTIVE_PREFIX: str = '!'
    COMMENT_PREFIX: str = ';'
    DELIMITER: str = '='

    VARIABLE_VALUE: int = 0
    OPERAND_VALUE: str = "0"

    CSM_VERSION: str = "Python 1.0"
    CSM_EXTENSION: str = ".csm"

    ARGUMENT_PROCESSOR_ERRORS_HEADER: str = "Argument Processor Errors:"
    PREPROCESSOR_ERRORS_HEADER: str = "Preprocessor Errors:"
    LEXER_ERRORS_HEADER: str = "Lexer Errors:"
    PARSER_ERRORS_HEADER: str = "Parser Errors:"
    INSTRUCTION_POOL_ERRORS_HEADER: str = "Instruction Pool Errors:"
    SEMANTIC_ANALYSER_ERRORS_HEADER: str = "Semantic Analyser Errors:"

class lexerdefaults(metaclass=namespace):

    SEPARATOR: str = ','

    LEFT_SCOPE: str = '{'
    RIGHT_SCOPE: str = '}'
    SCOPE_CHARS: str = LEFT_SCOPE + RIGHT_SCOPE

    SPACING_CHARS: str = " \t\v"
    LINE_BREAK_CHARS: str = "\n\r\f"
    WHITESPACE_CHARS: str = SPACING_CHARS + LINE_BREAK_CHARS

    LABEL_BEGIN_CHARS: str = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_"
    LABEL_CHARS: str = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_" "1234567890"

    VALUE_BEGIN_CHARS: str = "+-" "1234567890"
    VALUE_CHARS: str = "1234567890"
    VALUE_SIGNS : str= "+-"

class symboltypes(metaclass=namespace):

    BRANCH: int = 1
    VARIABLE: int = 2
    PROCEDURE: int = 3
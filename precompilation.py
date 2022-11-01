"""Namespace for all precompilation functionality (pre- lexer, parser, etc.)"""

from csmtokens import tokenutils, PositionToken, UntypedToken
from csmdefaults import defaults, lexerdefaults
from csmerrors import Errors

class ArgumentProcessor:
    """Tokenise, parse and validate the command line arguments passed into the program"""

    def __init__(self, arguments: list[str], directive_prefix: str, delimiter: str, 
                 config_table: dict[str, int]) -> None:
        """Constructor for an 'ArgumentProcessor' object"""

        self.__arguments: list[str] = arguments
        self.__directive_prefix: str = directive_prefix
        self.__delimiter: str = delimiter
        self.__config_table: dict[str, int] = config_table

        self.__errors: Errors = Errors()
        self.__position: PositionToken = PositionToken(1, 1)

    def run(self) -> None:
        """Run the ArgumentProcessor"""

        for arg in self.__arguments:

            tokens: list[UntypedToken] = tokenutils.tokenise(arg, self.__directive_prefix, self.__delimiter, self.__position)
            tokenutils.parse(tokens, self.__config_table, self.__errors)

            self.__position.row += 1
            self.__position.column = 1

        self.__errors.get_errors(defaults.ARGUMENT_PROCESSOR_ERRORS_HEADER)

class Preprocessor:
    """Tokenise, parse and validate all directives in a source code file without modifying the source code"""

    def __init__(self, source_code: str, directive_prefix: str, comment_prefix: str, delimiter: str,
                 configuration_table: dict[str, int]) -> None:
        """Constructor for a 'Preprocessor' object"""

        self.__source_code: str = source_code
        self.__directive_prefix: str = directive_prefix
        self.__comment_prefix: str = comment_prefix
        self.__delimiter: str = delimiter
        self.__config_table: dict[str, int] = configuration_table

        self.__errors: Errors = Errors()
        self.__position: PositionToken = PositionToken(1, 1)
        self.__index: int = 0
        self.__length: int = len(source_code)


    def __skip_comment(self) -> None:
        """Iterate over and ignore a Chadsembly comment in a source code file"""

        while self.__index+1 < self.__length and \
              self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS:

            self.__index += 1

    def __get_directive(self) -> str:
        """Get the directive from the source code without removing it"""

        lower = self.__index
        self.__index += 1

        while self.__index < self.__length and \
              self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS and \
              self.__source_code[self.__index] != self.__directive_prefix and \
              self.__source_code[self.__index] != self.__comment_prefix:

            self.__index += 1

        directive = self.__source_code[lower:self.__index]
        self.__index -= 1

        return directive

    def __handle_directive(self) -> None:
        """Apply all validation checks over tokens generated from a directive"""

        tokens: list[UntypedToken] = tokenutils.tokenise(self.__get_directive(), self.__directive_prefix, self.__delimiter, self.__position )

        tokenutils.parse(tokens, self.__config_table, self.__errors)

    def run(self) -> None:
        """Run the Preprocessor"""

        while self.__index < self.__length:

            match self.__source_code[self.__index]:

                case self.__comment_prefix:

                    self.__skip_comment()
                
                case self.__directive_prefix:

                    self.__handle_directive()

            if self.__source_code[self.__index] in lexerdefaults.LINE_BREAK_CHARS:
                
                self.__position.row += 1
                self.__position.column = 0

            self.__index += 1
            self.__position.column += 1

        self.__errors.get_errors(defaults.PREPROCESSOR_ERRORS_HEADER)

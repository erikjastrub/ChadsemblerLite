"""Namespace for all precompilation functionality (pre- lexer, parser, etc.)"""

from csmtokens import PositionToken, UntypedToken
from csmdefaults import defaults, lexerdefaults
from csmerrors import errormessages, Errors

class ArgumentProcessor:
    """Tokenise, parse and validate the command line arguments passed into the program"""

    def __init__(self, arguments: list[str], directive_prefix: str, delimiter: str, 
                 config_table: dict[str, int]) -> None:
        """Constructor for a 'ArgumentProcessor' object"""

        self._directives: list[str] = arguments
        self._directive_prefix: str = directive_prefix
        self._delimiter: str = delimiter
        self._config_table: dict[str, int] = config_table

        self._errors: Errors = Errors()
        self._position: PositionToken = PositionToken(1, 1)

    def __tokenise(self, directive: str) -> list[UntypedToken]:
        """Split a directive into its individual components"""

        tokens: list[UntypedToken] = []
        length: int = len(directive)
        current_index: int = 0

        if directive and directive[0] == self._directive_prefix:

            current_index += 1
            self._position.column += 1

        while current_index < length:

            if directive[current_index] not in lexerdefaults.WHITESPACE_CHARS and \
               directive[current_index] != self._delimiter:

                lower_index = current_index

                while current_index < length and \
                      directive[current_index] not in lexerdefaults.WHITESPACE_CHARS and \
                      directive[current_index] != self._delimiter:

                    current_index += 1
                    self._position.column += 1

                tokens.append(
                    UntypedToken(
                        defaults.default_casing(directive[lower_index:current_index]),
                        self._position.row,
                        # Subtract the length of the token from the current self._position to get the starting self._position of the token 
                        self._position.column - (current_index - lower_index)
                    )
                )

            else:

                current_index += 1
                self._position.column += 1

        return tokens

    def __valid_number_tokens(self, tokens: list[UntypedToken]) -> bool:
        """Verify the amount of tokens generated"""

        if len(tokens) == 2:

            return True

        elif tokens:

            self._errors.record_error(tokens[0].row, tokens[0].column, errormessages.SINGLE_KEY_VALUE_PAIR.type, errormessages.SINGLE_KEY_VALUE_PAIR.message)
        
        return False

    def __valid_configuration_option(self, option: UntypedToken) -> bool:
        """Verify the validity of the config option"""

        if option.value in self._config_table:

            return True

        self._errors.record_error(option.row, option.column, errormessages.UNKNOWN_CONFIG_OPTION.type, errormessages.UNKNOWN_CONFIG_OPTION.message)
        return False

    def __contains_no_sign(self, value: UntypedToken) -> bool:
        """Verify the config value has no sign (+ or -)"""

        if value.value[0] not in lexerdefaults.VALUE_SIGNS:

            return True

        self._errors.record_error(value.row, value.column, errormessages.SIGN_SPECIFIED.type, errormessages.SIGN_SPECIFIED.message)
        return False

    def __valid_configuration_value(self, value: UntypedToken) -> bool:
        """Verify the validity of the config value"""

        for c in value.value:

            if not c.isdigit():

                self._errors.record_error(value.row, value.column, errormessages.INVALID_CONFIG_VALUE.type, errormessages.INVALID_CONFIG_VALUE.message)
                return False

        return True

    def __update_configuration_table(self, option: UntypedToken, value: UntypedToken) -> bool:
        """Update the config table if the option and value are valid"""

        # Previous checks will ensure this can always be converted to an int
        value_int = int(value.value)

        minimum = -1

        # Previous checks will ensure this will always correspond to a valid option
        for config in (defaults.CLOCK_CONFIG, defaults.REGISTERS_CONFIG, defaults.MEMORY_CONFIG):

            if config[0] == option.value:

                minimum = config[1]

        if value_int < minimum:
        
            self._errors.record_error(value.row, value.column, errormessages.MINIMUM_VALUE.type, errormessages.MINIMUM_VALUE.message)
            return False

        self._config_table[option.value] = value_int
        return True

    def _parse(self, directive: str) -> None:
        """Apply all validation checks on the tokens generated from a command-line argument"""

        tokens: list[UntypedToken] = self.__tokenise(directive)

        if self.__valid_number_tokens(tokens):

            option, value = tokens

            if self.__valid_configuration_option(option) and \
               self.__contains_no_sign(value) and \
               self.__valid_configuration_value(value):
            
                self.__update_configuration_table(option, value)

    def run(self) -> None:
        """Run the ArgumentProcessor"""

        for directive in self._directives:

            self._parse( directive )

            self._position.row += 1
            self._position.column = 0

        self._errors.get_errors(defaults.ARGUMENT_PROCESSOR_ERRORS_HEADER)

class Preprocessor(ArgumentProcessor):
    """Tokenise, parse and validate all directives in a source code file without modifying the source code"""

    def __init__(self, source_code: str, directive_prefix: str, comment_prefix: str, delimiter: str,
                 configuration_table: dict[str, int]) -> None:
        """Constructor for a 'Preprocessor' object"""

        super().__init__([], directive_prefix, delimiter, configuration_table)

        self.__source_code: str = source_code
        self.__comment_prefix: str = comment_prefix
        self.__index: int = 0
        self.__length: int = len(source_code)


    def __skip_comment(self) -> None:
        """Iterate over and ignore a Chadsembly comment in a source code file"""

        while self.__index < self.__length and \
              self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS:

            self.__index += 1

    def __get_directive(self) -> str:
        """Get the directive from the source code without removing it"""

        lower = self.__index
        self.__index += 1

        while self.__index < self.__length and \
              self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS and \
              self.__source_code[self.__index] != self._directive_prefix and \
              self.__source_code[self.__index] != self.__comment_prefix:

            self.__index += 1

        directive = self.__source_code[lower:self.__index]

        if directive == '!':

            self.__index -= 1
            self._position.column -= 1

        return directive

    def run(self) -> None:
        """Run the Preprocessor"""

        parallel_positions: list[PositionToken] = []

        while self.__index < self.__length:

            match self.__source_code[self.__index]:

                case self.__comment_prefix:

                    self.__skip_comment()
                
                case self._directive_prefix:

                    parallel_positions.append(PositionToken(self._position.row, self._position.column))
                    self._directives.append( self.__get_directive() )

            if self.__index < self.__length:

                self._position.advance_position(self.__source_code[self.__index], 1)

            self.__index += 1

        for directive, position in zip(self._directives, parallel_positions):

            self._position = position
            self._parse( directive )

        self._errors.get_errors(defaults.PREPROCESSOR_ERRORS_HEADER)

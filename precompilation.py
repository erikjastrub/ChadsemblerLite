"""Namespace for all precompilation functionality (pre- lexer, parser, etc.)"""

from csmtokens import tokenutils, PositionToken, UntypedToken
from csmdefaults import defaults, lexerdefaults
from csmerrors import errormessages, Errors

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

    def __tokenise(self, argument: str) -> list[UntypedToken]:
        """Split a directive into its individual components"""

        return tokenutils.tokenise(argument, self.__directive_prefix, self.__delimiter, self.__position)

    def __valid_number_tokens(self, tokens: list[UntypedToken]) -> bool:
        """Verify the amount of tokens generated"""

        if tokenutils.valid_number_tokens(tokens):

            return True

        elif tokens:

            self.__errors.record_error(tokens[0].row, 0, errormessages.SINGLE_KEY_VALUE_PAIR.type, errormessages.SINGLE_KEY_VALUE_PAIR.message)
        
        return False

    def __valid_configuration_option(self, option: UntypedToken) -> bool:
        """Verify the validity of the config option"""

        if tokenutils.valid_configuration_option(option, self.__config_table):

            return True

        self.__errors.record_error(option.row, option.column, errormessages.UNKNOWN_CONFIG_OPTION.type, errormessages.UNKNOWN_CONFIG_OPTION.message)
        return False

    def __contains_no_sign(self, value: UntypedToken) -> bool:
        """Verify the config value has no sign (+ or -)"""

        if tokenutils.contains_no_sign(value):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.SIGN_SPECIFIED.type, errormessages.SIGN_SPECIFIED.message)
        return False

    def __valid_configuration_value(self, value: UntypedToken) -> bool:
        """Verify the validity of the config value"""

        if tokenutils.valid_configuration_value(value):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.INVALID_CONFIG_VALUE.type, errormessages.INVALID_CONFIG_VALUE.message)
        return False

    def __update_configuration_table(self, option: UntypedToken, value: UntypedToken) -> bool:
        """Update the config table if the option and value are valid"""

        if tokenutils.update_configuration_table(option, value, self.__config_table):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.MINIMUM_VALUE.type, errormessages.MINIMUM_VALUE.message)
        return False

    def __parse(self, tokens: list[UntypedToken]) -> None:
        """Apply all validation checks on the tokens generated from a command-line argument"""

        if self.__valid_number_tokens(tokens):

            option, value = tokens

            if self.__valid_configuration_option(option) and \
               self.__contains_no_sign(value) and \
               self.__valid_configuration_value(value):
            
                self.__update_configuration_table(option, value)

    def run(self) -> None:
        """Run the ArgumentProcessor"""

        for arg in self.__arguments:

            self.__parse( self.__tokenise(arg) )

            self.__position.row += 1
            self.__position.column = 0

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

        while self.__index < self.__length and \
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

        if directive == '!':

            self.__index -= 1
            self.__position.column -= 1

        return directive

    def __tokenise(self, directive: str) -> list[UntypedToken]:
        """Split a directive into its individual components"""

        return tokenutils.tokenise(directive, self.__directive_prefix, self.__delimiter, self.__position)

    def __valid_number_tokens(self, tokens: list[UntypedToken]) -> bool:
        """Verify the amount of tokens generated"""

        if tokenutils.valid_number_tokens(tokens):

            return True

        elif tokens:

            self.__errors.record_error(tokens[0].row, tokens[0].column, errormessages.SINGLE_KEY_VALUE_PAIR.type, errormessages.SINGLE_KEY_VALUE_PAIR.message)
        
        return False

    def __valid_configuration_option(self, option: UntypedToken) -> bool:
        """Verify the validity of the config option"""

        if tokenutils.valid_configuration_option(option, self.__config_table):

            return True

        self.__errors.record_error(option.row, option.column, errormessages.UNKNOWN_CONFIG_OPTION.type, errormessages.UNKNOWN_CONFIG_OPTION.message)
        return False

    def __contains_no_sign(self, value: UntypedToken) -> bool:
        """Verify the config value has no sign (+ or -)"""

        if tokenutils.contains_no_sign(value):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.SIGN_SPECIFIED.type, errormessages.SIGN_SPECIFIED.message)
        return False

    def __valid_configuration_value(self, value: UntypedToken) -> bool:
        """Verify the validity of the config value"""

        if tokenutils.valid_configuration_value(value):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.INVALID_CONFIG_VALUE.type, errormessages.INVALID_CONFIG_VALUE.message)
        return False

    def __update_configuration_table(self, option: UntypedToken, value: UntypedToken) -> bool:
        """Update the config table if the option and value are valid"""

        if tokenutils.update_configuration_table(option, value, self.__config_table):

            return True

        self.__errors.record_error(value.row, value.column, errormessages.MINIMUM_VALUE.type, errormessages.MINIMUM_VALUE.message)
        return False

    def __parse(self, tokens: list[UntypedToken]) -> None:
        """Apply all validation checks on the tokens generated from a directive"""

        if self.__valid_number_tokens(tokens):

            # Unpack the tokens into a config option and config value
            option, value = tokens

            if self.__valid_configuration_option(option) and \
               self.__contains_no_sign(value) and \
               self.__valid_configuration_value(value):
            
                self.__update_configuration_table(option, value)

    def __handle_directive(self) -> None:
        """Apply all validation checks over tokens generated from a directive"""

        self.__parse( self.__tokenise( self.__get_directive() ) )

    def run(self) -> None:
        """Run the Preprocessor"""

        while self.__index < self.__length:

            match self.__source_code[self.__index]:

                case self.__comment_prefix:

                    self.__skip_comment()
                
                case self.__directive_prefix:

                    self.__handle_directive()

            if self.__index < self.__length:

                self.__position.advance_position(self.__source_code[self.__index], 1)

            self.__index += 1

        self.__errors.get_errors(defaults.PREPROCESSOR_ERRORS_HEADER)

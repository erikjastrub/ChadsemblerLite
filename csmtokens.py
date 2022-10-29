"""Namespace for all token types and token utilities"""

from dataclasses import dataclass
from csmerrors import Errors, errormessages
from csmdefaults import defaults, lexerdefaults

@dataclass(slots=True)
class PositionToken:
    """Stores the positional related data for a given item
       Can be thought of as a 2d coordinate"""

    row: int
    column: int

    def advance_position(self, current_char: str, reset_value: int=0) -> None:
        """Given the current_char, will update the row and column attributes accordingly
           Will reset the column attribute to the reset_value if a line break char is encountered"""

        if current_char in lexerdefaults.LINE_BREAK_CHARS:

            self.row += 1
            self.column = reset_value

        else:

            self.column += 1

@dataclass(slots=True)
class UntypedToken:
    """Stores both positional related data and a token_value for a given item"""

    value: str
    row: int
    column: int    

@dataclass(slots=True)
class TypedToken:
    """Stores the positional related data, token_value and token_type for a given item"""

    type: int
    value: str
    row: int
    column: int

class tokentypes:
    """Namespace for all token types that can be used in conjunction with the TypedToken class"""

    @staticmethod
    def type_to_str(token_type: int) -> str:
        """Returns the stringified token if valid otherwise will return an empty string"""

        # Using an array as a dictionary where the index is the token type
        # And the value at the index is the token as a string
        index_to_token: list[str] = [
            "End Of Statement",
            "Instruction",
            "Addressing Mode",
            "Value",
            "Register",
            "Label",
            "Instruction Separator",
            "Right Curly Brace",
            "Left Curly Brace",
            "Assembly Directive"
        ]

        if -1 < token_type < len(index_to_token):

            return index_to_token[token_type]

        return ""

    END: int = 0  # /
    INSTRUCTION: int = 1  # INP, OUT, ADD, etc.
    ADDRESSING_MODE: int = 2  # IMMEDIATE, REGISTER, #, %, etc.
    VALUE: int = 3  # Any integer value (E.g. 5, 200, -100, etc.)
    REGISTER: int = 4  # ACC, IP, etc.
    LABEL: int = 5  # Any valid label (E.g. NUM, FUNC, etc.)
    SEPARATOR: int = 6  # ,
    LEFT_BRACE: int = 7  # {
    RIGHT_BRACE: int = 8  # }
    ASSEMBLY_DIRECTIVE: int = 9  # DAT

class tokenutils:
    """namespace for all token parsing functionality"""

    @staticmethod
    def tokenise(text: str, prefix: str, delimiter: str, position: PositionToken) -> list[UntypedToken]:
        """tokenise a string into its individual components, separating on the delimiter and ignoring the prefix"""

        tokens: list[UntypedToken] = []
        length: int = len(text)
        current_index: int = 0

        if text and text[0] == prefix:

            current_index += 1
            position.column += 1

        while current_index < length:

            if text[current_index] not in lexerdefaults.WHITESPACE_CHARS and \
               text[current_index] != delimiter:

                lower_index = current_index

                while current_index < length and \
                      text[current_index] not in lexerdefaults.WHITESPACE_CHARS and \
                      text[current_index] != delimiter:

                    current_index += 1
                    position.column += 1

                tokens.append(
                    UntypedToken(
                        defaults.default_casing(text[lower_index:current_index]),
                        position.row,
                        # Subtract the length of the token from the current position to get the starting position of the token 
                        position.column - (current_index - lower_index)
                    )
                )

            else:

                current_index += 1
                position.column += 1

        return tokens

    @staticmethod
    def valid_number_tokens(tokens: list[UntypedToken], errors: Errors) -> bool:
        """Verify the amount of tokens generated"""

        if len(tokens) == 2:

            return True

        elif len(tokens) > 0:

            errors.record_error(tokens[0].row, tokens[0].column, errormessages.SINGLE_KEY_VALUE_PAIR.type, errormessages.SINGLE_KEY_VALUE_PAIR.message)

        return False

    @staticmethod
    def valid_config_option(option: UntypedToken, configuration_table: dict[str, int], errors: Errors) -> bool:
        """Verify the validity of the config option"""

        if option.value in configuration_table:

            return True

        else:

            errors.record_error(option.row, option.column, errormessages.UNKNOWN_CONFIG_OPTION.type, errormessages.UNKNOWN_CONFIG_OPTION.message)
            return False

    @staticmethod
    def contains_no_sign(value: UntypedToken, errors: Errors) -> bool:
        """Verify the config value has no sign (+ or -)"""

        if value.value[0] in lexerdefaults.VALUE_SIGNS:

            errors.record_error(value.row, value.column, errormessages.SIGN_SPECIFIED.type, errormessages.SIGN_SPECIFIED.message)
            return False

        else:

            return True

    @staticmethod
    def valid_config_value(value: UntypedToken, errors: Errors) -> bool:
        """Verify the validity of the config value"""

        for c in value.value:

            if not c.isdigit():

                errors.record_error(value.row, value.column, errormessages.INVALID_CONFIG_VALUE.type, errormessages.INVALID_CONFIG_VALUE.message)
                return False

        return True

    @staticmethod
    def update_config_table(option: UntypedToken, value: UntypedToken, configuration_table: dict[str, int], errors: Errors) -> bool:
        """Update the config table if the option and value are valid"""

        # Previous checks will ensure this can always be converted to an int
        value_int = int(value.value)

        minimum = 0

        # Previous checks will ensure this will always correspond to a valid option
        for config in (defaults.CLOCK_CONFIG, defaults.REGISTERS_CONFIG, defaults.MEMORY_CONFIG):

            if config[0] == option.value:

                minimum = config[1]

        if value_int < minimum:

            errors.record_error(value.row, value.column, errormessages.MINIMUM_VALUE.type, errormessages.MINIMUM_VALUE.message);
            return False

        else: 
            
            configuration_table[option.value] = value_int
            return True

    @staticmethod
    def parse(tokens: list[UntypedToken], config_table: dict[str, int], errors: Errors):
        """Convenience method, wrapping all other methods together"""

        if tokenutils.valid_number_tokens(tokens, errors):

            option: UntypedToken = tokens[0]
            value: UntypedToken = tokens[1]

            if tokenutils.valid_config_option(option, config_table, errors) and \
               tokenutils.contains_no_sign(value, errors) and \
               tokenutils.valid_config_value(value, errors):

                tokenutils.update_config_table(option, value, config_table, errors)

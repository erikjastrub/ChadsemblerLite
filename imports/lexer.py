"""Module containing the Lexer (stage 1/5 of the pipeline)"""

from csmerrors import Errors, errormessages
from csmtokens import PositionToken, TypedToken, tokentypes
from csmdefaults import lexerdefaults, defaults
from architecture import addressingmodes, registers, instructions

class Lexer:
    """Tokenise the source code, ignoring any comments and directives"""

    def __init__(self, source_code: str, directive_prefix: str, comment_prefix: str) -> None:
        """Constructor for a 'Lexer' object"""

        self.__source_code: str = source_code
        self.__comment_prefix: str = comment_prefix
        self.__directive_prefix: str = directive_prefix

        self.__index: int = 0
        self.__length: int = len(source_code)
        self.__errors: Errors = Errors()
        self.__position: PositionToken = PositionToken(1, 1)

    def __skip_line(self) -> None:
        """Iterate until a new line character is reached"""

        # Only iterate while the next character is not a line-breaking character

        # Check the next index is indexable to ensure no over-increment occurs
        while self.__index+1 < self.__length and \
              self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS:

            self.__index += 1

    def __get_token(self) -> str:
        """Read the current token at the current index held"""

        lower: int = self.__index

        # Iterate until the beginning of another possible token
        while   self.__index < self.__length and \
                self.__source_code[self.__index] != self.__comment_prefix and \
                self.__source_code[self.__index] != self.__directive_prefix and \
                self.__source_code[self.__index] != lexerdefaults.SEPARATOR and \
                self.__source_code[self.__index] not in lexerdefaults.WHITESPACE_CHARS and \
                self.__source_code[self.__index] not in lexerdefaults.LINE_BREAK_CHARS and \
                self.__source_code[self.__index] not in lexerdefaults.SCOPE_CHARS and \
                self.__source_code[self.__index] not in addressingmodes.ADDRESSING_MODES:

            self.__index += 1

        # Default-casing to standardise how tokens are processed
        return defaults.default_casing(self.__source_code[lower:self.__index])

    def __is_gpr(self, token: str) -> str:
        """Check if a token is a General Purpose Register - GPR
           If the token isn't a GPR then an empty string is returned
           If it is then a string containing the GPR number is returned"""

        # The syntax for a GPR can look like: "REG5"
        # To extract the digits at the end, a pointer to the end of the token is initialised
        # and then decremented until the beginning of the digits is found
        # The digits can then be extracted as a substring

        lower: int = len(token)

        while token[lower-1].isdigit():

            lower -= 1

        register: str = token[:lower]
        digits: str = token[lower:]

        return digits if register in registers.GPR.variants else ""

    def __get_type(self, token: str) -> int:
        """Will determine and return the token type of a given token"""

        if token in instructions.INSTRUCTION_SET:

            return tokentypes.INSTRUCTION

        elif token in registers.SPECIAL_PURPOSE_REGISTERS:

            return tokentypes.REGISTER

        elif token in addressingmodes.ADDRESSING_MODES:

            return tokentypes.ADDRESSING_MODE

        elif token == instructions.DAT:

            return tokentypes.ASSEMBLY_DIRECTIVE

        else:
            # A label token can be inferred if no special-cases are matched
            return tokentypes.LABEL

    def __handle_value(self, token: str) -> None:
        """Will verify the validity of a value token, recording errors if invalid"""

        index, length = 1 if token[0] in lexerdefaults.VALUE_SIGNS else 0, len(token)

        while index < length:

            if token[index] not in lexerdefaults.VALUE_CHARS:

                self.__errors.record_error(self.__position.row, self.__position.column+index,
                                    errormessages.INVALID_VALUE.type, errormessages.INVALID_VALUE.message)

            index += 1

    def __handle_label(self, token: str) -> None:
        """Will verify the validity of a label token, recording errors if invalid"""

        index, length = 0, len(token)

        while index < length:

            if token[index] not in lexerdefaults.LABEL_CHARS:

                self.__errors.record_error(self.__position.row, self.__position.column+index,
                                    errormessages.INVALID_LABEL.type, errormessages.INVALID_LABEL.message)
            index += 1

    def __handle_token(self) -> TypedToken:
        """Will determine the token type and call the appropriate methods to verify the validity"""

        token: str = self.__get_token()

        if token[0] in lexerdefaults.VALUE_BEGIN_CHARS:

            self.__handle_value(token)
            return TypedToken(tokentypes.VALUE, token, self.__position.row, self.__position.column)

        isGPR: str = self.__is_gpr(token)

        if isGPR:

            return TypedToken(tokentypes.REGISTER, isGPR, self.__position.row, self.__position.column)

        token_type: int = self.__get_type(token)

        match token_type:

            case tokentypes.ADDRESSING_MODE:

                token = addressingmodes.ADDRESSING_MODES[token].symbol

            case tokentypes.LABEL:

                self.__handle_label(token)

        return TypedToken(token_type, token, self.__position.row, self.__position.column)

    def __tokenise(self) -> list[TypedToken]:
        """Will iterate over and split the source code into its lexemes
           Comments and directives are ignored"""

        tokens: list[TypedToken] = []

        while self.__index < self.__length:

            current_char: str = self.__source_code[self.__index]

            if current_char == self.__directive_prefix or \
               current_char == self.__comment_prefix:

               self.__skip_line()
               tokens.append(TypedToken(
                    tokentypes.END, lexerdefaults.LINE_BREAK_CHARS, 
                    self.__position.row, self.__position.column
                ))

            elif current_char in lexerdefaults.LINE_BREAK_CHARS and \
                 tokens and tokens[-1].type != tokentypes.END: # Avoid appending non-necessary duplicate END tokens

                tokens.append(TypedToken(
                    tokentypes.END, '/', 
                    self.__position.row, self.__position.column
                ))

            elif current_char in lexerdefaults.LEFT_SCOPE:

                tokens.append(TypedToken(
                    tokentypes.LEFT_BRACE, lexerdefaults.LEFT_SCOPE, 
                    self.__position.row, self.__position.column
                ))

            elif current_char in lexerdefaults.RIGHT_SCOPE:

                tokens.append(TypedToken(
                    tokentypes.RIGHT_BRACE, lexerdefaults.RIGHT_SCOPE, 
                    self.__position.row, self.__position.column
                ))

            elif current_char in lexerdefaults.SEPARATOR:

                tokens.append(TypedToken(
                    tokentypes.SEPARATOR, lexerdefaults.SEPARATOR, 
                    self.__position.row, self.__position.column
                ))

            elif addressingmodes.ADDRESSING_MODES.get(current_char) is not None:

                tokens.append(TypedToken(
                    tokentypes.ADDRESSING_MODE, current_char, 
                    self.__position.row, self.__position.column
                ))

            elif current_char not in lexerdefaults.WHITESPACE_CHARS:

                token: TypedToken = self.__handle_token()

                # Compensate for over-increment
                self.__index -= 1
                self.__position.column += len(token.value) - 1

                tokens.append(token)

            self.__position.advance_position(self.__source_code[self.__index], 1)
            self.__index += 1

        tokens.append(TypedToken(
            tokentypes.END, lexerdefaults.LINE_BREAK_CHARS, 
            self.__position.row, self.__position.column
        ))

        return tokens

    def run(self) -> list[TypedToken]:
        """Run the Lexer
           Will return the generated tokens from the source code"""

        tokens: list[TypedToken] = self.__tokenise()

        self.__errors.get_errors(defaults.LEXER_ERRORS_HEADER)

        return tokens

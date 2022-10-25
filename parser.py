"""Module containing the Parser (stage 2/5 of the pipeline)"""

from csmtokens import TypedToken, tokentypes
from csmdefaults import defaults

class Parser:
    """Validate the syntax of the language"""

    END: list[int] = [tokentypes.END, tokentypes.INSTRUCTION, tokentypes.LABEL, tokentypes.RIGHT_BRACE, tokentypes.LEFT_BRACE]
    INSTRUCTION: list[int] = [tokentypes.END, tokentypes.ADDRESSING_MODE, tokentypes.VALUE, tokentypes.REGISTER, tokentypes.LABEL, tokentypes.RIGHT_BRACE]
    ADDRESSING_MODE: list[int] = [tokentypes.VALUE, tokentypes.REGISTER, tokentypes.LABEL]
    OPERAND: list[int] = [tokentypes.END, tokentypes.SEPARATOR, tokentypes.RIGHT_BRACE, tokentypes.LEFT_BRACE]  # Value / Register
    LABEL: list[int] = [tokentypes.END, tokentypes.SEPARATOR, tokentypes.INSTRUCTION, tokentypes.RIGHT_BRACE, tokentypes.LEFT_BRACE, tokentypes.ASSEMBLY_DIRECTIVE]
    SEPARATOR: list[int] = [tokentypes.ADDRESSING_MODE, tokentypes.VALUE, tokentypes.REGISTER, tokentypes.LABEL]
    SCOPE: list[int] = [tokentypes.END]
    ASSEMBLY_DIRECTIVE: list[int] = [tokentypes.END, tokentypes.VALUE]

    def __init__(self, tokens: list[TypedToken]) -> None:
        """Constructor for a 'Parser' object"""
        
        self.__tokens: list[TypedToken] = tokens

        self.__errors: list[tuple[TypedToken, TypedToken]] = []
        self.__previous_scope: TypedToken | None = None

    def __record_error(self, first_token: TypedToken, second_token: TypedToken) -> None:
        """Append a tuple containing the syntactically invalid tokens"""

        self.__errors.append( (first_token, second_token) )

    def __get_errors(self) -> None:
        """If there are errors, will output all errors and exit the program"""

        if self.__errors:

            print(defaults.PARSER_ERRORS_HEADER)

            for error in self.__errors: 
                
                if error[0].type == tokentypes.END:

                    print(f"Invalid Syntax Error {error[1].row}:{error[1].column} -> Statement cannot begin with a {tokentypes.type_to_str(error[1].type)}")

                elif error[1].type == tokentypes.END:

                    print(f"Invalid Syntax Error {error[0].row}:{error[0].column} -> Statement cannot end with a {tokentypes.type_to_str(error[0].type)}")

                elif error[0].type == tokentypes.LEFT_BRACE and error[1].type == tokentypes.LEFT_BRACE:

                    print(f"Invalid Syntax Error {error[0].row}:{error[0].column} -> Block scope was opened but never closed")

                elif error[0].type == tokentypes.RIGHT_BRACE and error[1].type == tokentypes.RIGHT_BRACE:

                    print(f"Invalid Syntax Error {error[0].row} at position {error[0].column} -> Block scope was opened but never closed")

                else:

                    print(f"Invalid Syntax Error {error[1].row}:{error[1].column} -> {tokentypes.type_to_str(error[1].type)} was found after {tokentypes.type_to_str(error[0].type)}")

            exit(-1)

    def __possible_tokens(self, token: TypedToken) -> list[int]:
        """Return the expected tokens that should come after a given token"""

        match token.type:

            case tokentypes.END: 
                
                return Parser.END

            case tokentypes.INSTRUCTION: 
                
                return Parser.INSTRUCTION

            case tokentypes.ADDRESSING_MODE: 
                
                return Parser.ADDRESSING_MODE

            case tokentypes.VALUE | tokentypes.REGISTER: 
                
                return Parser.OPERAND

            case tokentypes.LABEL: 
                
                return Parser.LABEL

            case tokentypes.SEPARATOR: 
                
                return Parser.SEPARATOR

            case tokentypes.RIGHT_BRACE | tokentypes.LEFT_BRACE: 
                
                return Parser.SCOPE

            case tokentypes.ASSEMBLY_DIRECTIVE: 
                
                return Parser.ASSEMBLY_DIRECTIVE

    def __validate_scope(self, token: TypedToken) -> None:
        """Verify a block scope is valid"""

        match token.type:

            case tokentypes.LEFT_BRACE:

                if self.__previous_scope is None:

                    self.__previous_scope = token

                else:

                    self.__record_error(token, token)

            case tokentypes.RIGHT_BRACE:

                if self.__previous_scope is None:

                    self.__record_error(token, token)

                else:

                    self.__previous_scope = None
    
    def __parse(self) -> None:
        """Verify the tokens match the syntax of the language"""

        # Initialise with an END token to open the start of a new statement
        previous: TypedToken = TypedToken(tokentypes.END, '', -1, -1)

        for token in self.__tokens:

            if token.type == tokentypes.LEFT_BRACE or \
               token.type == tokentypes.RIGHT_BRACE:

               self.__validate_scope(token)

            if token.type not in self.__possible_tokens(previous):

                self.__record_error(previous, token)

            previous = token

        # Ensure there is no unclosed block scope
        if self.__previous_scope is not None:

            left_brace: TypedToken = TypedToken(tokentypes.LEFT_BRACE, '', -1, -1)
            self.__record_error(left_brace, left_brace)

    def run(self) -> None:
        """Run the Parser"""

        self.__parse()
        self.__get_errors()

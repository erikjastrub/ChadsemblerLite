"""Namespace for all token types and token utilities"""

from dataclasses import dataclass
import csmdefaults

@dataclass(slots=True)
class PositionToken:
    """Stores the positional related data for a given item
       Can be thought of as a 2d coordinate"""

    row: int
    column: int

    def advance_position(self, current_char: str, reset_value: int=0) -> None:
        """Given the current_char, will update the row and column attributes accordingly
           Will reset the column attribute to the reset_value if a line break char is encountered"""

        if current_char in csmdefaults.lexerdefaults.LINE_BREAK_CHARS:

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

    def __repr__(self) -> str:
        return f"({self.value})"

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

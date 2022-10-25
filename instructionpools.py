"""Module containing the InstructionPools class - a helper class to make it easier to semantically analyse a token stream"""

from csmerrors import Errors, errormessages
from csmtokens import TypedToken, tokentypes
from csmdefaults import defaults, symboltypes
from csmstructs import Symbol, Scope

class InstructionPools:
    """Split a token stream into its relevant scopes
       Variables found will be removed from the token stream and marked in the symbol table"""

    def __init__(self, tokens: list[TypedToken]) -> None:
        """Constructor for an 'InstructionPools' object"""
        
        self.__tokens: list[TypedToken] = tokens

        self.__index: int = 0
        self.__length: int = len(tokens)
        self.__errors: Errors = Errors()

    def __get_scope(self) -> list[TypedToken]:
        """Accumulate all tokens encountered in the scope"""

        token: TypedToken = self.__tokens[self.__index]
        tokens: list[TypedToken] = []

        while token.type != tokentypes.RIGHT_BRACE:

            tokens.append(token)
            self.__index += 1
            token = self.__tokens[self.__index]

        self.__index += 1
        return tokens

    def __get_scopes(self, global_scope: Scope, procedure_scopes: dict[str, Scope]) -> None:
        """Find and accumulate all scopes found within the token stream"""

        while self.__index < self.__length:

            token: TypedToken = self.__tokens[self.__index]

            if token.type == tokentypes.LEFT_BRACE:

                # Pop garbage tokens out of the global scope
                procedure_token: TypedToken = global_scope.tokens.pop()

                if procedure_token.type == tokentypes.END:

                    procedure_token: TypedToken = global_scope.tokens.pop()

                self.__index += 2
                tokens: list[TypedToken] = self.__get_scope()

                procedure_scopes[procedure_token.value] = Scope(tokens, {}, 0, 0)

            else: 
                
                global_scope.tokens.append(token)

            self.__index += 1

    def __update_global_scope(self, global_scope: Scope, procedure_scopes: dict[str, Scope]) -> None:
        """Append all procedure identifiers to the global scope
           This allows them to be called from the global scope"""

        for scope in procedure_scopes:

            global_scope.symbol_table[scope] = Symbol(-1, symboltypes.PROCEDURE)

    def __handle_symbol(self, symbol: Symbol, current_token: TypedToken, next_token: TypedToken) -> None:
        """Verify the validity of a symbol"""

        match next_token.type:

            # Branch Label
            case tokentypes.INSTRUCTION:

                match symbol.type:

                    case symboltypes.PROCEDURE:

                        self.__errors.record_error(current_token.row, current_token.column, errormessages.PROC_TO_BRANCH_REDECL.type, errormessages.PROC_TO_BRANCH_REDECL.message)

                    case symboltypes.BRANCH:

                        self.__errors.record_error(current_token.row, current_token.column, errormessages.DUPLICATE_BRANCH.type, errormessages.DUPLICATE_BRANCH.message)

                    case symboltypes.VARIABLE:

                        self.__errors.record_error(current_token.row, current_token.column, errormessages.VAR_TO_BRANCH_REDECL.type, errormessages.VAR_TO_BRANCH_REDECL.message)

            # Variable Label
            case tokentypes.ASSEMBLY_DIRECTIVE:

                match symbol.type:

                    case symboltypes.PROCEDURE:

                        self.__errors.record_error(current_token.row, current_token.column, errormessages.PROC_TO_VAR_REDECL.type, errormessages.PROC_TO_VAR_REDECL.message)

                    case symboltypes.BRANCH:

                        self.__errors.record_error(current_token.row, current_token.column, errormessages.BRANCH_TO_VAR_REDECL.type, errormessages.BRANCH_TO_VAR_REDECL.message)

                    case symboltypes.VARIABLE:
                        
                        self.__errors.record_error(current_token.row, current_token.column, errormessages.DUPLICATE_VAR.type, errormessages.DUPLICATE_VAR.message)

    def __remove_variable(self, scope: Scope, index: int) -> None:
        """Remove the tokens representing a variable from the token stream"""

        while scope.tokens and scope.tokens[index].type != tokentypes.END:

            scope.tokens.pop(index)

    def __handle_label(self, scope: Scope, index: int, statements: int) -> None:
        """Verify and update the symbol table accordingly for a given label"""

        first_token: TypedToken = scope.tokens[index]  # The label token
        second_token: TypedToken = scope.tokens[index+1]  # Either a directive, instruction or end token
        third_token: TypedToken = scope.tokens[index+2]  # Either an end or value token

        if first_token.value in scope.symbol_table:

            symbol: Symbol = scope.symbol_table[first_token.value]
            self.__handle_symbol(symbol, first_token, second_token)

        else:

            symbol: Symbol = Symbol(-1, symboltypes.VARIABLE)

            match second_token.type:

                case tokentypes.ASSEMBLY_DIRECTIVE:  # Label inferred to be a variable declaration

                    symbol.value = int(third_token.value) \
                                   if third_token.type == tokentypes.VALUE \
                                   else defaults.VARIABLE_VALUE
                                   
                    self.__remove_variable(scope, index)
                    scope.number_variables += 1

                case tokentypes.INSTRUCTION:  # Label inferred to be a branch declaration

                    symbol.type = symboltypes.BRANCH
                    symbol.value = statements

            scope.symbol_table[first_token.value] = symbol

    def __update_symbol_table(self, scope: Scope):
        """Update the symbol table with its labels for a given scope"""

        statements: int = 0

        for index, token in enumerate(scope.tokens):

            if token.type == tokentypes.LABEL and \
               scope.tokens[index+1].type in (tokentypes.INSTRUCTION, tokentypes.ASSEMBLY_DIRECTIVE):

                self.__handle_label(scope, index, statements)

            elif token.type == tokentypes.INSTRUCTION:

                statements += 1
        
        scope.number_instructions = statements

    def run(self) -> tuple[Scope, dict[str, Scope]]:
        """Run the InstructionPools class
           Will return the global and procedure scopes"""

        global_scope: Scope = Scope([], {}, 0, 0)
        procedure_scopes: dict[str, Scope] = {}

        self.__get_scopes(global_scope, procedure_scopes)

        self.__update_global_scope(global_scope, procedure_scopes)

        self.__update_symbol_table(global_scope)

        for scope in procedure_scopes.values():

            self.__update_symbol_table(scope)

        self.__errors.get_errors(defaults.INSTRUCTION_POOL_ERRORS_HEADER)

        return (global_scope, procedure_scopes)

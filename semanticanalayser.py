"""Module containing the SemanticAnalyser (stage 3/5 of the pipeline)"""

from architecture import addressingmodes, instructions, registers
from csmdefaults import defaults, lexerdefaults
from csmtokens import TypedToken, tokentypes
from csmerrors import Errors, errormessages
from csmstructs import Operand, Instruction, Scope

class SemanticAnalyser:
    """Will ensure the semantic validity of a program
       Tokens can be syntactically correct but not a valid program"""

    def __init__(self, global_scope: Scope, procedure_scopes: dict[str, Scope]) -> None:
        """Constructor for a 'SemanticAnalyser' object"""
        
        self.__global_scope: Scope = global_scope
        self.__procedure_scopes: dict[str, Scope] = procedure_scopes

        self.__errors: Errors = Errors()

    def __count_operands(self, index: int, scope: Scope) -> int:
        """Return the number of operands found for an instruction in the token stream"""

        operands: int = 0
        token_type: int = scope.tokens[index].type

        while token_type != tokentypes.END:

            if token_type == tokentypes.VALUE or \
               token_type == tokentypes.REGISTER or \
               token_type == tokentypes.LABEL:

                operands += 1

            index += 1
            token_type = scope.tokens[index].type

        return operands

    def __analyse_addressing_mode(self, operand: Operand) -> None:
        """Verify the semantic validity of the addressing mode of an operand"""

        if operand.addressing_mode.value == addressingmodes.REGISTER.symbol and \
           operand.value.type != tokentypes.REGISTER:

            self.__errors.record_error(operand.value.row, operand.value.column, errormessages.REGISTER_MODE_MISMATCH.type, errormessages.REGISTER_MODE_MISMATCH.message)

        elif operand.addressing_mode.value != addressingmodes.REGISTER.symbol and \
             operand.value.type == tokentypes.REGISTER:

            self.__errors.record_error(operand.value.row, operand.value.column, errormessages.REGISTER_OPERAND_MISMATCH.type, errormessages.REGISTER_OPERAND_MISMATCH.message)

    def __analyse_operand_value(self, operand: Operand, scope: Scope) -> None:
        """Verify the semantic validity of the value of an operand"""

        if operand.value.type == tokentypes.LABEL and \
           operand.value.value not in self.__global_scope.symbol_table and \
           operand.value.value not in scope.symbol_table:

            self.__errors.record_error(operand.value.row, operand.value.column, errormessages.UNDECLARED_LABEL.type, errormessages.UNDECLARED_LABEL.message)

        elif operand.value.type == tokentypes.REGISTER and \
             operand.value.value == "0":

            self.__errors.record_error(operand.value.row, operand.value.column, errormessages.GPR_ZERO.type, errormessages.GPR_ZERO.message)

    def __analyse_operand(self, operand: Operand, scope: Scope) -> None:
        """Verify the semantic validity of an operand as a whole"""

        self.__analyse_addressing_mode(operand)

        self.__analyse_operand_value(operand, scope)

    def __get_operand(self, index: int, scope: Scope) -> Operand:
        """Get the operand of an instruction
           Will insert a default operand into the token stream if not present
           index: int -> the beginning index of the operand"""

        token: TypedToken = scope.tokens[index]

        match token.type:

            case tokentypes.SEPARATOR:

                return self.__get_operand(index+1, scope)

            case tokentypes.END:

                scope.tokens.insert(index, TypedToken(tokentypes.REGISTER, registers.ACCUMULATOR.register, -1, -1))
                scope.tokens.insert(index, TypedToken(tokentypes.ADDRESSING_MODE, addressingmodes.REGISTER.symbol, -1, -1))

                if scope.tokens[index-1].type in (tokentypes.REGISTER, tokentypes.LABEL, tokentypes.VALUE):

                    scope.tokens.insert(index, TypedToken(tokentypes.SEPARATOR, lexerdefaults.SEPARATOR, -1, -1))
                    index += 1

            case tokentypes.REGISTER:

                scope.tokens.insert(index, TypedToken(tokentypes.ADDRESSING_MODE, addressingmodes.REGISTER.symbol, -1, -1))

            case tokentypes.LABEL | tokentypes.VALUE:

                scope.tokens.insert(index, TypedToken(tokentypes.ADDRESSING_MODE, addressingmodes.DIRECT.symbol, -1, -1))

        return Operand(scope.tokens[index], scope.tokens[index+1])

    def __analyse_instruction(self, index: int, scope: Scope) -> None:
        """Verify the semantic validity of an instruction"""

        token: TypedToken = scope.tokens[index]

        #                            An instruction will always be returned
        instruction: Instruction = instructions.get_instruction(token.value)
        number_operands: int = self.__count_operands(index, scope)

        if number_operands > instruction.operands:

            self.__errors.record_error(token.row, token.column, errormessages.EXCESS_OPERANDS.type, errormessages.EXCESS_OPERANDS.message)

        else:

            if instruction.operands > 1 and \
               scope.tokens[index+1].type == tokentypes.END:

               self.__errors.record_error(token.row, token.column, errormessages.NO_SOURCE_OPERAND.type, errormessages.NO_SOURCE_OPERAND.message)

            if instruction.operands > 0:

                source_operand = self.__get_operand(index+1, scope)
                self.__analyse_operand(source_operand, scope)

                # Various Semantic Checks
                if instruction == instructions.INP and \
                   source_operand.addressing_mode.value != addressingmodes.REGISTER.symbol:

                    self.__errors.record_error(token.row, token.column, errormessages.NON_REGISTER_INP_OPERAND.type, errormessages.NON_REGISTER_INP_OPERAND.message)

                if instruction in instructions.NON_IMMEDIATE_MODE_INSTRUCTIONS and \
                   source_operand.addressing_mode.value == addressingmodes.IMMEDIATE.symbol:

                    self.__errors.record_error(token.row, token.column, errormessages.IMMEDIATE_MODE.type, errormessages.IMMEDIATE_MODE.message)

            if instruction.operands > 1:

                destination_operand = self.__get_operand(index+3, scope)
                self.__analyse_operand(destination_operand, scope)

                # Various Semantic Checks
                if destination_operand.addressing_mode.value != addressingmodes.REGISTER.symbol:

                    self.__errors.record_error(token.row, token.column, errormessages.NON_REGISTER_DESTINATION_OPERAND.type, errormessages.NON_REGISTER_DESTINATION_OPERAND.message)

    def __semantic_analyse(self, scope: Scope) -> None:
        """Semantically analyse a scope"""

        for index, token in enumerate(scope.tokens):

            if token.type == tokentypes.INSTRUCTION:

                self.__analyse_instruction(index, scope)

    def run(self) -> None:
        """Run the SemanticAnalyser"""

        self.__semantic_analyse(self.__global_scope)

        for scope in self.__procedure_scopes.values():

            self.__semantic_analyse(scope)

        self.__errors.get_errors(defaults.SEMANTIC_ANALYSER_ERRORS_HEADER)

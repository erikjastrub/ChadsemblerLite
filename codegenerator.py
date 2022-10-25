"""Module containing the CodeGenerator (stage 4/5 of the pipeline)"""

import binarystring
from architecture import instructions, addressingmodes, registers
from csmtokens import TypedToken, tokentypes
from csmdefaults import defaults, symboltypes
from csmstructs import Memory, Operand, Scope, Symbol, Instruction, Register

class CodeGenerator:

    def __init__(self, global_scope: Scope, procedure_scopes: dict[str, Scope], 
                 config_table: dict[str, int]) -> None:
        """Constructor for a 'CodeGenerator' object"""
        
        self.__global_scope = global_scope
        self.__procedure_scopes = procedure_scopes
        self.__config_table: dict[str, int] = config_table

        # Only the values 0..n-1 need to be represented in binary
        self.__machine_operation_bits: int = binarystring.number_bits(instructions.NUMBER_INSTRUCTIONS - 1)
        self.__addressing_mode_bits: int = binarystring.number_bits(addressingmodes.NUMBER_MODES - 1)
        
        self.__number_registers: int = config_table[defaults.REGISTERS_CONFIG[0]] + registers.NUMBER_SPRS
        self.__number_memory_addresses: int = config_table[defaults.MEMORY_CONFIG[0]]

        self.__operand_bits: int = (binarystring.number_bits(self.__number_registers) if 
                                    self.__number_registers > self.__number_memory_addresses
                                    else binarystring.number_bits(self.__number_memory_addresses - 1)) + 1

        self.__offset: int = 0
        self.__index: int = 0

        # For caching purposes
        self.__total_bits: int = self.__machine_operation_bits + self.__addressing_mode_bits + 2*self.__operand_bits
        self.__number_gprs: int = self.__number_registers - registers.NUMBER_SPRS

    def __update_global_symbols(self) -> None:
        """update all global scope related symbols"""

        offset: int = self.__global_scope.number_instructions + self.__global_scope.number_variables

        for identifier, scope in self.__procedure_scopes.items():

            self.__global_scope.symbol_table[identifier].value = offset
            offset += scope.number_instructions + scope.number_variables

    def __resolve_operand(self, operand: Operand, scope: Scope) -> int:
        """Return the value an operand points to"""

        match operand.value.type:

            case tokentypes.LABEL:

                symbol: Symbol | None = scope.symbol_table.get(operand.value.value, None)

                if symbol is None:

                    # If the label is not in the local scope is is in the global scope
                    symbol = self.__global_scope.symbol_table[operand.value.value]
                
                return symbol.value

            case tokentypes.VALUE:

                return int(operand.value.value)

            case tokentypes.REGISTER:

                spr: Register | None = registers.get_spr(operand.value.value)

                if spr is None:

                    # GPR Zero cannot be accessible so the value must be wrapped between 1..n (inclusive)
                    return defaults.wrap_bounds(1, self.__number_gprs, int(operand.value.value)) * -1

                return (self.__number_gprs + spr.offset) * -1

    def __generate_machine_operation(self, instruction: Instruction, source_operand: Operand, destination_operand: Operand, 
                                     scope: Scope) -> str:
        """Generate the machine code (bits) that would represent a low level CPU instruction"""

        instruction_bits: str = binarystring.unsigned_int(instruction.opcode, self.__machine_operation_bits)


        addressing_mode_bits: str = binarystring.unsigned_int(
            #                                  An addressing mode will always be returned
            addressingmodes.get_addressing_mode(source_operand.addressing_mode.value).opcode, self.__addressing_mode_bits)
        
        source_operand_bits: str = binarystring.signed_int(self.__resolve_operand(source_operand, scope), self.__operand_bits)

        destination_operand_bits: str = binarystring.signed_int(self.__resolve_operand(destination_operand, scope), self.__operand_bits)

        return instruction_bits + addressing_mode_bits + source_operand_bits + destination_operand_bits
    
    def __update_local_symbols(self, scope: Scope, memory: Memory) -> None:
        """Update any local symbols and prematurely place any variables into the memory pool"""

        self.__offset += scope.number_instructions

        # Update the local symbols
        for symbol in scope.symbol_table.values():

            match symbol.type:

                case symboltypes.BRANCH:

                    # Update address to be relative to its position in memory instead of its position in the scope
                    symbol.value += self.__index

                case symboltypes.VARIABLE:

                    # Place variables at the end of the instructions
                    memory.insert_binary(self.__offset, binarystring.signed_int(int(symbol.value), self.__total_bits))
                    symbol.value = self.__offset
                    self.__offset += 1

    def __generate_code(self, scope: Scope, memory: Memory) -> None:
        """Generate the code and variables for a given scope"""

        self.__update_local_symbols(scope, memory)

        # Generate the machine code for each instruction
        for index, token in enumerate(scope.tokens):

            if token.type == tokentypes.INSTRUCTION:

                #                           An instruction will always be returned
                instruction: Instruction = instructions.get_instruction(token.value)

                default_operand: Operand = Operand(
                    TypedToken(tokentypes.ADDRESSING_MODE, addressingmodes.REGISTER.symbol, -1, -1),
                    TypedToken(tokentypes.VALUE, defaults.OPERAND_VALUE, -1, -1)
                )

                source_operand: Operand = Operand(scope.tokens[index+1], scope.tokens[index+2]) \
                                          if instruction.operands > 0 \
                                          else default_operand

                destination_operand: Operand = Operand(scope.tokens[index+4], scope.tokens[index+5]) \
                                               if instruction.operands > 1 \
                                               else default_operand

                memory.insert_binary(self.__index, self.__generate_machine_operation(instruction, source_operand, destination_operand, scope))
                self.__index += 1

        self.__index = self.__offset

    def run(self) -> tuple[Memory, int, int, int]:
        """run the CodeGenerator
           Will return the memory and the bits used by each part of the machine code"""

        self.__update_global_symbols()
        
        memory: Memory = Memory(self.__number_registers, self.__total_bits, self.__operand_bits)

        self.__generate_code(self.__global_scope, memory)

        for scope in self.__procedure_scopes.values():

            self.__generate_code(scope, memory)

        return (memory, self.__machine_operation_bits, self.__addressing_mode_bits, self.__operand_bits)

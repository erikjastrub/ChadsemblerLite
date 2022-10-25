"""Namespace for all data structures used throughout the system"""

from dataclasses import dataclass
import binarystring
from csmtokens import TypedToken

@dataclass(slots=True)
class Instruction:
    """
    mnemonic: The symbol that represents a machine code operation
    opcode: the integer value the mnemonic is encoded to
    operands: the number of values an instruction can operate on at most
    """

    mnemonic: str
    opcode: int
    operands: int

@dataclass(slots=True)
class Register:
    """
    register: the key symbol that represents a register
    variants: the other symbols that can be used to represent the register
    offset: a constant value used when determining the registers address
    """

    register: str
    variants: list[str]
    offset: int

@dataclass(slots=True)
class AddressingMode:
    """
    symbol: a character that represents the addressing mode
    variants: other symbols that can be used to represent the addressing mode
    opcode: the integer value the addressing mode is encoded to
    """

    symbol: str
    variants: list[str]
    opcode: int

@dataclass(slots=True)
class Symbol:
    """
    value: the memory address the symbol points to
    type: what type of data the symbol value is pointing to
    """

    value: int
    type: int

@dataclass(slots=True)
class Scope:
    """
    tokens: the lexemes that were generated for a particular scope
    symbol_table: a dictionary storing the local symbols of a scope
    number_instructions: the amount of instructions within the scope
    number_variables: the amount of variables within the scope
    """

    tokens: list[TypedToken]
    symbol_table: dict[str, Symbol]
    number_instructions: int
    number_variables: int

@dataclass(slots=True)
class Operand:
    """
    addressing_mode: how the operand value should be interpreted
    value: the value of the operand
    """

    addressing_mode: TypedToken
    value: TypedToken

class Memory:
    """Allows for a secure way to manipulate an abstract pool of memory"""

    def __init__(self, number_registers: int, architecture: int, operand_bits: int) -> None:
        """Constructor for a 'Memory' object"""

        self.__number_addresses: int = 2 ** (operand_bits - 1)
        self.__number_registers: int = number_registers
        
        self.__architecture: int = architecture

        default_value: str = '0'*architecture
        self.__memory_pool: list[str] = [default_value for _ in range( self.__number_registers + self.__number_addresses )]
        self.__memory_pool_length: int = len(self.__memory_pool)

    def __calculate_address(self, address: int) -> int:
        """Calculate the underlying address an abstract address corresponds to"""

        pointer: int = self.__number_registers + address

        if pointer > -1 and \
           pointer < self.__memory_pool_length:

            return pointer

        else:

            exit(f"Segmentation Fault: Attempted to access memory address {address}")

    def get(self, address: int) -> str:
        """Get the value at a given memory address"""

        return self.__memory_pool[self.__calculate_address(address)]

    def insert_binary(self, address: int, value: str) -> None:
        """Place a binary string into a given memory address"""

        self.__memory_pool[self.__calculate_address(address)] = value

    def insert_value(self, address: int, value: int) -> None:
        """Place a value (converted to a binary string) into a given memory address"""

        self.__memory_pool[self.__calculate_address(address)] = binarystring.signed_int(value, self.__architecture)

@dataclass(slots=True)
class MemoryValue:
    """
    address: the address in memory the value is located in
    bits: the binary string equivalent of the value
    value: the actual value
    """

    address: int
    bits: str
    value: int

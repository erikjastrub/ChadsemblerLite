"""Module containing the VirtualMachine (stage 5/5 of the pipeline)"""

from time import sleep
from architecture import addressingmodes, registers
import binarystring
from csmdefaults import defaults
from csmstructs import Memory, MemoryValue
from machineoperations import MachineOperations

class VirtualMachine:
    """Will execute the generated chadsembly code in a safe and secure environment"""

    def __init__(self, config_table: dict[str, int], memory: Memory, 
                 machine_operation_bits: int, addressing_mode_bits: int, operand_bits: int) -> None:
        """Constructor for a 'VirtualMachine' object"""

        self.__config_table: dict[str, int] = config_table
        self.__memory: Memory = memory
        self.__machine_operation_bits: int = machine_operation_bits
        self.__addressing_mode_bits: int = addressing_mode_bits
        self.__operand_bits: int = operand_bits

        self.__architecture: int = machine_operation_bits + addressing_mode_bits + (2 * operand_bits)

        self.__number_gprs: int = config_table[defaults.REGISTERS_CONFIG[0]]
        self.__clock_speed: float = config_table[defaults.CLOCK_CONFIG[0]] / 1000  # Convert to seconds for the sleep() function

        self.__program_counter_address: int = ( registers.PROGRAM_COUNTER.offset + self.__number_gprs ) * -1

        self.__machine_operations: MachineOperations = MachineOperations(memory, self.__architecture, self.__number_gprs)

    def __intro_prompt(self) -> str:
        """Generate the introduction prompt for the chadsembler which outlines the system and other useful information"""

        max_operand_value: int = ( 2 ** (self.__operand_bits - 1) ) - 1
        max_address_value: int = ( 2 ** (self.__architecture - 1) ) - 1
        number_addresses: int  = 2 ** (self.__operand_bits - 1)

        machine_code_format: str = f"{'0'*self.__machine_operation_bits} {'0'*self.__addressing_mode_bits} {'0'*self.__operand_bits} {'0'*self.__operand_bits}"

        return f"""\
Chadsembly Version `{defaults.CSM_VERSION}`
{self.__operand_bits} bit operand, {self.__architecture} bit address bus,
Instruction Format: {machine_code_format}
Values -{max_operand_value}..{max_operand_value} in an Operand, Values -{max_address_value}..{max_address_value} in an address
{number_addresses} (0..{number_addresses-1}) memory addresses, {self.__number_gprs} (1..{self.__number_gprs}) GPRs
"""

    def __resolve_operand(self, addressing_mode: str, operand: str) -> MemoryValue:
        """Return the address, bits and value an operand points to"""
        
        operand_value: int = binarystring.read_signed_int(operand)

        binary_at_operand: str = self.__memory.get(operand_value)
        value_at_operand: int = binarystring.read_signed_int(binary_at_operand)

        match binarystring.read_unsigned_int(addressing_mode):

            case addressingmodes.REGISTER.opcode | addressingmodes.DIRECT.opcode:

                return MemoryValue(
                    operand_value,
                    binary_at_operand,
                    value_at_operand
                )

            case addressingmodes.INDIRECT.opcode:

                binary_at_operand: str = self.__memory.get(value_at_operand)

                return MemoryValue(
                    value_at_operand,
                    binary_at_operand,
                    binarystring.read_signed_int(binary_at_operand)
                )

            case addressingmodes.IMMEDIATE.opcode:

                return MemoryValue(
                    operand_value,
                    binarystring.signed_int(operand_value, self.__architecture),
                    operand_value
                )

    def __handle_instruction(self, machine_code: str, program_counter: int) -> None:
        """Split an instruction into its subparts and execute it"""

        self.__memory.insert_binary(self.__program_counter_address, 
                          binarystring.unsigned_int(program_counter+1, self.__architecture))

        lower: int = 0
        upper: int = self.__machine_operation_bits

        machine_operation: str = machine_code[lower:upper]

        addressing_mode: str = machine_code[(lower := upper):(upper := upper + self.__addressing_mode_bits)]

        source_operand: str = machine_code[(lower := upper):(upper := upper + self.__operand_bits)]

        destination_operand: str = machine_code[(lower := upper):(upper := upper + self.__operand_bits)]

        self.__machine_operations.execute(binarystring.read_unsigned_int(machine_operation),
                                          self.__resolve_operand(addressing_mode, source_operand),

                                          # The opcode for register mode is 0 which is "0" in binary
                                          self.__resolve_operand("0", destination_operand))

    def run(self) -> None:
        """Run the VirtualMachine"""

        print(self.__intro_prompt())

        program_counter: int = 0

        while True:

            sleep(self.__clock_speed)
            
            self.__handle_instruction(self.__memory.get(program_counter), program_counter)

            program_counter: int = binarystring.read_unsigned_int(self.__memory.get(self.__program_counter_address))

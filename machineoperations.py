"""Module containing the MachineOperations class"""

from architecture import registers
from codegenerator import Memory
from csmstructs import MemoryValue
import binarystring

class MachineOperations:

    def __init__(self, memory: Memory, architecture: int, gprs: int) -> None:

        self.__memory: Memory = memory
        self.__architecture: int = architecture

        self.__program_counter_address: int = ( registers.PROGRAM_COUNTER.offset + gprs ) * -1
        self.__flags_register_address: int  = ( registers.FLAGS_REGISTER.offset  + gprs ) * -1
        self.__return_register_address: int = ( registers.RETURN_REGISTER.offset  + gprs ) * -1

    def HLT(self, source: MemoryValue, destination: MemoryValue) -> None:
        """0 Operands - Suspends the execution of the program"""

        exit(0)

    def ADD(self, source: MemoryValue, destination: MemoryValue) -> None:
        """ 2 Operands - Add the value in the source operand onto the value in the destination operand"""

        self.__memory.insert_value(destination.address, destination.value + source.value)

    def SUB(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Subtract the value in the source operand from the value in the destination operand"""

        self.__memory.insert_value(destination.address, destination.value - source.value)

    def STA(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Store the value in the destination operand into the source operand"""

        self.__memory.insert_binary(source.address, destination.bits)

    def NOP(self, source: MemoryValue, destination: MemoryValue) -> None:
        """0 Operands - Perform an empty operation, do nothing - wastes a clock cycle"""

        pass

    def LDA(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Load the value in the source operand onto the destination operand"""

        self.__memory.insert_binary(destination.address, source.bits)

    def BRA(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Always branch to the address in the source operand, regardless what value is in the destination operand"""

        self.__memory.insert_value(self.__program_counter_address, source.address)

    def BRZ(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Branch to the address in the source operand if the value in the destination operand == 0"""

        if destination.value == 0:

            self.__memory.insert_value(self.__program_counter_address, source.address)
    
    def BRP(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Branch to the address in the source operand if the value in the destination operand >= 0"""

        if destination.value > -1:

            self.__memory.insert_value(self.__program_counter_address, source.address)

    def INP(self, source: MemoryValue, destination: MemoryValue) -> None:
        """1 Operand - Get and store integer input in address in the source operand"""

        try:

            value: int = int(input(">>>"))

        except ValueError:

            exit("Runtime Error: Input could not be interpreted as an integer")

        self.__memory.insert_value(source.address, value)

    def OUT(self, source: MemoryValue, destination: MemoryValue) -> None:
        """1 Operand - Output the value in source the source operand"""

        # Flush the buffer to synchronise the output and ensure it is sequential
        print(source.value, flush=True)

    def OUTC(self, source: MemoryValue, destination: MemoryValue) -> None:
        """1 Operand - Output the value in the source operand encoded as a character"""

        # Flush the buffer to synchronise the output and ensure it is sequential
        print(chr(source.value), end='', flush=True)

    def OUTB(self, source: MemoryValue, destination: MemoryValue) -> None:
        """1 Operand - Output the bits in the source operand"""

        # Flush the buffer to synchronise the output and ensure it is sequential
        print(source.bits, flush=True)

    def AND(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise AND on the destination operand with a mask of the source operand"""

        self.__memory.insert_binary(destination.address, 
                                    binarystring.bitwise_and(source.bits, destination.bits))

    def OR(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise OR on the destination operand with a mask of the source operand"""

        self.__memory.insert_binary(destination.address, 
                                    binarystring.bitwise_or(source.bits, destination.bits))

    def NOT(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise NOT on the source operand with the result stored in the destination operand"""

        self.__memory.insert_binary(destination.address, 
                                    binarystring.bitwise_not(source.bits))

    def XOR(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise XOR on the destination operand with a mask of the source operand"""

        self.__memory.insert_binary(destination.address, 
                                    binarystring.bitwise_xor(source.bits, destination.bits))

    def LSL(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Logical Left Shift on the destination operand N times where N is the value in the source operand"""

        shift: tuple[str, str] | None = binarystring.logical_shift_left(destination.bits, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def LSR(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Logical Right Shift on the destination operand N times where N is the value in the source operand"""

        shift: tuple[str, str] | None = binarystring.logical_shift_right(destination.bits, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def ASL(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Arithmetic Left Shift on the destination operand N times where N is the value in the source operand"""

        shift: tuple[str, str] | None = binarystring.arithmetic_shift_left(destination.bits, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def ASR(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Arithmetic Right Shift on the destination operand N times where N is the value in the source operand"""

        shift: tuple[str, str] | None = binarystring.arithmetic_shift_right(destination.bits, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def CSL(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Circular Left Shift on the destination operand N times where N is the value in the source operand"""

        shift: str | None = binarystring.circular_shift_left(destination.bits, source.value)

        if shift:

            self.__memory.insert_binary(destination.address, shift)

    def CSR(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Circular Right Shift on the destination operand N times where N is the value in the source operand"""

        shift: str | None = binarystring.circular_shift_right(destination.bits, source.value)

        if shift:

            self.__memory.insert_binary(destination.address, shift)

    def CSLC(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Circular Left Shift with Carry on the destination operand N times where N is the value in the source operand"""

        # The last bit in the flags register is used as the carry bit flag
        carry_bit: str = self.__memory.get(self.__flags_register_address)[-1]

        shift: tuple[str, str] | None = \
            binarystring.circular_shift_left_carry(destination.bits, carry_bit, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def CSRC(self, source: MemoryValue, destination: MemoryValue) -> None:
        """2 Operands - Bitwise Circular Right Shift with Carry on the destination operand N times where N is the value in the source operand"""

        # The last bit in the flags register is used as the carry bit flag
        carry_bit: str = self.__memory.get(self.__flags_register_address)[-1]

        shift: tuple[str, str] | None = \
            binarystring.circular_shift_right_carry(destination.bits, carry_bit, source.value)

        if shift is not None:

            carry_bit, value = shift

            self.__memory.insert_binary(self.__flags_register_address,
                                        binarystring.pad_binary(carry_bit, self.__architecture-1, '0'))

            self.__memory.insert_binary(destination.address, value)

    def CALL(self, source: MemoryValue, destination: MemoryValue) -> None:
        """1 Operand - Invoke the address held in the source operand
           The RR is updated to store the current address"""

        # print("CALL source:", source)
        # print("CALL destination:", destination)
        self.__memory.insert_binary(self.__return_register_address, 
                                    self.__memory.get(self.__program_counter_address))

        self.__memory.insert_value(self.__program_counter_address,
                                   source.address)

    def RET(self, source: MemoryValue, destination: MemoryValue) -> None:
        """0 Operands - Returns from a procedure by setting the PC to the value in the RR"""

        self.__memory.insert_binary(self.__program_counter_address,
                                    self.__memory.get(self.__return_register_address))

    def execute(self, opcode: int, source: MemoryValue, destination: MemoryValue) -> None:
        """Will perform the operation associated with a given opcode and on the source and destination values"""

        # The index matches the opcode of the instruction
        machine_operations = [
            self.HLT,  self.ADD,  self.SUB,  self.STA,  self.NOP,
            self.LDA,  self.BRA,  self.BRZ,  self.BRP,  self.INP,
            self.OUT,  self.OUTC, self.OUTB, self.AND,  self.OR,
            self.NOT,  self.XOR,  self.LSL,  self.LSR,  self.ASL,
            self.ASR,  self.CSL,  self.CSR,  self.CSLC, self.CSRC,
            self.CALL, self.RET

        ]

        machine_operations[opcode](source, destination)

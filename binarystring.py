"""Namespace for all functionality to generate, read and manipulate binary strings"""

ENCODED_ZERO: int = ord('0')  # The value the char '0' maps to (in ASCII this value is 48)
TOGGLE: int = 1  # A constant that toggles 1 to 0 and 0 to 1 (Important when negating bits - NOT)

@staticmethod
def to_binary(value: int) -> str:
    """Generate a binary string for a given integer value with the minimum amount of bits needed to represent it"""

    return f"{value:b}"

@staticmethod
def number_bits(value: int) -> int:
    """Return the minimum amount of bits needed to represent an integer value"""

    # A constant holding the size (in bits) of the integer type
    BITS: int = 32

    # Iterate until the left most bit is found
    # The position of this bit from the left can be used to calculate the number of bits
    for i in range(BITS):

        if (value << i) & 0b10000000000000000000000000000000:

            return BITS - i

    return 0

@staticmethod
def pad_binary(binary_string: str, n: int, bit: str):
    """Left pad a binary string n times with the input bit"""

    return (bit * n) + binary_string

@staticmethod
def overflow(value: int, bits: int):
    """Performs 2s complement overflow wrapping in the range 0..(2**bits) on an integer value"""

    return value % (2**bits)

@staticmethod
def unsigned_int(value: int, bits: int):
    """Generate an unsigned binary string from a given integer value represented in the amount of bits specified"""

    # Minimum 1 bit should be present
    bits = max(bits, 1)

    binary_string: str = to_binary(overflow(value, bits))

    return pad_binary(binary_string, bits - len(binary_string), '0')

@staticmethod
def signed_int(value: int, bits: int):
    """Generate a signed binary string from a given integer value represented in the amount of bits specified"""

    # Minimum 2 bits should be present (1 for the sign bit and 1 for the actual value)
    bits = max(bits, 2)

    sign_bit: str = '0'

    if value < 0:

        sign_bit = '1'
        value *= -1
    
    binary_string = to_binary(overflow(value, bits-1))

    return sign_bit + pad_binary(binary_string, bits-len(binary_string)-1 , '0')

@staticmethod
def read_unsigned_int(binary_string: str) -> int:
    """Interpret an unsigned binary string as an integer"""

    return int(binary_string, 2)

@staticmethod
def read_signed_int(binary_string: str) -> int:
    """Interpret a signed binary string as an integer"""

    sign: int = 1 if binary_string.startswith("0") else -1
    
    return sign * int(binary_string[1:], 2)

# ====================== Shift Instructions

@staticmethod
def logical_shift_left(binary_string: str, n: int) -> tuple[str, str] | None:
    """Perform a logical left shift, n times"""

    length: int = len(binary_string)

    # Cannot perform a shift a negative amount of times
    # If n == 0 then the value is unchanged and no shifting should occur
    if n < 1:

        return None

    # A shift greater than the # bits will set the bits to all 0s
    elif n > length:

        return '0', '0' * length

    else:
        
        return binary_string[n-1], binary_string[n:] + '0' * n

@staticmethod
def logical_shift_right(binary_string: str, n: int) -> tuple[str, str] | None:
    """Perform a logical right shift, n times"""

    length: int = len(binary_string)

    # Cannot perform a shift a negative amount of times
    # If n == 0 then the value is unchanged and no shifting should occur
    if n < 1:

        return None

    # A shift greater than the # bits will set all bits to 0
    elif n > length:

        return '0', '0' * length

    else:
        
        return binary_string[length-n], '0' * n + binary_string[:length-n]

@staticmethod
def arithmetic_shift_left(binary_string: str, n: int) -> tuple[str, str] | None:
    """Perform an arithmetic left shift, n times"""

    # An arithmetic left shift is the same as a logical left shift
    return logical_shift_left(binary_string, n)

@staticmethod
def arithmetic_shift_right(binary_string: str, n: int) -> tuple[str, str] | None:
    """Perform an arithmetic right shift, n times"""

    length: int = len(binary_string)

    # Cannot perform a shift a negative amount of times
    # If n == 0 then the value is unchanged and no shifting should occur
    if n < 1:

        return None

    # A shift greater than the # bits will set all bits to the sign bit
    elif n > length:

        return binary_string[0], binary_string[0] * length

    else:
        
        return binary_string[length-n], binary_string[0] * n + binary_string[:length-n]  

@staticmethod
def circular_shift_left(binary_string: str, n: int) -> str | None:
    """Perform a circular left shift, n times"""

    # Cannot perform a shift a negative amount of times
    # If n == 0 then the value is unchanged and no shifting should occur
    if n < 1:

        return None

    # Calculate the minimum # of shifts that can output the correct result
    length: int = len(binary_string)
    n = n % length

    # If n == 0 then the value is unchanged and no shifting should occur
    if n == 0:

        return None

    return binary_string[n:] + binary_string[:n]

@staticmethod
def circular_shift_right(binary_string: str, n: int) -> str | None:
    """Perform a circular right shift, n times"""

    # Cannot perform a shift a negative amount of times
    # If n == 0 then the value is unchanged and no shifting should occur
    if n < 1:

        return None

    # Calculate the minimum # of shifts that can output the correct result
    length: int = len(binary_string)
    n = n % length

    # If n == 0 then the value is unchanged and no shifting should occur
    if n == 0:

        return None

    i: int = length - n
    return binary_string[i:] + binary_string[:i]

@staticmethod
def circular_shift_left_carry(binary_string: str, carry_bit: str, n: int) -> tuple[str, str] | None:
    """Perform a circular left shift with carry, n times"""

    bits: str | None = circular_shift_left(carry_bit + binary_string, n)

    if bits:

        return bits[0], bits[1:]

    else:
        
        return None

@staticmethod
def circular_shift_right_carry(binary_string: str, carry_bit: str, n: int) -> tuple[str, str] | None:
    """Perform a circular right shift with carry, n times"""

    bits: str | None = circular_shift_right(binary_string + carry_bit, n)

    if bits:

        return bits[-1], bits[:-1]

    else:
        
        return None

# ====================== Bitwise Manipulation Instructions
#   It is important bitwise manipulations can be applied on binary strings outright
#   No integer casting to apply the corresponding operation under the hood should occur
#   This is to avoid the overflow that can occur when attempting to parse a binary string
#       which has more bits than the system can store and interpret as an integer

@staticmethod
def bitwise_and(left: str, right: str) -> str:
    """Perform the bitwise AND operation on two binary strings"""

    bits: str = ""

    for l, r in zip(left, right):

        bits += str((ord(l) - ENCODED_ZERO) & (ord(r) - ENCODED_ZERO))

    return bits

@staticmethod
def bitwise_or(left: str, right: str) -> str:
    """Perform the bitwise OR operation on two binary strings"""

    bits: str = ""

    for l, r in zip(left, right):

        bits += str((ord(l) - ENCODED_ZERO) | (ord(r) - ENCODED_ZERO))

    return bits

@staticmethod
def bitwise_not(binary: str) -> str:
    """Perform the bitwise NOT operation on a binary string"""

    bits: str = ""

    for bit in binary:

        bits += str((ord(bit) - ENCODED_ZERO) ^ TOGGLE)

    return bits

@staticmethod
def bitwise_xor(left: str, right: str) -> str:
    """Perform the bitwise XOR operation on two binary strings"""

    bits: str = ""

    for l, r in zip(left, right):

        bits += str((ord(l) - ENCODED_ZERO) ^ (ord(r) - ENCODED_ZERO))

    return bits


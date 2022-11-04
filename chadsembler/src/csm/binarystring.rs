/// The value the char '0' maps to (in ASCII this value is 48)
const ENCODED_ZERO: u8 = '0' as u8;

/// A constant that toggles 1 to 0 and 0 to 1 (Important when negating bits - NOT)
const TOGGLE: u8 = 1;

/// Generate a binary string for a given integer value with the minimum amount of bits needed to represent it
pub fn to_binary(value: isize) -> String {

    // :b formatter returns the value as a binary string with no '0b' prefix
    format!("{value:b}")
}

/// Return the minimum amount of bits needed to represent an integer value
pub fn number_bits(value: usize) -> usize {

    const BITS: usize = isize::BITS as usize;
    const MASK: usize = 2usize.pow(usize::BITS-1);

    // Iterate until the left most bit is found
    // The position of this bit from the left can be used to calculate the number of bits
    for i in 0..BITS {

        if ((value << i) & MASK) > 0 {

            return BITS - i;
        }
    }

    0
}

/// Left pad a binary string n times with the input bit
pub fn pad_binary(binary_string: &str, n: isize, bit: &str) -> Option<String> {

    if n < 0 {

        None
    
    } else {

        Some(bit.repeat(n as usize) + binary_string)
    }
}

/// Performs 2s complement overflow wrapping in the range 0..(2**bits) on an integer value
pub fn overflow(value: isize, bits: u32) -> isize {

    // The rust % operator is the remainder operator
    // NOT the modulo operator
    // A formula using the remainder operator can imitate the results of the modulo operator

    let bits = 2isize.pow(bits);

    ((value % bits) + bits) % bits
}

/// Generate an unsigned binary string from a given integer value represented in the amount of bits specified
pub fn unsigned_int(value: isize, mut bits: isize) -> String { 

    // Minimum 1 bit should be present
    bits = std::cmp::max(bits, 1);
    
    let binary_string = to_binary(overflow(value, bits as u32));

    if let Some(s) = pad_binary(&binary_string, bits - binary_string.len() as isize, "0") {

        s
    
    } else {

        binary_string
    }
}

/// Generate a signed binary string from a given integer value represented in the amount of bits specified
pub fn signed_int(mut value: isize, mut bits: isize) -> String { 

    // Minimum 2 bits should be present (1 for the sign bit and 1 for the actual value)
    bits = std::cmp::max(bits, 2);

    let mut sign_bit: &str = "0";

    if value < 0 {

        sign_bit = "1";
        value *= -1;

    }
    
    let binary_string = to_binary(overflow(value, bits as u32 - 1));

    if let Some(s) = pad_binary(&binary_string, bits - binary_string.len() as isize - 1, "0") {

        sign_bit.to_owned() + &s
    
    } else {
        
        sign_bit.to_owned() + &binary_string
    }
}

/// Interpret an unsigned binary string as an integer
pub fn read_unsigned_int(binary_string: &str) -> Result<isize, std::num::ParseIntError> {

    isize::from_str_radix(&binary_string, 2)
}

/// Interpret a signed binary string as an integer
pub fn read_signed_int(binary_string: &str) -> Result<isize, std::num::ParseIntError> {

    let sign = if binary_string.starts_with("0") { 1 } else { -1 };

    let value = isize::from_str_radix(&binary_string[1..], 2)?;

    Ok(sign * value)
}

// ====================== Bitwise Shift Instructions

/// Perform a logical left shift, n times
pub fn logical_shift_left(binary_string: &str, n: isize) -> Option<(char, String)> {

    let length = binary_string.len();

    // Cannot perform a shift a negative amount of times
    // If n == 0 then the value is unchanged and no shifting should occur
    if n < 1 {

        return None;
    }
    
    let n = n as usize;

    // A shift greater than the # bits will set the bits to all 0s
    if n > length {
        
        Some( ('0', "0".repeat(length)) )

    } else {

        Some( (binary_string.as_bytes()[n-1] as char, binary_string[n..].to_owned() + &"0".repeat(n)) )
    }
}

/// Perform a logical right shift, n times
pub fn logical_shift_right(binary_string: &str, n: isize) -> Option<(char, String)> {

    let length = binary_string.len();

    // Cannot perform a shift a negative amount of times
    // If n == 0 then the value is unchanged and no shifting should occur
    if n < 1 {

        return None;
    }

    let n = n as usize;

    // A shift greater than the # bits will set the bits to all 0s
    if n > length {
        
        Some( ('0', "0".repeat(length)) )

    } else {

        Some( (binary_string.as_bytes()[length-n] as char, "0".repeat(n) + &binary_string[..length-n].to_owned()) )
    }
}

/// Perform an arithmetic left shift, n times
pub fn arithmetic_shift_left(binary_string: &str, n: isize) -> Option<(char, String)> {

    // An arithmetic left shift is the same as a logical left shift
    logical_shift_left(binary_string, n)
}

/// Perform an arithmetic right shift, n times
pub fn arithmetic_shift_right(binary_string: &str, n: isize) -> Option<(char, String)> {

    let length = binary_string.len();

    // Cannot perform a shift a negative amount of times
    // If n == 0 then the value is unchanged and no shifting should occur
    if n < 1 {

        return None;
    }
    
    let n = n as usize;

    // A shift greater than the # bits will set all bits to the sign bit
    if n > length {
        
        Some( (binary_string.as_bytes()[0] as char, binary_string[0..1].repeat(length)) )

    } else {

        Some( (binary_string.as_bytes()[length-n] as char, binary_string[0..1].repeat(n) + &binary_string[..length-n]) )
    }
}

/// Perform a circular left shift, n times
pub fn circular_shift_left(binary_string: &str, n: isize) -> Option<String> {

    // Cannot perform a shift a negative amount of times
    // If n == 0 then the value is unchanged and no shifting should occur
    if n < 1 {

        return None;
    }

    let mut n = n as usize;

    // Calculate the minimum # of shifts that can output the correct result
    let length = binary_string.len();
    n %= length;

    // If n == 0 then the value is unchanged and no shifting should occur
    if n == 0 {

        None

    } else {

        Some(binary_string[n..].to_owned() + &binary_string[..n])
    }
}

/// Perform a circular right shift, n times
pub fn circular_shift_right(binary_string: &str, n: isize) -> Option<String>{

    // Cannot perform a shift a negative amount of times
    // If n == 0 then the value is unchanged and no shifting should occur
    if n < 1 {

        return None;
    }

    let mut n = n as usize;

    // Calculate the minimum # of shifts that can output the correct result
    let length = binary_string.len();
    n %= length;

    // If n == 0 then the value is unchanged and no shifting should occur
    if n == 0 {

        None

    } else {

        let i = length - n;
        Some(binary_string[i..].to_owned() + &binary_string[..i])
    }
}

/// Perform a circular left shift with carry, n times
pub fn circular_shift_left_carry(binary_string: &str, carry_bit: &str, n: isize) -> Option<(char, String)> {

    let bits = circular_shift_left(&(carry_bit.to_owned() + binary_string), n)?;

    Some( (bits.as_bytes()[0] as char, bits[1..].to_owned()) )
}

/// Perform a circular right shift with carry, n times
pub fn circular_shift_right_carry(binary_string: &str, carry_bit: &str, n: isize) -> Option<(char, String)> {

    let bits = circular_shift_left(&(binary_string.to_owned() + carry_bit), n)?;

    let i = bits.len() - 1;
    Some( (bits.as_bytes()[i] as char, bits[..i].to_owned()) )
}

// ====================== Bitwise Manipulation Instructions
//   It is important bitwise manipulations can be applied on binary strings outright
//   No integer casting to apply the corresponding operation under the hood should occur
//   This is to avoid the overflow that can occur when attempting to parse a binary string
//       which has more bits than the system can store and interpret as an integer

/// Perform the bitwise AND operation on two binary strings
pub fn bitwise_and(left: &str, right: &str) -> String {

    let mut bits = String::new();

    for (l, r) in std::iter::zip(left.chars(), right.chars()) {

        bits += &((l as u8 - ENCODED_ZERO) & (r as u8 - ENCODED_ZERO)).to_string();
    }

    bits
}

/// Perform the bitwise OR operation on two binary strings
pub fn bitwise_or(left: &str, right: &str) -> String {

    let mut bits = String::new();

    for (l, r) in std::iter::zip(left.chars(), right.chars()) {

        bits += &((l as u8 - ENCODED_ZERO) | (r as u8 - ENCODED_ZERO)).to_string();
    }

    bits
}

/// Perform the bitwise NOT operation on a binary string
pub fn bitwise_not(binary: &str) -> String {

    let mut bits = String::new();

    for bit in binary.chars() {

        bits += &((bit as u8 - ENCODED_ZERO) ^ TOGGLE).to_string();
    }

    bits
}

/// Perform the bitwise XOR operation on two binary strings
pub fn bitwise_xor(left: &str, right: &str) -> String {

    let mut bits = String::new();

    for (l, r) in std::iter::zip(left.chars(), right.chars()) {

        bits += &((l as u8 - ENCODED_ZERO) ^ (r as u8 - ENCODED_ZERO)).to_string();
    }

    bits
}

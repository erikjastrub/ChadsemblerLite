use std::io::{BufReader, BufRead};
use std::fs::{File, metadata};
use std::process::exit;
use std::collections::HashMap;
use std::env::args;

mod csm;
mod pipeline;

use pipeline::{precompilation, lexer, parser, instructionpools, semanticanalyser, codegenerator, virtualmachine};

use csm::defaults::sysdefaults;
use crate::csm::architecture::{registers, addressingmodes};
use crate::csm::defaults::lexerdefaults;
use crate::csm::tokens::{TokenTypes, TypedToken};

/// Read a file into a string
/// Will read the file using a Universal New Line Sequence
/// In this case it is a singular '\n'
fn read_file(path: &str) -> String {

    if let Ok(file) = File::open(path) {

        let file = BufReader::new(file);

        let metadata = match metadata(path) {

            Ok(md) => md,
            Err(_) => {

                eprintln!("Failed to get metadata for file");
                exit(sysdefaults::EXIT_CODE)
            }
        };

        // Preallocate capacity to avoid reallocating to make the string bigger
        let mut buffer = String::with_capacity(metadata.len() as usize);

        for line in file.lines() {

            buffer += &line.unwrap();
            buffer += "\n";
        }

        // Possible that the string may have been preallocated with a bigger size
        // Remove unnecessary bytes
        buffer.shrink_to_fit();

        buffer
    
    } else {

        eprintln!("Cannot assemble a file that does not exist");
        exit(sysdefaults::EXIT_CODE);
    }
}

fn get_source_code(argv: &Vec<String>) -> String {

    let path = match argv.get(1) {

        Some(p) => p,
        None => {

            eprintln!("No file was passed in to be assembled");
            exit(sysdefaults::EXIT_CODE);
        }
    };

    if !path.ends_with(sysdefaults::CSM_EXTENSION) {

        eprintln!("Chadsembly Warning: File name does not end with a `.csm` file extension");
    }

    read_file(path)
}

fn main() {

    let mut config_table = HashMap::new();
    config_table.insert(sysdefaults::MEMORY_CONFIG.0.to_owned(),    sysdefaults::MEMORY_CONFIG.1);  // defaults::MEMORY_CONFIG.1
    config_table.insert(sysdefaults::REGISTERS_CONFIG.0.to_owned(), sysdefaults::REGISTERS_CONFIG.1);
    config_table.insert(sysdefaults::CLOCK_CONFIG.0.to_owned(),     sysdefaults::CLOCK_CONFIG.1);

    let arguments: Vec<String> = args().collect();

    let source_code = get_source_code(&arguments);

    precompilation::argumentprocessor::run(
        &arguments[2..], 
        sysdefaults::DIRECTIVE_PREFIX, 
        sysdefaults::DELIMITER, 
        &mut config_table
    );

    precompilation::preprocessor::run(
        &source_code,
        sysdefaults::DIRECTIVE_PREFIX, 
        sysdefaults::COMMENT_PREFIX,
        sysdefaults::DELIMITER, 
        &mut config_table
    );

    let tokens = lexer::run(
        &source_code,
        sysdefaults::DIRECTIVE_PREFIX,
        sysdefaults::COMMENT_PREFIX,
    );

    parser::run(&tokens);

    let (mut global_scope, mut procedure_scopes) = instructionpools::run(&tokens);

    let default_acc = TypedToken { token_type: TokenTypes::Register, token_value: registers::ACCUMULATOR.register.to_owned(), row: 0, column: 0 };
    let default_register = TypedToken { token_type: TokenTypes::AddressingMode, token_value: addressingmodes::REGISTER.symbol.to_owned(), row: 0, column: 0 };
    let default_direct = TypedToken { token_type: TokenTypes::AddressingMode, token_value: addressingmodes::DIRECT.symbol.to_owned(), row: 0, column: 0 };
    let default_separator = TypedToken { token_type: TokenTypes::Separator, token_value: lexerdefaults::SEPARATOR.to_string(), row: 0, column: 0 };

    let default_operands = (&default_acc, &default_register, &default_direct, &default_separator);

    semanticanalyser::run(&mut global_scope, &mut procedure_scopes, &default_operands);    

    let (mut memory, machine_operation_bits, addressing_mode_bits, operand_bits) = codegenerator::run(&mut global_scope, &mut procedure_scopes, &config_table);


    let bits = (machine_operation_bits, addressing_mode_bits, operand_bits, machine_operation_bits+addressing_mode_bits+2*operand_bits);

    virtualmachine::run(&config_table, &mut memory, &bits);
}

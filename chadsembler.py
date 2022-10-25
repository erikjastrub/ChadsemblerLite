"""The main file to be execute - The Chadsembler"""
import sys, pathlib

# Inserts the path of the 'imports' directory to python path
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}\\imports")


from csmtokens import TypedToken
from precompilation import ArgumentProcessor, Preprocessor
from lexer import Lexer
from parser import Parser
from instructionpools import InstructionPools
from semanticanalayser import SemanticAnalyser
from codegenerator import CodeGenerator
from virtualmachine import VirtualMachine

from sys import argv
from csmdefaults import defaults

def get_source_code(argv: list[str], argc: int) -> str:
    """Convenience function, responsible for handling the the source code file"""

    # argv[0] is the file name

    if argc == 1:

        exit("No file was passed in to be assembled")

    if not argv[1].endswith(defaults.CSM_EXTENSION):

        print("Chadsembly Warning: File name does not end with a `.csm` file extension")

    try:

        with open(argv[1]) as file:

            return file.read()

    except FileNotFoundError:

        exit("Cannot assemble a file that does not exist")       

def main(argv: list[str], argc: int) -> int:
    """The main function"""

    config_table: dict[str, int] = {
        defaults.REGISTERS_CONFIG[0]: defaults.REGISTERS_CONFIG[1],
        defaults.MEMORY_CONFIG[0]: defaults.MEMORY_CONFIG[1],
        defaults.CLOCK_CONFIG[0]: defaults.CLOCK_CONFIG[1],
    }
    
    source_code: str = get_source_code(argv, argc)

    # Argument Processing - Pre-compilation
    ap: ArgumentProcessor = ArgumentProcessor(
        argv[2:], defaults.DIRECTIVE_PREFIX,
        defaults.DELIMITER, config_table
    )
    ap.run()

    # Preprocessing - Precompilation
    pp: Preprocessor = Preprocessor(
        source_code,
        defaults.DIRECTIVE_PREFIX, 
        defaults.COMMENT_PREFIX, 
        defaults.DELIMITER, config_table
    )
    pp.run()

    # Lexer - 1/5
    lexer: Lexer = Lexer(
        source_code,
        defaults.DIRECTIVE_PREFIX,
        defaults.COMMENT_PREFIX
    )
    tokens: list[TypedToken] = lexer.run()

    # Parser - 2/5
    parser: Parser = Parser(
        tokens
    )
    parser.run()

    # Instruction Pools - 2.5/5
    ip: InstructionPools = InstructionPools(
        tokens
    )
    global_scope, procedure_scopes = ip.run()

    # Semantic Analysis - 3/5
    sa: SemanticAnalyser = SemanticAnalyser(
        global_scope, procedure_scopes
    )
    sa.run()

    # Code Generation - 4/5
    cg: CodeGenerator = CodeGenerator(
        global_scope, 
        procedure_scopes, 
        config_table
    )

    # Virtual Machine - 5/5
    vm: VirtualMachine = VirtualMachine(
        config_table, 
        *cg.run()
    )
    vm.run()

    return 0;

if __name__ == "__main__":
    
    exit ( main(argv, len(argv)) )
    
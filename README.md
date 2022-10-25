# Empty:

When translating the main branch into another language, this branch should be used as the template to provide an empty branch to begin working from

The README.md of any branch should outline how to run the code in the branch as well as any other information to do with the branch


Recommended ordering of modules to implement:
(shows the module and its dependencies)

- chadsembler (implement as you go along)
- csmdefaults
- csmerrors
- csmtokens <- csmdefaults
- binarystring
- csmstructs <- binarystring, csmtokens
- architecture <- csmstructs
- precompilation <- csmtokens, csmdefaults, csmerrors
- lexer <- csmerrors, csmtokens, csmdefaults, architecture
- parser <- csmtokens
- instructionpools <- csmerrors, csmtokens, csmdefaults, csmstructs
- semanticanalyser <- architecture, csmdefaults, csmtokens, csmerrors, csmstructs
- codegenerator <- binarystring, architecture, csmtokens, csmdefaults, csmstructs
- machineoperations <- architecutre, csmstructs, binarystring
- virtualmachine <- architecture, binarystring, csmdefaults, csmstructs, machineoperations

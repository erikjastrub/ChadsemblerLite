# Lightweight Chadsembler - Python Optimised

This is the Python branch for the Chadsembler.

The original branch is focused on being language agnostic and so it is written in readable, minimal python so as to not use any language specific features which may make it harder to translate into another language.

This branch is the Python branch and will be optimised using pythonic features and optimisations.

Key Optimisations:

- Got rid of the "tokenutils" class previosuly located in the "csmtokens.py" file
- Use of inheritance between the ArgumentProcessor and Preprocessor
- Various small syntax sugar optimisations
- Use of dictionaries for O(1) access of architectural info

How to Run:

Download the Python Branch and run the 'chadsembly.py' file with the source code file you want to execute!

E.g: 'py ./chadsembly.py ./code.csm'

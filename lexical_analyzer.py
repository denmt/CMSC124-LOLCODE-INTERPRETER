import re

# Define token specifications as regex patterns
TOKENS = [
    ("COMMENT", r"BTW .+"),  # Line comment
    ("MULTILINE_COMMENT_START", r"OBTW"),  # Multiline comment start
    ("MULTILINE_COMMENT_END", r"TLDR"),  # Multiline comment end
    ("CODE_DELIMITER", r"(HAI|KTHXBYE)"),  # Program Start/End
    ("VARIABLE_DECLARATION", r"I HAS A"),  # Variable declaration keyword
    ("VARIABLE_ASSIGNMENT", r"ITZ"),  # ITZ keyword for variable initialization
    ("OUTPUT_KEYWORD", r"VISIBLE"),  # Output keyword
    ("INPUT_KEYWORD", r"GIMMEH"),  # Input
    ("DECLARATION_START", r"WAZZUP"),  # Variable declaration section start
    ("DECLARATION_END", r"BUHBYE"),  # Variable declaration section end
    ("EXPR_SUM", r"SUM OF"),  # Sum operation
    ("EXPR_DIFF", r"DIFF OF"),  # Difference operation
    ("EXPR_PRODUKT", r"PRODUKT OF"),  # Product operation
    ("EXPR_QUOSHUNT", r"QUOSHUNT OF"),  # Division operation
    ("EXPR_MOD", r"MOD OF"),  # Modulo operation
    ("EXPR_BIGGR", r"BIGGR OF"),  # Max operation
    ("EXPR_SMALLR", r"SMALLR OF"),  # Min operation
    ("CONCAT", r"SMOOSH"),  # String concatenation
    ("BOOL_AND", r"BOTH OF"),  # Logical AND
    ("BOOL_OR", r"EITHER OF"),  # Logical OR
    ("BOOL_XOR", r"WON OF"),  # Logical XOR
    ("BOOL_NOT", r"NOT"),  # Logical NOT
    ("BOOL_ALL_OF", r"ALL OF"),  # Infinite arity AND
    ("BOOL_ANY_OF", r"ANY OF"),  # Infinite arity OR
    ("CLOSING_KEYWORD", r"MKAY"),  # Closing keyword
    ("COMPARE_EQUALS", r"BOTH SAEM"),  # Comparison equal
    ("COMPARE_DIFF", r"DIFFRINT"),  # Comparison not equal
    ("TYPECAST_OPERATOR", r"(MAEK|IS NOW A)"),  # Typecast
    ("IF_START", r"O RLY\?"),  # If statement start
    ("IF_YES", r"YA RLY"),  # If true clause
    ("IF_NO", r"NO WAI"),  # If false clause
    ("CONDITIONAL_END", r"OIC"),  # If statement end
    ("SWITCH_START", r"WTF\?"),  # Switch-case start
    ("SWITCH_CASE", r"OMG "),  # Switch-case case
    ("SWITCH_DEFAULT", r"OMGWTF"),  # Switch-case default
    ("BREAK", r"GTFO"),  # Break statement
    ("LOOP_START", r"IM IN YR"),  # Loop start
    ("LOOP_END", r"IM OUTTA YR"),  # Loop end
    ("LOOP_OPERATION", r"(UPPIN|NERFIN)"),  # Loop operation
    ("LOOP_IDENTIFIER", r"((?<=IM IN YR)|(?<=IM OUTTA YR)) \w+"),  # Loop label
    ("LOOP_CONDITION", r"(TIL|WILE)"),  # Loop condition
    ("FUNCTION_DEF", r"HOW IZ I"),  # Function definition
    ("FUNCTION_END", r"IF U SAY SO"),  # Function end
    ("FUNCTION_CALL", r"I IZ"),  # Function call
    ("FUNCTION_IDENTIFIER", r"((?<=HOW IZ I)|(?<=I IZ)) \w+"),  # Function name
    ("RETURN", r"FOUND YR"),  # Return statement
    ("TROOF_LITERAL", r"(WIN|FAIL)"),  # Boolean values
    ("YARN_LITERAL", r'"([^"]*)"'),  # String literal, including content inside quotes
    ("NUMBAR_LITERAL", r"-?\b(\d+\.\d+|\.\d+)\b"),  # Number literal with decimals
    ("NUMBR_LITERAL", r"\-?\b\d+\b"),  # Number literal
    ("TYPE_LITERAL", r"(NOOB|TROOF|NUMBAR|NUMBR|YARN)"),  # Type literal
    ("OPERATOR_SEPARATOR", r"AN"),  # Operator separator
    ("DELIMITER", r"YR"),  # Delimiter
    ("ASSIGNMENT", r"R"),  # Variable assignment
    ("TYPE_ASSIGNMENT", r"A"),  # Type assignment
    ("PRINT_CAT", r"\+"),  # Print concatenation
    ("VARIABLE_IDENTIFIER", r"\b\w+\b"),  # Variable identifier
    ("WHITESPACE", r"[ \t]+"),  # Ignore whitespace
    ("NEWLINE", r"\n"),  # Newline for end of statement
]

# Compile token regex patterns into a master regex pattern
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKENS)
token_compiler = re.compile(token_regex)

# Tokenizer function
def tokenize(code):
    tokens = []
    multiline_comment = False

    for match in token_compiler.finditer(code):
        kind = match.lastgroup
        value = match.group(kind)

        # Handle multiline comments
        if kind == "MULTILINE_COMMENT_START":
            multiline_comment = True
        elif kind == "MULTILINE_COMMENT_END":
            multiline_comment = False
        elif multiline_comment:
            continue  # Ignore everything inside multiline comments
        elif kind == "COMMENT":
            continue  # Ignore single-line comments
        elif kind == "WHITESPACE":
            continue  # Ignore whitespace
        elif kind == "NEWLINE":
            continue  # Newlines just separate statements
        else:
            tokens.append((kind, value))  # Add as a tuple

    return tokens


def lexical_analyzer(program_code):
    tokens = []
    for line in program_code:
        tokens.extend(tokenize(line))

    return tokens

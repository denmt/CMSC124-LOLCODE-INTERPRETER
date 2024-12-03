import lexical_analyzer

class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0

    def get_current_token(self):
        """Returns the current token."""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def consume(self):
        """Consume the current token and move to the next one."""
        self.current_index += 1

    def match(self, token_type):
        """Match the current token with a specific type."""
        current_token = self.get_current_token()
        if current_token and current_token[0] == token_type:
            self.consume()
            return True
        return False

    def parse(self):
        """Start parsing the program."""
        if not self.parse_program():
            return False
        if self.get_current_token() is None:  # No tokens left, valid program
            return True
        return False

    def parse_program(self):
        """Parse the full program, starting with HAI and ending with KTHXBYE."""
        if not self.match("CODE_DELIMITER"):  # Expecting 'HAI'
            print("Error: Expected 'HAI' at the beginning.")
            return False

        # Check for the WAZZUP section (variable declarations)
        if not self.parse_wazzup():
            return False

        # Check for statements (operations, outputs, etc.)
        if not self.parse_statements():
            return False

        # Ending KTHXBYE
        if not self.match("CODE_DELIMITER"):  # Expecting 'KTHXBYE'
            print("Error: Expected 'KTHXBYE' at the end.")
            return False

        return True

    def parse_wazzup(self):
        """Parse the WAZZUP block for variable declarations."""
        if not self.match("DECLARATION_START"):  # Expecting 'WAZZUP'
            return True  # If there's no WAZZUP, it's valid to skip (i.e., no variables)

        while True:
            if self.match("DECLARATION_END"):  # Expecting 'BUHBYE' to end WAZZUP block
                return True

            if not self.match("VARIABLE_DECLARATION"):  # Expecting 'I HAS A'
                print("Error: Expected 'I HAS A' for variable declaration.")
                return False

            # We expect the variable name next
            if not self.match("VARIABLE_IDENTIFIER"):
                print("Error: Expected a variable identifier.")
                return False

            # Check if there’s an initialization
            if self.match("VARIABLE_ASSIGNMENT"):  # 'ITZ'
                if not self.parse_expression():
                    return False

        return True

    def parse_statements(self):
        """Parse various statements in the program."""
        while self.get_current_token():
            token_type = self.get_current_token()[0]
            
            # If we encounter a CODE_DELIMITER, we should only allow it at the end
            if token_type == "CODE_DELIMITER":
                # We should only allow CODE_DELIMITER at the end (i.e., after 'KTHXBYE')
                if self.get_current_token()[1] == 'KTHXBYE':
                    return True
                self.consume()
                continue

            if token_type == "COMMENT" or token_type == "MULTILINE_COMMENT_START":
                # Ignore comments, we don't need to process them
                self.consume()
                continue

            if token_type == "OUTPUT_KEYWORD":  # Expecting VISIBLE
                if not self.parse_output_statement():
                    return False

            elif token_type == "INPUT_KEYWORD":  # Expecting GIMMEH
                if not self.parse_input_statement():
                    return False

            elif token_type == "EXPR_SUM" or token_type == "EXPR_DIFF" or token_type == "EXPR_PRODUKT":
                # Handle arithmetic operations like SUM OF, DIFF OF
                if not self.parse_expression():
                    return False

            elif token_type == "IF_START":  # Expecting O RLY?
                if not self.parse_if_statement():
                    return False

            elif token_type == "LOOP_START":  # Expecting IM IN YR
                if not self.parse_loop_statement():
                    return False

            elif token_type == "FUNCTION_DEF":  # Expecting HOW IZ I
                if not self.parse_function_definition():
                    return False

            else:
                print(f"Error: Unexpected token {token_type}")
                return False

        return True

    def parse_output_statement(self):
        """Parse VISIBLE statement."""
        if not self.match("OUTPUT_KEYWORD"):
            print("Error: Expected 'VISIBLE'.")
            return False
        while self.get_current_token() and self.get_current_token()[0] not in ["NEWLINE", "CODE_DELIMITER"]:
            self.consume()  # Consume the arguments of VISIBLE
        return True

    def parse_input_statement(self):
        """Parse GIMMEH statement."""
        if not self.match("INPUT_KEYWORD"):
            print("Error: Expected 'GIMMEH'.")
            return False
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable for GIMMEH.")
            return False
        return True

    def parse_expression(self):
        """Parse a basic expression like NUMBR, SUM OF, etc."""
        # First, check if it's a complex operation like SUM OF, DIFF OF, etc.
        if self.match("EXPR_SUM") or self.match("EXPR_DIFF") or self.match("EXPR_PRODUKT") or self.match("EXPR_QUOSHUNT"):
            if not self.parse_operand():
                return False

            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False

            if not self.parse_operand():
                return False

        else:
            # If it's not an operator-based expression, we consider literals and variables
            if not self.parse_operand():
                return False

        return True

    def parse_operand(self):
        """Parse operands in an expression (NUMBR, NUMBAR, YARN, etc.)."""
        token_type = self.get_current_token()[0]

        if token_type == "NUMBR_LITERAL":  # Handle integer literals
            self.consume()
            return True

        elif token_type == "NUMBAR_LITERAL":  # Handle float literals
            self.consume()
            return True

        elif token_type == "YARN_LITERAL":  # Handle string literals
            # Consume the YARN_LITERAL (string literal), which includes the string content and quotes
            self.consume()  # Now we consume the YARN_LITERAL token itself (including the quotes)
            return True

        elif token_type == "TROOF_LITERAL":  # Handle boolean literals (WIN/FAIL)
            self.consume()
            return True

        elif token_type == "VARIABLE_IDENTIFIER":  # Handle variables
            self.consume()
            return True

        elif token_type == "EXPR_SUM" or token_type == "EXPR_DIFF" or token_type == "EXPR_PRODUKT" or token_type == "EXPR_QUOSHUNT":
            # Handle nested expressions
            return self.parse_expression()

        else:
            print(f"Error: Expected valid operand, but found {token_type}.")
            return False




    def parse_if_statement(self):
        """Parse IF-THEN statement."""
        if not self.match("IF_START"):
            return False
        if not self.match("IF_YES"):  # YA RLY
            print("Error: Expected 'YA RLY'.")
            return False
        if not self.parse_statements():  # Handle if body
            return False
        if not self.match("IF_NO"):  # NO WAI
            return False
        if not self.parse_statements():  # Handle else body
            return False
        if not self.match("CONDITIONAL_END"):  # OIC
            return False
        return True

    def parse_loop_statement(self):
        """Parse loop statement."""
        if not self.match("LOOP_START"):
            print("Error: Expected 'IM IN YR'.")
            return False
        if not self.match("LOOP_OPERATION"):  # UPPIN or NERFIN
            print("Error: Expected 'UPPIN' or 'NERFIN'.")
            return False
        if not self.match("VARIABLE_IDENTIFIER"):  # Loop variable
            print("Error: Expected loop variable.")
            return False
        if not self.match("LOOP_CONDITION"):  # TIL or WILE
            print("Error: Expected 'TIL' or 'WILE'.")
            return False
        if not self.parse_expression():  # Loop condition
            return False
        if not self.match("LOOP_END"):  # IM OUTTA YR
            print("Error: Expected 'IM OUTTA YR'.")
            return False
        return True

    def parse_function_definition(self):
        """Parse function definition."""
        if not self.match("FUNCTION_DEF"):
            print("Error: Expected 'HOW IZ I'.")
            return False
        if not self.match("FUNCTION_IDENTIFIER"):  # Function name
            print("Error: Expected function name.")
            return False
        if not self.match("FUNCTION_END"):  # IF U SAY SO
            print("Error: Expected 'IF U SAY SO'.")
            return False
        return True

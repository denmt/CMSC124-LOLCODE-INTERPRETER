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
            print(f"Matched token: {current_token}")
            self.consume()
            return True
        return False

    def parse(self):
        """Start parsing the program."""
        if not self.parse_program():
            return False
        if self.get_current_token() is None:  # No tokens left, valid program
            return True
        print("Error: Unexpected tokens after program end.")
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
            return True  # Valid to skip if there's no WAZZUP

        while not self.match("DECLARATION_END"):  # Expecting 'BUHBYE'
            if not self.match("VARIABLE_DECLARATION"):  # Expecting 'I HAS A'
                print("Error: Expected 'I HAS A' for variable declaration.")
                return False

            if not self.match("VARIABLE_IDENTIFIER"):  # Expecting variable name
                print("Error: Expected a variable identifier.")
                return False

            if self.match("VARIABLE_ASSIGNMENT"):  # Expecting 'ITZ'
                if not self.parse_expression():
                    return False

        return True

    def parse_statements(self):
        """Parse various statements in the program."""
        while self.get_current_token():
            token_type = self.get_current_token()[0]

            if token_type == "CODE_DELIMITER" and self.get_current_token()[1] == "KTHXBYE":
                return True  # Valid end of program

            if token_type in ["COMMENT", "MULTILINE_COMMENT_START"]:
                self.consume()  # Ignore comments
                continue

            if token_type == "OUTPUT_KEYWORD":
                if not self.parse_output_statement():
                    return False

            elif token_type == "INPUT_KEYWORD":
                if not self.parse_input_statement():
                    return False

            elif token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT"]:
                if not self.parse_expression():
                    return False

            elif token_type == "IF_START":
                if not self.parse_if_statement():
                    return False

            elif token_type == "LOOP_START":
                if not self.parse_loop_statement():
                    return False

            elif token_type == "FUNCTION_DEF":
                if not self.parse_function_definition():
                    return False
            
            elif token_type == "FUNCTION_CALL":
                if not self.parse_function_call():
                    return False

            else:
                print(f"Error: Unexpected token '{token_type}'.")
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
        if self.match("EXPR_SUM") or self.match("EXPR_DIFF") or self.match("EXPR_PRODUKT") or self.match("EXPR_QUOSHUNT"):
            if not self.parse_operand():
                return False
            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False
            if not self.parse_operand():
                return False
        else:
            if not self.parse_operand():
                return False
        return True

    def parse_operand(self):
        """Parse operands in an expression (NUMBR, NUMBAR, YARN, etc.)."""
        token_type = self.get_current_token()[0]
        if token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "YARN_LITERAL", "TROOF_LITERAL", "VARIABLE_IDENTIFIER"]:
            self.consume()
            return True
        print(f"Error: Expected valid operand, but found '{token_type}'.")
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
            print("Error: Expected 'NO WAI'.")
            return False
        if not self.parse_statements():  # Handle else body
            return False
        if not self.match("CONDITIONAL_END"):  # OIC
            print("Error: Expected 'OIC'.")
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
        if not self.match("FUNCTION_DEF"):  # Expecting 'HOW IZ I'
            print("Error: Expected 'HOW IZ I'.")
            return False
        
        # Match the function name
        if not self.match("FUNCTION_IDENTIFIER"):  # Function name
            print("Error: Expected function name.")
            return False

        # Collect function parameters
        while True:
            if not self.match("VARIABLE_IDENTIFIER"):
                break

        # Parse function body until FUNCTION_END
        while self.get_current_token():
            if self.match("FUNCTION_END"):  # Expecting 'IF U SAY SO'
                return True

            token_type = self.get_current_token()[0]

            # Check for a RETURN statement
            if token_type == "RETURN":
                if not self.parse_return():
                    return False
                
            # Handle OUTPUT statements
            elif token_type == "OUTPUT_KEYWORD":
                if not self.parse_output_statement():
                    return False

            # Handle INPUT statements
            elif token_type == "INPUT_KEYWORD":
                if not self.parse_input_statement():
                    return False

            # Handle expressions
            elif token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT"]:
                if not self.parse_expression():
                    return False
            
            elif token_type == "IF_START":
                if not self.parse_if_statement():
                    return False

            elif token_type == "LOOP_START":
                if not self.parse_loop_statement():
                    return False
            
            elif token_type == "FUNCTION_CALL":
                if not self.parse_function_call():
                    return False
            
            elif token_type == "BREAK":
                self.match("BREAK")

            # Consume unexpected tokens to prevent errors
            else:
                print(f"Warning: Unexpected token '{token_type}' inside function body.")
                self.consume()

        print("Error: Missing 'IF U SAY SO' to end the function definition.")
        return False



    def parse_function_call(self):
        """Parse function call."""
        if not self.match("FUNCTION_CALL"):
            print("Error: Expected 'I IZ'.")
            return False

        if not self.match("FUNCTION_IDENTIFIER"):
            print("Error: Expected function name.")
            return False

        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable.")
            return False
        else:
            while self.match("VARIABLE_IDENTIFIER"):
                self.consume()

        return True
    
    def parse_return(self):
        """Parse return statement."""
        if not self.match("RETURN"):
            print("Error: Expected 'FOUND YR'.")
            return False
        
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable.")
            return False
        
        return True
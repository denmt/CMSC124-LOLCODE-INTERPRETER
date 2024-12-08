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
                if not self.parse_literal():
                    print("Error: Invalid variable initialization.")
                elif not self.parse_arithmetic_op():
                    print("Error: Invalid variable initialization.")
                elif not self.parse_boolean_op():
                    print("Error: Invalid variable initialization.")
                elif not self.parse_comparison_op():
                    print("Error: Invalid variable initialization.")
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
                if not self.parse_arithmetic_op():
                    return False
                
            elif token_type in ["BOOL_ALL_OF", "BOOL_ANY_OF"]:
                if not self.parse_infinite_boolean_op():
                    return False
            
            elif token_type in ["BOOL_AND", "BOOL_OR", "BOOL_XOR", "BOOL_NOT", "BOOL_ALL_OF", "BOOL_ANY_OF"]:
                if not self.parse_boolean_op():
                    return False
                
            elif token_type in ["COMPARE_EQUALS", "COMPARE_DIFF"]:
                if not self.parse_comparison_op():
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
            
            elif token_type == "VARIABLE_IDENTIFIER":
                if not self.parse_assignment():
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
        
        token_type = self.get_current_token()[0]
        if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
            self.parse_literal() 
        elif token_type == "VARIABLE_IDENTIFIER":
            self.match("VARIABLE_IDENTIFIER")
        elif not self.parse_statements():
            print("Error: Invalid print argument.")
            return False
        
        while self.match("PRINT_CAT"):
            token_type = self.get_current_token()[0]
            if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
                self.parse_literal()
            elif token_type == "VARIABLE_IDENTIFIER":
                self.match("VARIABLE_IDENTIFIER")
            else:
                if not self.parse_statements():
                    print("Error: Invalid print argument.")
                    return False
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
    
    def parse_assignment(self):
        """Parse variable assignment."""
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable identifier.")
            return False
        if not self.match("ASSIGNMENT"):  # Expecting 'R'
            print("Error: Expected 'R'.")
            return False
        
        token_type = self.get_current_token()[0]
        if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
            self.parse_literal()
        elif token_type == "VARIABLE_IDENTIFIER":
            self.match("VARIABLE_IDENTIFIER")
        else:
            if not self.parse_statements():
                print("Error: Invalid assignment value.")
                return False
        return True

    def parse_arithmetic_op(self):
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
            return False
        return True
    
    def parse_infinite_boolean_op(self):
        """Parse infinite boolean expressions like ALL OF or ANY OF."""
        if not (self.match("BOOL_ALL_OF") or self.match("BOOL_ANY_OF")):
            return False  # Must start with ALL OF or ANY OF

        has_operand = False  # Track if we have at least one operand

        while self.get_current_token():
            token_type = self.get_current_token()[0]

            if token_type == "CLOSING_KEYWORD":  # End of the boolean operation
                self.match("CLOSING_KEYWORD")
                if not has_operand:
                    print("Error: Expected at least one operand before 'MKAY'.")
                    return False
                return True

            elif token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL", "VARIABLE_IDENTIFIER"]:  # Parse operands
                self.match(token_type)
                has_operand = True

            elif token_type in ["BOOL_AND", "BOOL_OR", "BOOL_XOR", "BOOL_NOT"]:
                if not self.parse_boolean_op():
                    return False
                has_operand = True

            elif token_type == "OPERATOR_SEPARATOR":  # 'AN' as a separator
                if not has_operand:
                    print("Error: Unexpected 'AN' without a preceding operand.")
                    return False
                self.match("OPERATOR_SEPARATOR")  # Consume the 'AN'

            else:
                print(f"Error: Unexpected token '{token_type}'.")
                return False

        # If the loop exits without finding CLOSING_KEYWORD
        print("Error: Expected 'MKAY' to close the boolean expression.")
        return False
          
    def parse_boolean_op(self):
        """Parse boolean expressions."""
        if self.match("BOOL_AND") or self.match("BOOL_OR") or self.match("BOOL_XOR"):
            if not self.parse_boolean_operand():
                print("Error: Expected boolean operand.")
                return False
            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False
            if not self.parse_boolean_operand():
                return False
        elif self.match("BOOL_NOT"):
            if not self.parse_boolean_operand():
                return False
            
        return True
    
    def parse_boolean_operand(self):
        """Parse boolean operands."""
        token_type = self.get_current_token()[0]  # Get current token type
        if token_type in ["NUMBR_LITERAL","NUMBAR_LITERAL","TROOF_LITERAL", "VARIABLE_IDENTIFIER"]:
            self.match(token_type)  # Consume the operand
            return True
        elif token_type in ["BOOL_AND", "BOOL_OR", "BOOL_XOR"]:
            return self.parse_boolean_op()  # Parse nested boolean op
        elif token_type == "BOOL_NOT":
            return self.parse_boolean_op()  # Parse NOT operation
        
        print("Error: Expected boolean operand.")
        return False
        
    def parse_comparison_op(self):
        """Parse a comparison expression."""
        if self.match("COMPARE_EQUALS") or self.match("COMPARE_DIFF"):
            if not self.parse_operand():
                return False
            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False
 
            token_type = self.get_current_token()[0]
            if token_type in ["EXPR_BIGGR", "EXPR_SMALLR"]:
                self.match(token_type)
                if not self.parse_operand():
                    return False
                if not self.match("OPERATOR_SEPARATOR"):
                    print("Error: Expected 'AN'.")
                    return False
                                
            if not self.parse_operand():
                return False
        return True
                  
    def parse_operand(self):
        """Parse operands in an expression (NUMBR, NUMBAR, YARN, etc.)."""
        token_type = self.get_current_token()[0]
        if token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "VARIABLE_IDENTIFIER"]:
            self.match(token_type)
            return True
        print(f"Error: Expected valid operand, but found '{token_type}'.")
        return False

    def parse_literal(self):
        """Parse Literals."""
        token_type = self.get_current_token()[0]
        if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
            if not self.match(token_type):
                print(f"Error: Expected literal, but found '{token_type}'.")
                return False
        return True

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
        if not self.parse_arithmetic_op():  # Loop condition
            return False
        if not self.match("LOOP_END"):  # IM OUTTA YR
            print("Error: Expected 'IM OUTTA YR'.")
            return False
        return True

    def parse_function_definition(self):
        """Parse function definition."""
        # Expecting 'HOW IZ I' to define a function
        if not self.match("FUNCTION_DEF"):  
            print("Error: Expected 'HOW IZ I'.")
            return False

        # Expecting a function name
        if not self.match("FUNCTION_IDENTIFIER"):  
            print("Error: Expected function name.")
            return False

        # Handle optional parameters
        if self.match("DELIMITER"):  # Expecting 'YR'
            if not self.match("VARIABLE_IDENTIFIER"):
                print("Error: Expected a parameter.")
                return False

            # Handle additional parameters with 'AN'
            while self.match("OPERATOR_SEPARATOR"):  
                if not self.match("DELIMITER"):  # Expecting 'YR'
                    print("Error: Expected parameter with 'YR'.")
                    return False
                if not self.match("VARIABLE_IDENTIFIER"):
                    print("Error: Expected a parameter.")
                    return False

        # Parse the function body until 'IF U SAY SO'
        while self.get_current_token():
            if self.match("FUNCTION_END"):  # Expecting 'IF U SAY SO'
                return True

            token_type = self.get_current_token()[0]

            # Handle return statements
            if token_type == "RETURN":
                if not self.parse_return():
                    return False

            # Handle output statements
            elif token_type == "OUTPUT_KEYWORD":
                if not self.parse_output_statement():
                    return False

            # Handle input statements
            elif token_type == "INPUT_KEYWORD":
                if not self.parse_input_statement():
                    return False

            # Handle expressions
            elif token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT"]:
                if not self.parse_arithmetic_op():
                    return False

            # Handle IF statements
            elif token_type == "IF_START":
                if not self.parse_if_statement():
                    return False

            # Handle loops
            elif token_type == "LOOP_START":
                if not self.parse_loop_statement():
                    return False

            # Handle function calls
            elif token_type == "FUNCTION_CALL":
                if not self.parse_function_call():
                    return False

            # Handle breaks
            elif token_type == "BREAK":
                self.match("BREAK")

            # Handle unexpected tokens to avoid errors
            else:
                print(f"Warning: Unexpected token '{token_type}' inside function body.")
                self.consume()

        # If 'IF U SAY SO' is not found
        print("Syntax Error: Missing end line for function definition.")
        return False

    def parse_function_call(self):
        """Parse function call."""
        if not self.match("FUNCTION_CALL"):
            print("Error: Expected 'I IZ'.")
            return False

        if not self.match("FUNCTION_IDENTIFIER"):
            print("Error: Expected function name.")
            return False
        
        # Handle optional parameters
        if self.match("DELIMITER"):  # Expecting 'YR'
            if not self.match("VARIABLE_IDENTIFIER"):
                print("Error: Expected a parameter.")
                return False

            # Handle additional parameters with 'AN'
            while self.match("OPERATOR_SEPARATOR"):  
                if not self.match("DELIMITER"):  # Expecting 'YR'
                    print("Error: Expected parameter with 'YR'.")
                    return False
                if not self.match("VARIABLE_IDENTIFIER"):
                    print("Error: Expected a parameter.")
                    return False
        
        return True
    
    def parse_return(self):
        """Parse return statement."""
        if not self.match("RETURN"):
            print("Error: Expected 'FOUND YR'.")
            return False
        
        token_type = self.get_current_token()[0]

        if token_type == "VARIABLE_IDENTIFIER":
            self.match("VARIABLE_IDENTIFIER")
            return True
        elif token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT"]:
            return self.parse_arithmetic_op()
        else:
            print("Error: Invalind return value.\n")
            return False
        

from tkinter import simpledialog


class SemanticAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = {}
        self.console_output = []  # Stores console output (for VISIBLE)

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
            token_type = self.get_current_token()[0]
            if token_type == "VARIABLE_IDENTIFIER":
                var_name = self.get_current_token()[1]
                self.symbol_table[var_name] = "NOOB" # Initialize variable with NOOB
                self.match("VARIABLE_IDENTIFIER")
            else:
                print("Error: Expected a variable identifier.")
                return False
            
            if self.match("VARIABLE_ASSIGNMENT"):  # Expecting 'ITZ'
                token_type = self.get_current_token()[0]
                if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
                    value = self.get_current_token()[1]
                    self.symbol_table[var_name] = value
                    self.match(token_type)  # Consume the literal value

                elif token_type == "VARIABLE_IDENTIFIER":
                    value = self.get_current_token()[1]
                    # Check if the value is a valid variable
                    if value not in self.symbol_table:
                        print(f"Error: Variable '{value}' not declared.")
                        return False
                    else:
                        self.symbol_table[var_name] = self.symbol_table[value] # Assign the value of the variable.
                        self.match("VARIABLE_IDENTIFIER")  # Consume the variable name
                else:
                    value = self.parse_expressions()
                    if value is None:
                        print("Error: Invalid assignment value.")
                        return False
                    self.symbol_table[var_name] = value
        return True

    
    def parse_expressions(self):
        """Parse expressions."""
        token_type = self.get_current_token()[0]
        if token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT", "EXPR_MOD", "EXPR_BIGGR", "EXPR_SMALLR"]:
            return self.parse_arithmetic_op()
        elif token_type in ["BOOL_ALL_OF", "BOOL_ANY_OF"]:
            return self.parse_infinite_boolean_op()
        elif token_type in ["BOOL_AND", "BOOL_OR", "BOOL_XOR", "BOOL_NOT"]:
            return self.parse_boolean_op()
        elif token_type in ["COMPARE_EQUALS", "COMPARE_DIFF"]:
            return self.parse_comparison_op()
        elif token_type == "CONCAT":
            return self.parse_concat()
        elif token_type == "OUTPUT_KEYWORD":
            return self.parse_output_statement()
        elif token_type == "INPUT_KEYWORD":
            return self.parse_input_statement()
        elif token_type == "TYPECAST_OPERATOR":
            return self.parse_typecast()
        elif token_type == "SWITCH_START":
            return self.parse_switch_statement()
        elif token_type == "IF_START":
            return self.parse_if_statement()
        elif token_type == "LOOP_START":
            return self.parse_loop_statement()
        elif token_type == "FUNCTION_CALL":
            return self.parse_function_call()
        elif token_type == "VARIABLE_IDENTIFIER":
            self.consume()  # Move to the next token
            next_token = self.get_current_token()  # Peek at the next token

            if next_token and next_token[1] == "IS NOW A":
                self.current_index -= 1  # Move back to the variable identifier
                return self.parse_typecast()
            elif next_token and next_token[1] == "R":
                self.current_index -= 1  # Move back to the variable identifier
                return self.parse_assignment()
            else:
                self.current_index -= 1  # Move back to the variable identifier
                self.match("VARIABLE_IDENTIFIER")
                return True
        # Unrecognized token
        print(f"Error: Unexpected token '{token_type}' in expressions.")
        return False

    def parse_statements(self):
        """Parse various statements in the program."""
        while self.get_current_token():
            token_type = self.get_current_token()[0]

            # End of program
            if token_type == "CODE_DELIMITER" and self.get_current_token()[1] == "KTHXBYE":
                return True  # Valid end of program

            # Ignore comments
            if token_type in ["COMMENT", "MULTILINE_COMMENT_START"]:
                self.consume()  # Skip comments
                continue

            if token_type == "FUNCTION_DEF":
                if not self.parse_function_definition():
                    return False

            # Delegate to parse_expressions for handling statements
            elif not self.parse_expressions():
                print(f"Error: Unexpected token '{token_type}' in statements.")
                return False
            
        return True

    def parse_output_statement(self):
        """Parse VISIBLE statement."""
        if not self.match("OUTPUT_KEYWORD"):  # Match "VISIBLE"
            print("Error: Expected 'VISIBLE'.")
            return False

        output_parts = []  # Collect parts of the output

        # Parse the first argument
        token_type = self.get_current_token()[0]
        if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
            value = self.parse_literal()
            output_parts.append(value)
        elif token_type == "VARIABLE_IDENTIFIER":
            var_name = self.get_current_token()[1]
            self.match("VARIABLE_IDENTIFIER")
            if var_name in self.symbol_table:
                output_parts.append(self.symbol_table[var_name])
            else:
                print(f"Error: Variable '{var_name}' not declared.")
                return False
        else:
            value = self.parse_expressions()
            if value is None:
                print("Error: Invalid print argument.")
                return False
            output_parts.append(value)

        # Parse concatenated arguments
        while self.match("PRINT_CAT"):  # Match "!"
            token_type = self.get_current_token()[0]
            if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
                value = self.parse_literal()
                output_parts.append(value)
            elif token_type == "VARIABLE_IDENTIFIER":
                var_name = self.get_current_token()[1]
                self.match("VARIABLE_IDENTIFIER")
                if var_name in self.symbol_table:
                    output_parts.append(self.symbol_table[var_name])
                else:
                    print(f"Error: Variable '{var_name}' not declared.")
                    return False
            else:
                value = self.parse_expressions()
                if value is None:
                    print("Error: Invalid print argument.")
                    return False
                output_parts.append(value)

        # Store the output in the console_output list
        self.console_output.append("".join(map(str, output_parts)))
        return True

        
    def parse_input_statement(self):
        """Parse GIMMEH statement."""
        if not self.match("INPUT_KEYWORD"):
            print("Error: Expected 'GIMMEH'.")
            return False
        
        token_type = self.get_current_token()[0]
        if token_type == "VARIABLE_IDENTIFIER":
            var_name = self.get_current_token()[1]
            if var_name not in self.symbol_table:
                print(f"Error: Variable '{var_name}' not declared.")
                return False
            else:
                self.match("VARIABLE_IDENTIFIER")
                # Use a popup input dialog to get the value
                value = simpledialog.askstring("Input Required", f"Enter value for {var_name}:")
                
                if value is None:  # Handle cancellation
                    print("Input cancelled.")
                    return False
                
                self.symbol_table[var_name] = value
        return True

    
    def parse_assignment(self):
        """Parse variable assignment."""
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable identifier.")
            return False
        
        variable_name = self.tokens[self.current_index - 1][1]
        
        if not self.match("ASSIGNMENT"):  # Expecting 'R'
            print("Error: Expected 'R'.")
            return False

        value = self.evaluate_expression()
        if value is None:
            print("Error: Invalid assignment value.")
            return False
        
        # Update variable in the symbol table
        self.symbol_table[variable_name] = value
        print(f"Variable updated: {variable_name} = {value}")
        return True

    def parse_arithmetic_op(self):
        """Parse and evaluate arithmetic operation."""
        operator = self.get_current_token()[0]
        
        if self.match("EXPR_SUM") or self.match("EXPR_DIFF") or self.match("EXPR_PRODUKT") or \
        self.match("EXPR_QUOSHUNT") or self.match("EXPR_MOD") or self.match("EXPR_BIGGR") or \
        self.match("EXPR_SMALLR"):
            
            # Parse and get the value of the first operand
            operand1 = self.parse_arith_operand()
            if operand1 is None:
                return None

            # Expect the operator separator 'AN'
            if not self.match("OPERATOR_SEPARATOR"):
                print("Error: Expected 'AN'.")
                return None

            # Parse and get the value of the second operand
            operand2 = self.parse_arith_operand()
            if operand2 is None:
                return None

            # Perform the arithmetic operation
            if operator == "EXPR_SUM":
                return operand1 + operand2
            elif operator == "EXPR_DIFF":
                return operand1 - operand2
            elif operator == "EXPR_PRODUKT":
                return operand1 * operand2
            elif operator == "EXPR_QUOSHUNT":
                if operand2 == 0:
                    print("Error: Division by zero.")
                    return None
                return operand1 / operand2
            elif operator == "EXPR_MOD":
                if operand2 == 0:
                    print("Error: Division by zero.")
                    return None
                return operand1 % operand2
            elif operator == "EXPR_BIGGR":
                return max(operand1, operand2)
            elif operator == "EXPR_SMALLR":
                return min(operand1, operand2)
        else:
            print(f"Error: Expected arithmetic operator, but found '{operator}'.")
            return None

    def parse_arith_operand(self):
        """Parse and return the value of operands in an arithmetic expression."""
        token_type = self.get_current_token()[0]

        # Check for numeric literals
        if token_type == "NUMBR_LITERAL":
            value = int(self.get_current_token()[1])
            self.match("NUMBR_LITERAL")  # Consume the token
            return value
        elif token_type == "NUMBAR_LITERAL":
            value = float(self.get_current_token()[1])
            self.match("NUMBAR_LITERAL")  # Consume the token
            return value

        # Check for variables
        if token_type == "VARIABLE_IDENTIFIER":
            var_name = self.get_current_token()[1]

            if var_name not in self.symbol_table:
                print(f"Error: Variable '{var_name}' not declared.")
                return None

            value = self.symbol_table[var_name]

            # Check if the value is a string, then convert it to a number
            if isinstance(value, str):
                try:
                    if '.' in value:  # Check for decimal to decide float
                        value = float(value)
                    else:  # Otherwise, treat as int
                        value = int(value)
                except ValueError:
                    print(f"Error: Variable '{var_name}' does not hold a numeric value.")
                    return None

            self.match("VARIABLE_IDENTIFIER")  # Consume the token
            return value

        # Check for nested arithmetic expressions
        if token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT", "EXPR_QUOSHUNT", "EXPR_MOD", "EXPR_BIGGR", "EXPR_SMALLR"]:
            return self.parse_arithmetic_op()

        # If none of the above match, raise an error
        print(f"Error: Expected valid numeric operand, but found '{token_type}'.")
        return None

    def parse_boolean_op(self):
        '''Parse boolean operations'''
        if self.match("BOOL_AND") or self.match("BOOL_OR") or self.match("BOOL_XOR") or self.match("BOOL_NOT"):
            if not self.parse_operand():
                return False
            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False
            if not self.parse_operand():
                return False
        elif self.match("BOOL_ALL_OF") or self.match("BOOL_ANY_OF"):
            while self.match("CLOSING_KEYWORD"):
                if not self.parse_operand():
                    return False
                if not self.match("OPERATOR_SEPARATOR"):
                    print("Error: Expected 'AN'.")
                    return False
                if not self.parse_operand():
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
        value = self.get_current_token()[1]  # Extract the literal value
        if token_type == "NUMBR_LITERAL":
            value = int(value)  # Convert to integer
        elif token_type == "NUMBAR_LITERAL":
            value = float(value)  # Convert to float
        elif token_type in ["YARN_LITERAL", "TROOF_LITERAL"]:
            value = value  # Strings and TROOF literals can stay as is
        else:
            print(f"Error: Expected literal, but found '{token_type}'.")
            return None
        self.match(token_type)
        return value

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
        

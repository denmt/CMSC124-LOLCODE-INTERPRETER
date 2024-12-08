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
        elif token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "YARN_LITERAL", "TROOF_LITERAL"]:
            return self.parse_literal()
        if token_type == "CLOSING_KEYWORD": 
            return self.match("CLOSING_KEYWORD")
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
        while self.match("PRINT_CAT") or self.match("OPERATOR_SEPARATOR"):  # Match "!"
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
        token_type = self.get_current_token()[0]
        
        if token_type == "VARIABLE_IDENTIFIER":
            var_name = self.get_current_token()[1]
            if var_name not in self.symbol_table:
                print(f"Error: Variable '{var_name}' not declared.")
                return False
            self.match("VARIABLE_IDENTIFIER")
        
        if not self.match("ASSIGNMENT"):  # Expecting 'R'
            print("Error: Expected 'R'.")
            return False

        token_type = self.get_current_token()[0]

        if token_type in ["YARN_LITERAL", "NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL"]:
            value = self.parse_literal()
            self.symbol_table[var_name] = value

        elif token_type in ["TYPECAST_OPERATOR"]:
            if not self.match("TYPECAST_OPERATOR"):  # Consume "MAEK"
                return False
            varident = self.get_current_token()
            if varident[0] == "VARIABLE_IDENTIFIER":
                var_name1 = varident[1]
                if var_name != var_name1:
                    print("Error: Variable name mismatch.")
                    return False
                else: 
                    self.match("VARIABLE_IDENTIFIER")

            if not self.match("TYPE_ASSIGNMENT"):  # Consume "A"
                print("Error: Expected Type Assignment keyword after 'MAEK' and variable identifier.")
                return False
            
            var_type = self.get_current_token()
            if var_type[0] == "TYPE_LITERAL":
                if var_type[1] == "YARN":
                    # Change the variable to string.
                    self.symbol_table[var_name] = '"' + str(self.symbol_table[var_name]) + '"'
                elif var_type[1] == "NUMBR":
                    self.symbol_table[var_name] = int(self.symbol_table[var_name])
                elif var_type[1] == "NUMBAR":
                    self.symbol_table[var_name] = float(self.symbol_table[var_name])
                elif var_type[1] == "TROOF":
                    if self.symbol_table[var_name] == 1 or self.symbol_table[var_name] == "1":
                        self.symbol_table[var_name] = "WIN"
                    elif self.symbol_table[var_name] == 0 or self.symbol_table[var_name] == "0":
                        self.symbol_table[var_name] = "FAIL"
                else:
                    print("Error: Invalid type.")
                    return False
                self.match("TYPE_LITERAL")
            else:
                print("Error: Expected a valid type literal.")
                return False

        elif token_type == "VARIABLE_IDENTIFIER":
            value = self.get_current_token()[1]
            if value not in self.symbol_table:
                print(f"Error: Variable '{value}' not declared.")
                return False
            self.symbol_table[var_name] = self.symbol_table[value]
            self.match("VARIABLE_IDENTIFIER")

        elif token_type == "CONCAT":
            if not self.parse_concat():
                return False
        else:
            value = self.parse_expressions()
            if value is None:
                print("Error: Invalid assignment value.")
                return False
            self.symbol_table[var_name] = value

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

    def parse_typecast(self):
        """Parse typecast operation."""
        # Check for variable identifier
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected a variable identifier.")
            return False

        # Check for typecast operators (e.g., "IS NOW A" or "MAEK")
        if self.get_current_token()[1] == "IS NOW A":
            self.match("TYPECAST_OPERATOR")  # Consume "IS NOW A"
            if not self.match("TYPE_LITERAL"):
                print("Error: Expected a valid type literal.")
                return False
        elif self.get_current_token()[1] == "MAEK":
            self.match("TYPECAST_OPERATOR")  # Consume "MAEK"
            if not self.match("VARIABLE_IDENTIFIER"):
                print("Error: Expected a variable identifier after 'MAEK'.")
                return False

            # Handle type assignment or direct type literals
            token_type = self.get_current_token()[0]
            if token_type == "TYPE_ASSIGNMENT":
                self.match("TYPE_ASSIGNMENT")  # Consume "ITZ A"
                if not self.match("TYPE_LITERAL"):
                    print("Error: Expected a valid type literal after 'ITZ A'.")
                    return False
            elif token_type == "TYPE_LITERAL":
                self.match("TYPE_LITERAL")
            else:
                print("Error: Expected a valid type literal or type assignment.")
                return False
        else:
            print("Error: Expected 'IS NOW A' or 'MAEK' as typecast operator.")
            return False

        return True
    
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
        elif token_type == "TROOF_LITERAL":
            value = self.get_current_token()[1]
            if value == "WIN":
                self.match("TROOF_LITERAL")
                return 1
            elif value == "FAIL":
                self.match("TROOF_LITERAL")
                return 0
        elif token_type == "YARN_LITERAL":
            value = self.get_current_token()[1]
            
            # Remove the surrounding quotes from the string literal
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Remove the first and last character (quotes)
            
            # Check if the value is a valid number (for numeric literals that are mistakenly labeled as YARN)
            try:
                if '.' in value:  # Check for decimal to decide float
                    value = float(value)
                else:  # Otherwise, treat as int
                    value = int(value)
            except ValueError:
                # If it's not a valid number, it's treated as a string
                pass
            
            self.match("YARN_LITERAL")  # Consume the token
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
    
    def parse_concat(self):
        """Parse string concatenation."""
        if not self.match("CONCAT"):
            return False
        
        value = ""  # Initialize the concatenated value
        while True:
            token_type = self.get_current_token()
            if token_type[0] == "YARN_LITERAL":
                value = value + token_type[1]
                self.match("YARN_LITERAL")
            if token_type[0] == "NUMBR_LITERAL":
                value = value + str(token_type[1])
                self.match("NUMBR_LITERAL")
            if token_type[0] == "NUMBAR_LITERAL":
                value = value + str(token_type[1])
                self.match("NUMBAR_LITERAL")
            elif token_type[0] == "TROOF_LITERAL":
                value = value + token_type[1]
                self.match("TROOF_LITERAL")
            elif token_type[0] == "VARIABLE_IDENTIFIER":
                var_name = token_type[1]
                if var_name not in self.symbol_table:
                    print(f"Error: Variable '{var_name}' not declared.")
                    return False
                value = value + self.symbol_table[var_name]
                self.match("VARIABLE_IDENTIFIER")
            else:
                print("Error: Invalid concatenation value.")
                return False

            if not self.match("OPERATOR_SEPARATOR"):
                break  # End of concatenation chain

        return value

    def parse_infinite_boolean_op(self):
        """Parse infinite boolean expressions like ALL OF or ANY OF."""
        
        # Check for ANY OF or ALL OF
        token_type = self.get_current_token()[0]
        if not (token_type == "BOOL_ALL_OF" or token_type == "BOOL_ANY_OF"):
            return False  # Must start with ALL OF or ANY OF
        
        # Match the initial token for ALL OF or ANY OF
        self.match(token_type)
        
        has_operand = False  # Track if we have at least one operand
        result = None  # To store the final result of the operation

        print(f"Parsing an infinite boolean expression: {token_type}...")

        while self.get_current_token():
            token_type = self.get_current_token()[0]
            
            # Debug print to see the current token
            print(f"Current token: {token_type}")

            if token_type == "CLOSING_KEYWORD":  # End of the boolean operation
                self.match("CLOSING_KEYWORD")  # Consume 'MKAY'
                if not has_operand:
                    print("Error: Expected at least one operand before 'MKAY'.")
                    return False
                print(f"Final result: {result}")
                return result

            elif token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "TROOF_LITERAL", "VARIABLE_IDENTIFIER"]:
                # Consume literals or variable identifiers as operands
                operand = self.parse_boolean_operand()
                if operand is None:
                    return False
                has_operand = True
                # If it's the first operand, set it as the initial result
                if result is None:
                    result = operand
                else:
                    # Apply the boolean operation based on the type of "ALL OF" or "ANY OF"
                    if token_type == "BOOL_ALL_OF":
                        result = result and operand  # AND operation for ALL OF
                        print(f"Applying AND (ALL OF) with operand: {operand}, result now: {result}")
                    elif token_type == "BOOL_ANY_OF":
                        result = result or operand  # OR operation for ANY OF
                        print(f"Applying OR (ANY OF) with operand: {operand}, result now: {result}")

            elif token_type in ["BOOL_AND", "BOOL_OR", "BOOL_XOR", "BOOL_NOT"]:
                # Handle logical operators that are applied between operands
                if not self.parse_boolean_op():
                    return False
                has_operand = True

            elif token_type == "OPERATOR_SEPARATOR":  # Handle 'AN'
                if not has_operand:
                    print("Error: Unexpected 'AN' without a preceding operand.")
                    return False
                self.match("OPERATOR_SEPARATOR")  # Consume the 'AN'
                print("Found 'AN', looking for next operand...")

            elif token_type == "BOOL_BOTH_OF" or token_type == "BOOL_EITHER_OF":
                # Recursively parse nested operations like "BOTH OF" and "EITHER OF"
                # Ensure recursion is correctly managed and doesn't loop endlessly
                if not self.parse_infinite_boolean_op():
                    return False
                has_operand = True

            else:
                print(f"Error: Unexpected token '{token_type}'.")
                return False

        # If the loop exits without finding CLOSING_KEYWORD
        print("Error: Expected 'MKAY' to close the boolean expression.")
        return False




          
    def parse_boolean_op(self):
        """Parse and evaluate boolean operations like AND, OR, XOR, and NOT."""
        token_type = self.get_current_token()[0]
        
        # Check for boolean operators: AND, OR, XOR, NOT
        if self.match("BOOL_AND") or self.match("BOOL_OR") or self.match("BOOL_XOR") or self.match("BOOL_NOT"):
            
            # Handle 'NOT' operator, which only requires one operand
            if token_type == "BOOL_NOT":
                operand1 = self.parse_expressions()
                if operand1 is None:
                    return None
                return not bool(operand1)  # Negate the operand

            # For AND, OR, XOR, we need two operands
            operand1 = self.parse_expressions()
            if operand1 is None:
                return None
            
            # Expect the operator separator 'AN'
            if not self.match("OPERATOR_SEPARATOR"):
                print("Error: Expected 'AN'.")
                return None
            
            operand2 = self.parse_expressions()
            if operand2 is None:
                return None

            operand1 = bool(operand1)
            operand2 = bool(operand2)
            # Perform the logical operation based on the operator
            if token_type == "BOOL_AND":
                return operand1 and operand2
            elif token_type == "BOOL_OR":
                return operand1 or operand2
            elif token_type == "BOOL_XOR":
                return operand1 != operand2  # XOR is True if exactly one operand is True

        else:
            print(f"Error: Expected boolean operator, but found '{token_type}'.")
            return None

    
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
        return None

    def parse_comparison_op(self):
        """Parse a comparison expression."""
        if self.match("COMPARE_EQUALS") or self.match("COMPARE_DIFF"):
            if not self.comparison_operand():
                return False
            if not self.match("OPERATOR_SEPARATOR"):  # Expect 'AN'
                print("Error: Expected 'AN'.")
                return False
            if not self.comparison_operand():
                return False
        return True
    
    def comparison_operand(self):
        '''Parse comparison operands.'''
        token_type = self.get_current_token()[0]
        if token_type in ["NUMBR_LITERAL", "NUMBAR_LITERAL", "VARIABLE_IDENTIFIER"]:
            self.match(token_type)
            return True
        elif token_type in ["EXPR_BIGGR", "EXPR_SMALLR"]:
            self.match(token_type)
            if not self.comparison_operand():
                return False
            if not self.match("OPERATOR_SEPARATOR"):
                print("Error: Expected 'AN'.")
                return False
            if not self.comparison_operand():
                return False
            
            return True
            
        print(f"Error: Expected valid operand, but found '{token_type}'.")
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
        elif token_type in ["YARN_LITERAL"]:
            value = value[1:-1]  # Remove the quotes from the string
        elif token_type == "TROOF_LITERAL":
            value = value
        else:
            print(f"Error: Expected literal, but found '{token_type}'.")
            return None
        self.match(token_type)
        return value
    
    def parse_if_statement(self):
        """Parse if statement."""
        if not self.match("IF_START"):
            print("Error: Expected 'O RLY?'.")
            return False

        # Handle the "YA RLY" block
        if not self.match("IF_YES"):
            print("Error: Expected 'YA RLY'.")
            return False

        # Parse the statements under "YA RLY"
        while self.get_current_token():
            if self.match("CONDITIONAL_END"):
                return True  # End of the IF block
            if self.get_current_token()[0] == "IF_NO":
                break  # Transition to "NO WAI"
            if not self.parse_expressions():
                return False

        # Handle the "NO WAI" block if present
        if not self.match("IF_NO"):
            print("Error: Expected 'NO WAI'.")
            return False

        # Parse the statements under "NO WAI"
        while self.get_current_token():
            if self.match("CONDITIONAL_END"):
                return True  # End of the IF block
            if not self.parse_expressions():
                return False

        print("Error: Expected 'OIC' to close the if statement.")
        return False

    def parse_loop_statement(self):
        """Parse loop statement."""
        # Match the start of the loop
        if not self.match("LOOP_START"):  # 'IM IN YR'
            print("Error: Expected 'IM IN YR'.")
            return False

        # Match the loop label
        if not self.match("LOOP_IDENTIFIER"):  # e.g., 'asc' or 'desc'
            print("Error: Expected loop label after 'IM IN YR'.")
            return False

        # Match the operation (UPPIN or NERFIN)
        if not self.match("LOOP_OPERATION"):  # 'UPPIN' or 'NERFIN'
            print("Error: Expected 'UPPIN' or 'NERFIN'.")
            return False

        # Match the delimiter
        if not self.match("DELIMITER"):  # 'YR'
            print("Error: Expected 'YR' after 'UPPIN' or 'NERFIN'.")
            return False

        # Match the loop variable
        if not self.match("VARIABLE_IDENTIFIER"):  # Loop variable
            print("Error: Expected a variable after 'YR'.")
            return False

        # Match the loop condition (TIL or WILE)
        if not self.match("LOOP_CONDITION"):  # 'TIL' or 'WILE'
            print("Error: Expected 'TIL' or 'WILE'.")
            return False

        # Parse the loop condition expression
        if not self.parse_expressions():  # Expression after 'TIL' or 'WILE'
            print("Error: Failed to parse loop condition expression.")
            return False

        # Parse the body of the loop
        while self.get_current_token():
            # End of the loop block
            if self.match("LOOP_END"):  # 'IM OUTTA YR'
                if self.match("LOOP_IDENTIFIER"):  # Match the loop label
                    return True
                else:
                    print("Error: Expected loop label after 'IM OUTTA YR'.")
                    return False

            # Parse loop body expressions
            if not self.parse_expressions():
                return False

        # If we exit the loop without finding 'IM OUTTA YR'
        print("Error: Expected 'IM OUTTA YR' to end the loop.")
        return False

    def parse_switch_statement(self):
        """Parse a switch-case statement."""
        if not self.match("SWITCH_START"):
            print("Error: Expected 'WTF?'.")
            return False

        encountered_default = False

        while self.get_current_token():
            token_type = self.get_current_token()[0]

            # Parse each case or default block using switch_case
            if token_type in ["SWITCH_CASE", "SWITCH_DEFAULT"]:
                if token_type == "SWITCH_DEFAULT":
                    if encountered_default:
                        print("Error: Multiple 'OMGWTF' blocks are not allowed.")
                        return False
                    encountered_default = True

                if not self.switch_case():
                    return False

            # Handle the end of the switch statement
            elif token_type == "CONDITIONAL_END":
                self.match("CONDITIONAL_END")
                return True

            else:
                print(f"Error: Unexpected token '{token_type}' in switch statement.")
                return False

        print("Error: Expected 'OIC' to close the switch statement.")
        return False


    def switch_case(self):
        """Parse a single case or default block."""
        token_type = self.get_current_token()[0]

        # Handle case blocks
        if token_type == "SWITCH_CASE":
            self.match("SWITCH_CASE")  # Consume 'OMG'
            if not self.match("NUMBR_LITERAL"):
                print("Error: Expected a number literal for case block.")
                return False

            # Parse the statements within the case
            while self.get_current_token():
                exp_token = self.get_current_token()[0]
                if exp_token in ["SWITCH_CASE", "SWITCH_DEFAULT"]:
                    break
                elif exp_token == "BREAK":  # Break out of the current case
                    self.match("BREAK")
                    break
                if not self.parse_expressions():
                    return False

        # Handle the default block
        elif token_type == "SWITCH_DEFAULT":
            self.match("SWITCH_DEFAULT")

            # Parse the statements within the default case
            while self.get_current_token():
                next_token = self.get_current_token()[0]
                if next_token == "CONDITIONAL_END":  # End of the switch-case
                    return True
                if not self.parse_expressions():
                    return False
                
        # Handle unexpected cases
        else:
            print(f"Error: Unexpected token '{token_type}' in switch-case.")
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

            # Handle breaks
            elif token_type == "BREAK":
                self.match("BREAK")

            # Parse expressions within the function body
            elif not self.parse_expressions():
                return False

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
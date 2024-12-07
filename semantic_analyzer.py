class SemanticAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = {}  # Holds variables and their values
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
            self.consume()
            return True
        return False

    def parse(self):
        """Start parsing and executing the program."""
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

        # Parse the WAZZUP block for variable declarations
        if not self.parse_wazzup():
            return False

        # Parse statements (operations, outputs, etc.)
        if not self.parse_statements():
            return False

        # Expecting 'KTHXBYE' at the end
        if not self.match("CODE_DELIMITER"):
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

            # Handle variable initialization
            if self.match("VARIABLE_ASSIGNMENT"):  # 'ITZ'
                if not self.parse_expression():
                    return False

        return True

    def parse_statements(self):
        """Parse various statements in the program."""
        while self.get_current_token():
            token_type = self.get_current_token()[0]
            
            # Handle output (VISIBLE)
            if token_type == "OUTPUT_KEYWORD":  
                if not self.parse_output_statement():
                    return False
            
            # Handle input (GIMMEH)
            elif token_type == "INPUT_KEYWORD":
                if not self.parse_input_statement():
                    return False

            # Handle variable assignment
            elif token_type == "ASSIGNMENT":
                if not self.parse_assignment():
                    return False

            # Handle other operations or expressions
            elif token_type in ["EXPR_SUM", "EXPR_DIFF", "EXPR_PRODUKT"]:
                if not self.parse_expression():
                    return False

            elif token_type == "FUNCTION_DEF":  # Expecting function definition
                if not self.parse_function_definition():
                    return False

            elif token_type == "CODE_DELIMITER":
                if self.get_current_token()[1] == 'KTHXBYE':
                    return True

            else:
                print(f"Error: Unexpected token {token_type}")
                return False

        return True

    def parse_output_statement(self):
        """Handle 'VISIBLE' statement."""
        if not self.match("OUTPUT_KEYWORD"):
            print("Error: Expected 'VISIBLE'.")
            return False
        while self.get_current_token() and self.get_current_token()[0] not in ["NEWLINE", "CODE_DELIMITER"]:
            token_type = self.get_current_token()[0]
            if token_type == "VARIABLE_IDENTIFIER":
                var_name = self.get_current_token()[1]
                if var_name not in self.symbol_table:
                    print(f"Error: Undefined variable '{var_name}' used in VISIBLE.")
                    return False
                value = self.symbol_table[var_name]
                self.console_output.append(value)  # Output the value of the variable
            else:
                self.console_output.append(self.get_current_token()[1])  # Add string literals
            self.consume()  # Consume the token
        return True

    def parse_input_statement(self):
        """Handle 'GIMMEH' statement."""
        if not self.match("INPUT_KEYWORD"):
            print("Error: Expected 'GIMMEH'.")
            return False
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected variable for GIMMEH.")
            return False
        var_name = self.get_current_token()[1]
        if var_name not in self.symbol_table:
            print(f"Error: Undefined variable '{var_name}' for input.")
            return False
        user_input = input(f"Enter a value for {var_name}: ")
        self.symbol_table[var_name] = user_input  # Store the user input in the symbol table
        return True

    def parse_assignment(self):
        """Handle variable assignment."""
        if not self.match("VARIABLE_IDENTIFIER"):
            print("Error: Expected variable identifier for assignment.")
            return False
        var_name = self.get_current_token()[1]

        if not self.match("ASSIGNMENT"):  # Expecting 'R' for assignment
            print("Error: Expected assignment operator 'R'.")
            return False
        
        if not self.parse_expression():  # Handle the expression on the right-hand side
            return False

        # Assuming expression evaluation happens in parse_expression() method
        if self.get_current_token()[0] == "NUMBR_LITERAL":
            value = self.get_current_token()[1]  # Getting the value of the NUMBR_LITERAL
            self.symbol_table[var_name] = value
        elif self.get_current_token()[0] == "YARN_LITERAL":
            value = self.get_current_token()[1]  # Getting the value of the YARN_LITERAL
            self.symbol_table[var_name] = value
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

        if token_type == "NUMBR_LITERAL":  # Handle integer literals
            self.consume()
            return True

        elif token_type == "NUMBAR_LITERAL":  # Handle float literals
            self.consume()
            return True

        elif token_type == "YARN_LITERAL":  # Handle string literals
            self.consume()  # Now we consume the YARN_LITERAL token itself (including the quotes)
            return True

        elif token_type == "TROOF_LITERAL":  # Handle boolean literals (WIN/FAIL)
            self.consume()
            return True

        elif token_type == "VARIABLE_IDENTIFIER":  # Handle variables
            var_name = self.get_current_token()[1]
            if var_name not in self.symbol_table:
                print(f"Error: Undefined variable '{var_name}'.")
                return False
            self.consume()  # Consume the variable token
            return True

        else:
            print(f"Error: Expected valid operand, but found {token_type}.")
            return False

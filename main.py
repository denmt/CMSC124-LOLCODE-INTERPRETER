import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog, messagebox
from tkinter import ttk 
import lexical_analyzer
from syntax_analyzer import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer

def loadfile():
    # Open file dialog to select a file
    filepath = filedialog.askopenfilename()

    if filepath:
        with open(filepath, 'r') as file:
            content = file.read()

        text_editor.delete(1.0, tk.END)
        text_editor.insert(1.0, content)

def tokenize(content):
    """Save file content in a list and remove white space."""
    program = content.split('\n')
    program = [line.strip() for line in program]
    return lexical_analyzer.lexical_analyzer(program)

def execute():
    code = text_editor.get(1.0, tk.END).strip()

    if not code:
        messagebox.showwarning("Warning!", "No code to tokenize!")
        return

    try:
        # Tokenize the code
        tokens = tokenize(code)
        
        # Create an instance of SyntaxAnalyzer and parse the tokens
        syntax_analyzer = SyntaxAnalyzer(tokens)
        
        if syntax_analyzer.parse():  # Check if syntax is correct
            messagebox.showinfo("Success", "Syntax is correct!")
        else:
            messagebox.showerror("Error", "Syntax error in code!")
            return  # Stop further processing if syntax is incorrect

        # Create an instance of SemanticAnalyzer to perform semantic checks and execute the code
        semantic_analyzer = SemanticAnalyzer(tokens)
        
        if semantic_analyzer.parse():  # Check if semantic analysis passes
            messagebox.showinfo("Success", "Program executed successfully!")
        else:
            messagebox.showerror("Error", "Semantic error in code!")
            return  # Stop further processing if semantic analysis fails

        # Token output display
        token_output.delete(1.0, tk.END)
        for token in tokens:
            token_output.insert(tk.END, f"{token}\n")

        # Clear and display the symbol table
        for row in symbol_table.get_children():
            symbol_table.delete(row)

        for var, value in semantic_analyzer.symbol_table.items():
            symbol_table.insert("", "end", values=(var, value))
        
        # Display the console output (for VISIBLE statements)
        console_output.delete(1.0, tk.END)
        for output in semantic_analyzer.console_output:
            console_output.insert(tk.END, f"{output}\n")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to analyze syntax: {e}")

# GUI setup
root = tk.Tk()
root.title("LOLCODE Syntax and Semantic Checker")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Left column (text editor)
left_column = tk.Frame(frame, width=400, padx=10, pady=10)
left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

file_button = tk.Button(left_column, text="Load File", command=loadfile)
file_button.pack(pady=5)

text_editor_label = tk.Label(left_column, text="Code Editor:")
text_editor_label.pack()
text_editor = scrolledtext.ScrolledText(left_column, wrap=tk.WORD, height=25)
text_editor.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

# Right column (output)
right_column = tk.Frame(frame, width=400, padx=10, pady=10)
right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

run_button = tk.Button(right_column, text="Execute", command=execute)
run_button.pack(pady=5)

# Tokens display
token_output_label = tk.Label(right_column, text="Tokens:")
token_output_label.pack()
token_output = scrolledtext.ScrolledText(right_column, wrap=tk.WORD, height=10, bg="#f5f5f5")
token_output.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

# Symbol Table display 
symbol_table_label = tk.Label(right_column, text="Symbol Table:")
symbol_table_label.pack()

symbol_table = ttk.Treeview(right_column, columns=("Variable", "Value"), show="headings", height=10)
symbol_table.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

symbol_table.heading("Variable", text="Variable")
symbol_table.heading("Value", text="Value")

# Console output (for VISIBLE statements)
console_output_label = tk.Label(right_column, text="Console Output:")
console_output_label.pack()
console_output = scrolledtext.ScrolledText(right_column, wrap=tk.WORD, height=5, bg="#f5f5f5")
console_output.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

root.mainloop()

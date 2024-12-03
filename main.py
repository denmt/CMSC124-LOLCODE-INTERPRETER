import tkinter as tk
from tkinter import scrolledtext
import lexical_analyzer
from tkinter import filedialog, messagebox
from syntax_analyzer import SyntaxAnalyzer  # Import the syntax analyzer

def loadfile():
    # Open file dialog to select a file
    filepath = filedialog.askopenfilename()

    if filepath:
        with open(filepath, 'r') as file:
            content = file.read()

        text_editor.delete(1.0, tk.END)
        text_editor.insert(1.0, content)

def tokenize(content):
    # Save file content in a list and remove white space
    program = content.split('\n')
    program = [line.strip() for line in program]
    
    return lexical_analyzer.lexical_analyzer(program)

def execute():
    code = text_editor.get(1.0, tk.END).strip()

    if not code:
        messagebox.showwarning("Warning!", "No code to tokenize!")
        return

    try:
        tokens = tokenize(code)
        
        # Create an instance of SyntaxAnalyzer and parse the tokens
        syntax_analyzer = SyntaxAnalyzer(tokens)
        
        if syntax_analyzer.parse():  # Check if syntax is correct
            messagebox.showinfo("Success", "Syntax is correct!")
        else:
            messagebox.showerror("Error", "Syntax error in code!")
        
        # Token output display
        token_output.delete(1.0, tk.END)
        for token in tokens:
            token_output.insert(tk.END, f"{token}\n")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to analyze syntax: {e}")

# GUI setup
root = tk.Tk()
root.title("LOLCODE Syntax Checker")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

left_column = tk.Frame(frame, width=400, padx=10, pady=10)
left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Load file button
file_button = tk.Button(left_column, text="Load File", command=loadfile)
file_button.pack(pady=5)

# Text editor for code input
text_editor_label = tk.Label(left_column, text="Code Editor:")
text_editor_label.pack()
text_editor = scrolledtext.ScrolledText(left_column, wrap=tk.WORD, height=25)
text_editor.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

right_column = tk.Frame(frame, width=400, padx=10, pady=10)
right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Execute button
run_button = tk.Button(right_column, text="Execute", command=execute)
run_button.pack(pady=5)

# Output area for tokens
token_output_label = tk.Label(right_column, text="Tokens:")
token_output_label.pack()
token_output = scrolledtext.ScrolledText(right_column, wrap=tk.WORD, height=25, bg="#f5f5f5")
token_output.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

root.mainloop()

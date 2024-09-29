import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import logging
from main_node1 import main

# Redirect logging to the Text widget
class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

# Function to start the process and display a message
def start_process():
    # Clear the text box before starting
    output_text.delete(1.0, tk.END)
    
    # Redirect print statements to the text box
    sys.stdout = RedirectText(output_text)

    # Set up logging to redirect to the text box
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    text_handler = TextHandler(output_text)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    text_handler.setFormatter(formatter)
    logger.addHandler(text_handler)
    
    # Here you can integrate the functionality from your nodes or server
    messagebox.showinfo("Process Started", "The nodes and server have been started.")
    main()  # Call to main from main_node2

# Function to quit the application
def quit_application():
    sys.stdout = sys.__stdout__  # Restore original stdout
    logging.getLogger().handlers.clear()  # Clear logging handlers
    root.quit()

# Create the main application window
root = tk.Tk()
root.title("Distributed System GUI")
root.geometry("600x400")  # Set window size to be larger

# Create a start button
start_button = tk.Button(root, text="Start", command=start_process)
start_button.pack(pady=20)  # Add some vertical padding

# Create a quit button
quit_button = tk.Button(root, text="Quit", command=quit_application)
quit_button.pack(pady=10)

# Create a label to display text
label = tk.Label(root, text="Press 'Start' to run the nodes and server.")
label.pack(pady=10)

# Create a larger scrolled text box to display output
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
output_text.pack(pady=10)

# Run the application
root.mainloop()
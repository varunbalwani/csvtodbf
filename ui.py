
# ---------Full code to create a software application with python ---------------
 
# Import library
import csvtodbf
import tkinter as tk
from tkinter import filedialog
import karvy_direct
import os


column_map = {...}
column_list = [...]
# filename = ""

# def get_directory_path():
#     global filename
#     filename = os.path.dirname(__file__)

def browse_file():
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select File")
    if filename:
        # Process the selected file
        print("Selected File:", filename)
        csv_to_dbf_new(filename)
 
# Create window Tkinter
window = tk.Tk()
 
# Name our Tkinter application title
window.title(" Simple Windows App ")
 
# Define window size in Tkinter python
window.geometry("700x500")
 
# Create a label widget in Tkinter
label = tk.Label(window, text="Click the Button to update this Text",
font=('Calibri 15 bold'))
label.pack(pady=20)
 
# Function to update the label text for first button click in Tkinter
def csv_to_dbf_new(filename):
    csvtodbf.csv_to_dbf(filename, column_map, column_list)
     
# Function to update the label text for second button click in Tkinter
# get_directory_path()
def on_click_btn2():
    browse_file()   
    label["text"] = "Uploading..."
     
# Create 1st button to update the label widget
btn1 = tk.Button(window, text="Button1", command=csv_to_dbf_new)
btn1.pack(pady=20)
 
# Create 2nd button to update the label widget
btn2 = tk.Button(window, text="Button2", command=on_click_btn2)
btn2.pack(pady=40)
window.mainloop()
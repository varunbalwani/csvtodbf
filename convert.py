import os
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Progressbar, Treeview
import json
import pyperclip

from csvtodbf import csv_to_dbf, options


window = Tk()
window.title("CSV to DBF Convertor")
window.geometry('1980x800')

file_path = ""
option_list = list(options.keys())

display_error = []
total = 0
success_count = 0
error_count = 0


def update_progress_percentage(percentage):
    pb['value'] = int(percentage)
    formatted_percentage = "{:.1f}".format(percentage)
    value_label.config(text=f"{formatted_percentage}%")
    value_label.update()

    if percentage == 100:
        showinfo("Formatting Completed", "The formatting process has been completed.")


def select_file():
    result_tree.delete(*result_tree.get_children())
    error_tree.delete(*error_tree.get_children())
    global file_path
    file_path = filedialog.askopenfilename()
    file_name = file_path.split("/")[-1]
    file_label.config(text="Selected file: " + file_name)


def copy_table_line(event=None):
    selected_items = error_tree.selection()
    if not selected_items:
        data_values = []
        selected_items = result_tree.selection()
        for selected_item in selected_items:
            item_text = result_tree.item(selected_item)['text']
            data_values.append(item_text)
        data_values_str = "\n".join(data_values)
        pyperclip.copy(data_values_str)

    else:       
        table_lines = []
        for selected_item in selected_items:
            item_values = error_tree.item(selected_item)['values']
            table_line = [error_tree.item(selected_item)['text']] + item_values
            table_line_str = " | ".join(table_line)
            table_lines.append(table_line_str)

            child_items = error_tree.get_children(selected_item)
            for child_item in child_items:
                child_values = error_tree.item(child_item)['values']
                child_line = [error_tree.item(child_item)['text']] + child_values
                child_line_str = " | ".join(child_line)
                table_lines.append(child_line_str)

        table_lines_str = "\n".join(table_lines)
        pyperclip.copy(table_lines_str)

def select_all_table_lines():
    all_items = error_tree.get_children()
    error_tree.selection_set(all_items)


def run_script():
    global display_error, total, success_count, error_count
    if file_path:
        if not file_path.lower().endswith('.csv'):
            showerror("Invalid File", "Please select a CSV file.")
            return

        option = option_list.index(var.get())
        try:

            display_error, total, success_count, error_count = csv_to_dbf(
                file_path, *options.get(option_list[option]), update_progress_percentage
            )
            table_data = {
                "total": total,
                "success_count": success_count,
                "error_count": error_count,
                "error": display_error,
            }
            result_tree.delete(*result_tree.get_children())  # Clear the existing table
            error_tree.delete(*error_tree.get_children())  # Clear the existing error tree

            if display_error:
                # Stop the process and display all the values
                showinfo(
                    "Process Stopped",
                    "The process encountered errors. Please check the returned values.",
                )
            else:
                # Process completed successfully, display all the values
                showinfo("Process Completed", "The process has been completed successfully.")

            # Insert the JSON data into the table
            result_tree.insert(
                "",
                "end",
                text=file_path.split("/")[-1],
                values=(table_data['total'], table_data['success_count'], table_data['error_count']),
            )
            # result_tree.bind('<Button-3>',show_context_menu)
            result_tree.bind('<Control-c>',copy_table_line)
            # Insert error details
            if table_data['error']:
                for error in table_data['error']:
                    error_tree.insert(
                        "",
                        "end",
                        text=f"{error['row_no']}",
                        values=(error['csv_field'], error['dbf_field'], error['message']),
                    )

            # Add copy functionality to the error tree
            error_tree.bind('<Button-3>', show_context_menu)
            error_tree.bind('<Control-c>', copy_table_line)

        except Exception as e:
            showerror("Error", f"An error occurred during the process:\n{str(e)}")
    else:
        showerror("No File Selected", "Please select a file before running the script.")


def show_context_menu(event):
    error_tree.focus()
    selected_item = error_tree.selection()
    if selected_item:
        context_menu = Menu(window, tearoff=0)
        context_menu.add_command(label="Copy Line", command=copy_table_line)

        # Add "Select All" option to the context menu
        context_menu.add_command(label="Select All", command=select_all_table_lines)

        context_menu.post(event.x_root, event.y_root)
        # Bind the <Button-1> and <Button-3> events to unpost the context menu and close the dropdown menu
        window.bind("<Button-1>", lambda event: context_menu.unpost() or dropdown.unpost())
        window.bind("<Button-3>", lambda event: context_menu.unpost() or dropdown.unpost())



button_file = Button(window, text="Select File", command=select_file)
button_file.pack(pady=10)
file_label = Label(window, text="No file selected")
file_label.pack(pady=5)

var = StringVar(window)
var.set(option_list[0])
dropdown = OptionMenu(window, var, *option_list)
dropdown.pack()

button_run = Button(window, text="Convert", padx=70, command=run_script)
button_run.pack()
pb = Progressbar(
    window,
    orient='horizontal',
    mode='determinate',
    length=280
)
pb.pack(pady=20)
value_label = Label(window, text="0%")
value_label.pack()
result_tree = Treeview(window, height=1)
result_tree['columns'] = ('Total', 'Success Count', 'Error Count')
result_tree.heading('#0', text='Data')
result_tree.column('#0', anchor='center', width=100)
result_tree.heading('Total', text='Total')
result_tree.column('Total', anchor='center', width=100)
result_tree.heading('Success Count', text='Success Count')
result_tree.column('Success Count', anchor='center', width=120)
result_tree.heading('Error Count', text='Error Count')
result_tree.column('Error Count', anchor='center', width=100)
result_tree.pack(fill='both', expand=False)

error_tree = Treeview(window)
error_tree['columns'] = ('CSV Field', 'DBF Field', 'Error Message')
error_tree.heading('#0', text='Row')
error_tree.column('#0', anchor='center', width=80)
error_tree.heading('CSV Field', text='CSV Field')
error_tree.column('CSV Field', anchor='center', width=120)
error_tree.heading('DBF Field', text='DBF Field')
error_tree.column('DBF Field', anchor='center', width=120)
error_tree.heading('Error Message', text='Error Message')
error_tree.column('Error Message', anchor='center', width=220)
error_tree.pack(fill='both', expand=True)

window.mainloop()

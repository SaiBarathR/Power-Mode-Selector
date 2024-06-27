import subprocess
import re
import tkinter as tk
from tkinter import messagebox

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return result
    except Exception as e:
        print(f"An error occurred while running command: {command}")
        print(str(e))
        return None

def get_current_power_plan():
    result = run_command(['powercfg', '/GETACTIVESCHEME'])
    if result and result.returncode == 0:
        match = re.search(r'Power Scheme GUID: ([\w-]+)\s+\((.+)\)', result.stdout)
        if match:
            return match.group(1), match.group(2)
    return None, None

def get_all_power_plans():
    result = run_command(['powercfg', '/LIST'])
    if result and result.returncode == 0:
        plans = re.findall(r'Power Scheme GUID: ([\w-]+)\s+\((.+)\)', result.stdout)
        return plans
    return []

def set_power_plan(plan_guid):
    print(f"Attempting to set power plan to GUID: {plan_guid}")
    result = run_command(['powercfg', '/SETACTIVE', plan_guid])
    if result and result.returncode == 0:
        return True
    else:
        if result:
            print(f"Failed to set power plan. Return code: {result.returncode}")
            print(f"Error: {result.stderr}")
        return False

def on_select_plan():
    selected_plan = plans_var.get()
    if selected_plan:
        selected_name, selected_guid = selected_plan.rsplit(" (GUID: ", 1)
        selected_guid = selected_guid.strip().rstrip(")")
        selected_name = selected_name.strip()
        print(f"Selected GUID: {selected_guid}")
        print(f"Selected Name: {selected_name}")
        if set_power_plan(selected_guid):
            messagebox.showinfo("Success", f"Successfully set the power plan to: {selected_name}")            
        else:
            messagebox.showerror("Error", "Failed to set the power plan.")
    else:
        messagebox.showerror("Error", "No power plan selected.")

app = tk.Tk()
app.title("Power Plan Manager")

current_guid, current_name = get_current_power_plan()

plans = get_all_power_plans()
if plans:
    plans_var = tk.StringVar(app)
    plans_options = [f"{name} (GUID: {guid})" for guid, name in plans]
    plans_menu = tk.OptionMenu(app, plans_var, *plans_options)
    plans_menu.pack(pady=20)
    if current_name and current_guid:
        plans_var.set(f"{current_name} (GUID: {current_guid})")
else:
    tk.Label(app, text="No power plans available.").pack(pady=10)

select_button = tk.Button(app, text="Select Power Plan", command=on_select_plan)
select_button.pack(pady=10)

app.mainloop()
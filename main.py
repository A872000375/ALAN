# !pip install tkinter
import tkinter as tk
from tkinter import ttk
import json
from os import path

FREQ_KEY = 'food_freq_var'
AMT_KEY = 'food_amt_var'
TEMP_KEY = 'tank_temp_var'

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
WINDOW_GEOMETRY = str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
LABEL_PADDING = (20, 5)
JSON_FILE_NAME = 'smart_tank_config.json'
json_config = None
JSON_FILE_DEFAULTS = {
    FREQ_KEY: '12',
    AMT_KEY: '1',
    TEMP_KEY: 70
}

CONVERSION_FACTORS = {
    FREQ_KEY: 1,
    AMT_KEY: 1,
    TEMP_KEY: 1
}

# Init of root/frame
root = tk.Tk()
root.title('Smart Fish Tank Control')
root.geometry(WINDOW_GEOMETRY)
root.resizable(False, False)
frame = ttk.Frame(root, height=575, width=375, borderwidth=10)
frame.grid(row=1, column=1)

# Tkinter Vars (do not move from here)
# Must be below root init but above json loading
# Food Frequency Var
food_freq_var = tk.StringVar()
# Food Amount Var
food_amt_var = tk.StringVar()
# Tank Temperature Var
tank_temp_var = tk.IntVar()


# When save_changes_btn is clicked, save current settings and make changes to PID process.
def save_changes_button():
    global tank_temp_var, food_freq_var, food_amt_var
    print('Saving changes')

    # Debug vars
    print('food_freq_var:', food_freq_var.get())
    print('food_amt_var:', food_amt_var.get())
    print('tank_temp_var:', tank_temp_var.get())


def load_json_config():
    global food_freq_var, food_amt_var, tank_temp_var, \
        json_config, JSON_FILE_DEFAULTS, JSON_FILE_NAME, \
        TEMP_KEY, FREQ_KEY, AMT_KEY
    # Check if JSON config file exists
    if path.exists(JSON_FILE_NAME):
        # Read JSON config file
        with open(JSON_FILE_NAME, 'r') as file:
            json_config = json.loads(file.read())
            print('JSON Config File Found:', json_config)
    else:
        # Initialize JSON config file
        with open(JSON_FILE_NAME, 'w') as file:
            json_str = json.dumps(JSON_FILE_DEFAULTS)
            file.write(json_str)
            print('Initializing JSON Config File.')
        json_config = JSON_FILE_DEFAULTS

    # Load JSON Configs into Vars
    food_freq_var.set(json_config.get(FREQ_KEY))
    food_amt_var.set(json_config.get(AMT_KEY))
    temp_int = JSON_FILE_DEFAULTS[TEMP_KEY]
    try:
        temp_int = int(json_config.get(TEMP_KEY))
    except ValueError as e:
        print('Configuration file has been incorrectly altered. Setting Tank Temperature to default value.')
        json_config[TEMP_KEY] = JSON_FILE_DEFAULTS[TEMP_KEY]
        save_json_config()

    tank_temp_var.set(temp_int)


def save_json_config():
    global food_freq_var, food_amt_var, tank_temp_var, \
        json_config, JSON_FILE_DEFAULTS, JSON_FILE_NAME, \
        TEMP_KEY, FREQ_KEY, AMT_KEY

load_json_config()

# FOOD FREQUENCY

# Food Frequency Label
food_freq_lbl = ttk.Label(frame, text="Food Frequency (# Hours):", padding=LABEL_PADDING, justify=tk.RIGHT)
food_freq_lbl.grid(row=2, column=1, sticky=tk.E)
# Food Frequency Entry
food_freq_ent = ttk.Entry(frame, width=10, textvariable=food_freq_var)
food_freq_ent.grid(row=2, column=2, columnspan=2, sticky=tk.W)

# FOOD AMOUNT

# Food Amount Label
food_amt_lbl = ttk.Label(frame, text='Food Amount (# Units):', padding=LABEL_PADDING, justify=tk.RIGHT)
food_amt_lbl.grid(row=3, column=1, sticky=tk.E)
# Food Amount Entry
food_amt_ent = ttk.Entry(frame, width=4, textvariable=food_amt_var)
food_amt_ent.grid(row=3, column=2, columnspan=2, sticky=tk.W)

# TANK TEMPERATURE

# Tank Temperature Label
tank_temp_lbl = ttk.Label(frame, text='Tank Temperature (°F):', padding=LABEL_PADDING, justify=tk.RIGHT)
tank_temp_lbl.grid(row=4, column=1, sticky=tk.E)
# Tank Temperature Slider (Scale)
# Note: Fish usually live in water between 55F and 85F
tank_temp_scl = ttk.LabeledScale(frame, variable=tank_temp_var, from_=55, to=85)
tank_temp_scl.grid(row=4, column=2, sticky=tk.W)

# Save Changes Button
save_changes_btn = ttk.Button(frame, text='Save Changes', command=save_changes_button, width=50)
save_changes_btn.grid(row=100, column=1, columnspan=4, sticky=tk.W)

# Start Program
root.mainloop()

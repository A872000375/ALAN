#!/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install tkinter


# In[2]:


import tkinter as tk
from tkinter import ttk


# In[3]:


WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
WINDOW_GEOMETRY = str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)


# In[4]:


root = tk.Tk()
root.title('Smart Fish Tank Control')
root.geometry(WINDOW_GEOMETRY)
root.resizable(False, False)
frame = ttk.Frame(root, height=575, width=375, borderwidth=10)
frame.grid(row=1, column=1)
# In[5]:




# In[6]:


# When save_changes_btn is clicked, save current settings and make changes to PID process.
def save_changes_button():
    print('Saving changes')

food_freq_lbl = ttk.Label(frame, text="Food Frequency (# Hours):", padding=(20,5))
food_freq_lbl.grid(row=2, column=1)
food_freq_ent = ttk.Entry(frame, width=10)
food_freq_ent.grid(row=2, column=2, columnspan=2)

save_changes_btn = ttk.Button(frame, text='Save Changes', command=save_changes_button, width=50)
save_changes_btn.grid(row=3, column=1, columnspan=4)


# In[ ]:





# In[9]:


root.mainloop()


# In[ ]:





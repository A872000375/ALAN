from tkinter import *

def main():
    loginScreen()

def login():
    # Checks for USER/PASS in DB
    """
        Returns back three states
        State #1: Incorrect USER or Pass --> Pop up
        State #2: Not in registry --> Pop up
        State #3: Successfully login --> Takes to screen2
    """
    return 0

def register():
    # Creates a new window for registeration screen and connect this to a SQL DB which will store USER/PASS --> in screen1
    return 0

def loginScreen():
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 600
    WINDOW_GEOMETRY = str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
    screen = Tk()
    screen.geometry(WINDOW_GEOMETRY)
    screen.title("Smart Fish Tank")

    # Grid Placement System (Working based on columns without presetting rows) -- Weight how man columns it holds
    screen.columnconfigure(0, weight=4)
    screen.columnconfigure(1, weight=4)
    screen.columnconfigure(2, weight=4)
    screen.columnconfigure(3, weight=4)

    # Creation of Widgets
    title = Label(text="Smart Fish Tank", bg="lightblue",
                 font=("Ariel",30))
    loginLabel = Label(text="Welcome to SFT", font=("Ariel", 16))
    userLabel = Label(text="Username")
    passLabel = Label(text="Password")
    userEntry = Entry()
    passEntry = Entry()
    loginButton = Button(screen, text="Login", command=login)
    registerButton = Button(screen, text="Register", command=register)
    exitButton = Button(screen, text="Exit", command=quit)

    # Pushing the Widgets
    title.grid(sticky='ew', column=0, row=0, columnspan=4, ipady=15, ipadx=7.5)
    loginLabel.grid(sticky='ew', column=1, row=1, pady=15, columnspan=2)
    userLabel.grid(sticky='ew', column=0, row=2, columnspan=2, pady=10)
    userEntry.grid(sticky='ew', column=2, row=2, pady=10)
    passLabel.grid(sticky='ew', column=0, row=3, columnspan=2, pady=10)
    passEntry.grid(sticky='ew', column=2, row=3, pady=10)
    loginButton.grid(sticky='ew', column=1, row=4, columnspan=2, pady=10)
    registerButton.grid(sticky='ew', column=1, row=5, columnspan=2, pady=10)
    exitButton.grid(sticky='ew', column=2, row=6, pady=40)

    screen.mainloop()

if __name__ == "__main__":
    main()
from tkinter import *
from tkinter import messagebox
import socket

from PIL import Image, ImageTk
import tank_client, tank_trouble_globals, Game_Objects, threading

win = Tk()

def on_closing():
    global run
    tank_client.s.close()
    run = False

def handle():
    global win
    global run
    run = True
    while run:
        try:
            s = tank_client.s
            data = s.recv(4096)
            if not data:
                break
            data = tank_client.f.decrypt(data)
            data = data.decode()
            dict = tank_client.convert_raw(data)[0]
            if dict["action"] == "cr":
                tank = Game_Objects.Tank(float(dict["x"]), float(dict["y"]),dict["image"] , dict["name"])
                tank_trouble_globals.init_tank(dict["name"], tank)
                tank_trouble_globals.MY_NAME = dict["name"]
                tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].coins = int(dict["coins"])
                tank_client.sec = dict["sec"]
                print(tank_client.sec)
                tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].coins = int(dict["coins"])
                run = False
                return
        except:
            continue


def loginWindow():
    #window
    global win
    win.geometry('500x300')
    win.resizable(0,0)

    win.title('Tank Trouble')
    win.configure(bg = "#27395E")

    #background image
    img = Image.open("assets/UI Background.png").resize((500,300), Image.ANTIALIAS)
    bgImage = ImageTk.PhotoImage(img)
    background_label = Label(win, image=bgImage).place(x=0, y=0)

    #label
    label = Label(win, text = "WELCOME TO TANK-TROUBLE", font = ("Arial", 20), bg = "#27395E", fg = "white", height=2).place(x = 50, y = 2)

    #username label and text entry box
    usernameLabel = Label(win, text="User Name", fg="#211633", bg = "#1D5F85", font = ("Courier", 20)).place(x=100, y=150)
    username = StringVar()
    usernameEntry = Entry(win, textvariable=username).place(x=110, y=200)

    #password label and password entry box
    passwordLabel = Label(win,text="Password",fg="#211633", bg = "#1D5F85" , font = ("Courier", 20)).place(x=255, y=150)
    password = StringVar()
    passwordEntry = Entry(win, textvariable=password, show='').place(x=260, y=200)

    #ip label and ip entry box
    ip = StringVar()
    ipEntry = Entry(win, textvariable=ip, show='').place(x=250, y=100)
    #login button
    loginButton = Button(win, text="Login", command=lambda: tank_client.login(username.get(), password.get(), ip.get()), bg = "#622E51").place(x=150, y=230, width=70, height=40)
    registerButton = Button(win, text="Register", command=lambda: tank_client.sign_up(username.get(), password.get(), ip.get()), bg = "#622E51").place(x=270, y=230, width=70, height=40)
    t = threading.Thread(target=handle)
    t.start()
    win.protocol("WM_DELETE_WINDOW", on_closing)
    global run
    while run:
        win.update_idletasks()
        win.update()
    win.destroy()
    tank_client.reset_socket()
    return username.get()


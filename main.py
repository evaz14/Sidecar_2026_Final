import time
import tkinter as tk
from tkinter import font as tkfont

import wpilib
import threading

from wpilib import DriverStation

from networktables import NetworkTables
from open_gopro import WirelessGoPro

# global variables
secondsLeftTeleop = 0
secondsLeftAuton = 0
data = ""

# gopro (idk about this part)

gopro = WirelessGoPro()

def goProStartRecording():
    with gopro:
        gopro.http_command.set_shutter(shutter = WirelessGoPro.Shutter.ON)

def goProStopRecording():
    with gopro:
        gopro.http_command.set_shutter(shutter = WirelessGoPro.Shutter.OFF)

# visual gui
window = tk.Tk() # create window
window.geometry("1300x800") # size
window.title("Sidecar") # title

# font
stylizedFont = tkfont.Font()

# enabled/disabled
isEnabledStatusLabel = tk.Label(
    window,
    text = 'DISABLED', # defaulted to DISABLED
    font = ("Segoe UI", 50, 'bold'),
    bg = "red",
    fg = "black"
)
isEnabledStatusLabel.place(x=350, y=25, height=200, width=600)

# timer in game
GameTimeLeftLabel = tk.Label(
    window,
    text = '00:00', # defaulted to 00:00
    font = ("Segoe UI", 50, 'bold'),
    bg = "light blue",
    fg = "black"
)
GameTimeLeftLabel.place(x=350, y=275, height=200, width=600)

# autnomous/teleoperated
GamePeriodLabel = tk.Label(
    window,
    text = 'N/A', # defaulted to N/A
    font = ("Segoe UI", 50, 'bold'),
    bg = "light blue",
    fg = "black"
)
GamePeriodLabel.place(x=25, y=525, height=200, width=600)

# shift of the game, transition, scoring, etc.
GameShiftLabel = tk.Label(
    window,
    text = 'N/A', # defaulted to N/A
    font = ("Segoe UI", 50, 'bold'),
    bg = "light blue",
    fg = "black"
)
GameShiftLabel.place(x=650, y=525, height=200, width=600)

# networktables
def connectionListener(connected, info):
    print(info, "; Connected=%s" % connected)

def timerCountdownTeleop():
    global secondsLeftTeleop
    secondsLeftTeleop = 140
    while secondsLeftTeleop >= 0:
        time.sleep(1)
        secondsLeftTeleop -= 1

def timerCountdownAuton():
    global secondsLeftAuton
    secondsLeftAuton = 20
    while secondsLeftAuton >= 0:
        time.sleep(1)
        secondsLeftAuton -= 1

# enabled/disabled, auton/teleop
def valueChanged(table, key, value, isNew): 
    global data, secondsLeftTeleop, secondsLeftAuton
    if key == "FMSControlData":
        if value == 32:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red")
            GamePeriodLabel.config(text = "TELEOP")
            threading.Thread(target=goProStopRecording, daemon=True).start()
        elif value == 33:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green")
            GamePeriodLabel.config(text = "TELEOP")
            threading.Thread(target=timerCountdownTeleop, daemon=True).start()
            threading.Thread(target=goProStartRecording, daemon=True).start()
        elif value == 34:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red")
            GamePeriodLabel.config(text = "AUTON")
            threading.Thread(target=goProStopRecording, daemon=True).start()
        elif value == 35:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green")
            GamePeriodLabel.config(text = "AUTON")
            threading.Thread(target=timerCountdownAuton, daemon=True).start()
            threading.Thread(target=goProStartRecording, daemon=True).start()
    
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))

def periodic():
    global data
    data = wpilib.DriverStation.getGameSpecificMessage()
    alliance = wpilib.DriverStation.getAlliance()
    
    GameShiftLabel.config(bg = "light blue") # may cause flicker, change if needed

    if wpilib.DriverStation.isTeleop():
        if secondsLeftTeleop > 130:
            GameShiftLabel.config(text = "Transition Period", bg = "light blue")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 130))
        elif 105 < secondsLeftTeleop <= 130:
            GameShiftLabel.config(text = "Shift 1")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 105))
            if data == "R" and alliance == wpilib.DriverStation.Alliance.kBlue or data == "B" and alliance == wpilib.DriverStation.Alliance.kRed:
                        GameShiftLabel.config(bg = "green", fg = "black")
        elif 80 < secondsLeftTeleop <= 105:
            GameShiftLabel.config(text = "Shift 2")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 80))
            if data == "R" and alliance == wpilib.DriverStation.Alliance.kRed or data == "B" and alliance == wpilib.DriverStation.Alliance.kBlue:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 55 < secondsLeftTeleop <= 80:
            GameShiftLabel.config(text = "Shift 3")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 55))
            if data == "R" and alliance == wpilib.DriverStation.Alliance.kBlue or data == "B" and alliance == wpilib.DriverStation.Alliance.kRed:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 30 < secondsLeftTeleop <= 55:
            GameShiftLabel.config(text = "Shift 4")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 30))
            if data == "R" and alliance == wpilib.DriverStation.Alliance.kRed or data == "B" and alliance == wpilib.DriverStation.Alliance.kBlue:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 0 <= secondsLeftTeleop <= 30:
            GameShiftLabel.config(text = "Endgame", bg = "light blue", fg = "black")
            GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime()))
    elif wpilib.DriverStation.isAuton():
            GameShiftLabel.config(text = "Autonomous Period")
            GameTimeLeftLabel.config(text = str(secondsLeftAuton))

    window.after(200, periodic)
    

# Set the RoboRIO IP address
ip = "172.22.11.2"

NetworkTables.initialize(server=ip)
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

nt = NetworkTables.getTable("FMSInfo")
nt.addEntryListener(valueChanged)

time.sleep(1)

if NetworkTables.isConnected():
    print("Connected to NetworkTables server")
else:
    print("Failed to connect to NetworkTables server")

periodic()
window.mainloop()
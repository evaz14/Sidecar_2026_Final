import time
import tkinter as tk
import sys
from tkinter import font as tkfont

import wpilib

from wpilib import DriverStation

from networktables import NetworkTables
from open_gopro import WirelessGoPro

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

# main method
def valueChanged(table, key, value, isNew): 
    global isEnabledStatus
    
    if key == "FMSControlData":
        if value == 32:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red", fg = "black")
            GamePeriodLabel.config(text = "TELEOP")
        if value == 33:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green", fg = "black")
            GamePeriodLabel.config(text = "TELEOP")
        if value == 34:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red", fg = "black")
            GamePeriodLabel.config(text = "AUTON")
        if value == 35:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green", fg = "black")
            GamePeriodLabel.config(text = "AUTON")
    
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))



def periodic(intervalSeconds):
    while True:
        if wpilib.DriverStation.isTeleop():
                if wpilib.DriverStation.getMatchTime() > 130:
                    GameShiftLabel.config(text = "Transition Period")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime()))
                if 130 <= wpilib.DriverStation.getMatchTime() > 105:
                    GameShiftLabel.config(text = "Shift 1")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime() - 10))
                if 105 <= wpilib.DriverStation.getMatchTime() > 80:
                    GameShiftLabel.config(text = "Shift 2")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime() - 35))
                if 80 <= wpilib.DriverStation.getMatchTime() > 55:
                    GameShiftLabel.config(text = "Shift 3")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime() - 60))
                if 55 <= wpilib.DriverStation.getMatchTime() > 30:
                    GameShiftLabel.config(text = "Shift 4")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime() - 85))
                if 30 >= wpilib.DriverStation.getMatchTime() >= 0:
                    GameShiftLabel.config(text = "Endgame")
                    GameTimeLeftLabel.config(text = str(wpilib.DriverStation.getMatchTime() - 110))

        time.sleep(intervalSeconds)
    

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

window.mainloop()
periodic(1)


# enable teleop = 33
# disabled auton = 34

# disabled teleop = 32
# enabled auton = 35

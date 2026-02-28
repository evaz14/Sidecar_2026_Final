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
isTeleopStatus = False

# gopro (idk about this part)

# gopro = WirelessGoPro()

# def goProStartRecording():
#     with gopro:
#         gopro.http_command.set_shutter(shutter = WirelessGoPro.Shutter.ON)

# def goProStopRecording():
#     with gopro:
#         gopro.http_command.set_shutter(shutter = WirelessGoPro.Shutter.OFF)

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

# timer for teleoperated
def timerCountdownTeleop():
    global secondsLeftTeleop
    secondsLeftTeleop = 140
    while secondsLeftTeleop > 0:
        time.sleep(1)
        secondsLeftTeleop -= 1

# timer for autonomous
def timerCountdownAuton():
    global secondsLeftAuton
    secondsLeftAuton = 20
    while secondsLeftAuton > 0:
        time.sleep(1)
        secondsLeftAuton -= 1
    print(secondsLeftAuton)

# enabled/disabled, auton/teleop
def valueChanged(table, key, value, isNew): 
    global secondsLeftTeleop, secondsLeftAuton, isTeleopStatus
    global winner, alliance

    if key == "GameSpecificMessage":
        winner = value

    if key == "IsRedAlliance":
        alliance = value

    if key == "FMSControlData":
        if value == 32:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red")
            GamePeriodLabel.config(text = "TELEOP")
            isTeleopStatus = True
            secondsLeftTeleop = 0
            secondsLeftAuton = 0
            # threading.Thread(target=goProStopRecording, daemon=True).start()
        elif value == 33:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green")
            GamePeriodLabel.config(text = "TELEOP")
            isTeleopStatus = True
            threading.Thread(target=timerCountdownTeleop, daemon=True).start()
            # threading.Thread(target=goProStartRecording, daemon=True).start()
        elif value == 34:
            isEnabledStatusLabel.config(text = "DISABLED", bg = "red")
            GamePeriodLabel.config(text = "AUTON")
            isTeleopStatus = False
            secondsLeftTeleop = 0
            secondsLeftAuton = 0
            # threading.Thread(target=goProStopRecording, daemon=True).start()
        elif value == 35:
            isEnabledStatusLabel.config(text = "ENABLED", bg = "green")
            GamePeriodLabel.config(text = "AUTON")
            isTeleopStatus = False
            threading.Thread(target=timerCountdownAuton, daemon=True).start()
            # threading.Thread(target=goProStartRecording, daemon=True).start()
    
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))

# Set the RoboRIO IP address
ip = "172.22.11.2"

NetworkTables.initialize(server=ip)
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

nt = NetworkTables.getTable("FMSInfo")
nt.addEntryListener(valueChanged)

winnerEntry = nt.getEntry("GameSpecificMessage")
winner = winnerEntry.getString("")

allianceEntry = nt.getEntry("isRedAlliance")
alliance = allianceEntry.getBoolean(False)

time.sleep(1)

if NetworkTables.isConnected():
    print("Connected to NetworkTables server")
else:
    print("Failed to connect to NetworkTables server")

# timers, game shift
def periodic():

    GameShiftLabel.config(bg = "light blue") # may cause flicker, change if needed

    if isTeleopStatus:
        if secondsLeftTeleop > 130:
            GameShiftLabel.config(text = "Transition Period", bg = "light blue")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 130))
        elif 105 < secondsLeftTeleop <= 130:
            GameShiftLabel.config(text = "Shift 1")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 105))
            if winner == "R" and alliance == False or winner == "B" and alliance == True:
                        GameShiftLabel.config(bg = "green", fg = "black")
        elif 80 < secondsLeftTeleop <= 105:
            GameShiftLabel.config(text = "Shift 2")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 80))
            if winner == "R" and alliance == True or winner == "B" and alliance == False:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 55 < secondsLeftTeleop <= 80:
            GameShiftLabel.config(text = "Shift 3")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 55))
            if winner == "R" and alliance == False or winner == "B" and alliance == True:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 30 < secondsLeftTeleop <= 55:
            GameShiftLabel.config(text = "Shift 4")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop - 30))
            if winner == "R" and alliance == True or winner == "B" and alliance == False:
                GameShiftLabel.config(bg = "green", fg = "black")
        elif 0 <= secondsLeftTeleop <= 30:
            GameShiftLabel.config(text = "Endgame", bg = "light blue", fg = "black")
            GameTimeLeftLabel.config(text = str(secondsLeftTeleop))
    else:
        if secondsLeftAuton >= 0:
            GameShiftLabel.config(text = "Autonomous", bg = "light blue", fg = "black")
            GameTimeLeftLabel.config(text = str(secondsLeftAuton))

    window.after(200, periodic)

periodic()
window.mainloop()
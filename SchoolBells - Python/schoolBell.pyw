import time, json
from tkinter import *
from arduinocom import Arduino
import os.path
from _collections import deque
from datetime import datetime, date
from time import mktime
from _datetime import MINYEAR

PORT = "COM1"
BAUD = 9600

class UI:
    def __init__(self, master):
        self.root = master
        self.scheduler = ScheduleSupervisor()
               
        #Attach buttons to main frame
        self.inWindowFrame = Frame(master)
        self.inWindowFrame.pack(fill=BOTH, expand=1)
        self.buttonSchedule1 = Button(self.inWindowFrame, text="Разписание 1\n(45 min учебен час)", command=lambda:self.__activateProcess(1))
        self.buttonSchedule1.grid(row=0, column=0, padx=25, pady=25)
        self.buttonSchedule2 = Button(self.inWindowFrame, text="Разписание 2\n(40 min учебен час)", command=lambda:self.__activateProcess(2))
        self.buttonSchedule2.grid(row=0, column=1, padx=25, pady=25)
        self.buttonSchedule3 = Button(self.inWindowFrame, text="Разпределение 3\n(45 min учебен час)", command=lambda:self.__activateProcess(3))
        self.buttonSchedule3.grid(row=0, column=2, padx=25, pady=25)
        self.buttonSchedule4 = Button(self.inWindowFrame, text="Разпределение 4\n(40 min учебен час)", command=lambda:self.__activateProcess(4))
        self.buttonSchedule4.grid(row=1, column=0, padx=25, pady=25)
        self.buttonSchedule5 = Button(self.inWindowFrame, text="Разпределение 5\n(30 min учебен час)", command=lambda:self.__activateProcess(5))
        self.buttonSchedule5.grid(row=1, column=1, padx=25, pady=25)
        self.buttonSchedule6 = Button(self.inWindowFrame, text="Разпределение 6\n(50 min учебен час)", command=lambda:self.__activateProcess(6))
        self.buttonSchedule6.grid(row=1, column=2)
        self.statusMessage = Label(self.inWindowFrame, text="", fg="green", font=("Helvetica", 12))
        self.statusMessage.grid(row=2, column=0, columnspan=3, sticky=W)
        
        self.statusMessageProcessId = ""
        self.__checkComPort()

    def __activateProcess(self, scheduleId):
        self.scheduler.loadScheduleNumber(scheduleId)
        if not self.scheduler.isCommunicationOnGoing():
            return
        self.backgroundProcessId = self.root.after(1, self.__proceedProcess)
        self.__updateStatusMessage(True)
        self.__disableAllButtons()
    def __checkComPort(self):
        if not self.scheduler.isInitialSettingsApplied():
            self.top = Toplevel()
            self.top.title("Изберете COM порт")
            self.label1 = Label(self.top, text="Въведете номера на COM порта (вижте в 'Device Manager')", height=0, width=50)
            self.label1.pack()
            self.textEntry = Entry(self.top)
            self.textEntry.pack()
            self.button = Button(self.top, text="Ok", command=self.__setComPort)
            self.button.pack()
        else:
            pass
    def __setComPort(self):
        self.scheduler.setComPort(self.textEntry.get())
        self.top.destroy()
        pass
    def __proceedProcess(self):
        self.scheduler.checkTime()
        if self.scheduler.isScheduleComplited():
            self.root.after_cancel(self.statusMessageProcessId)
            self.__updateStatusMessage(False)
            print("Schedule complited!")
            self.__enableAllButtons()
            return
        else:
            self.backgroundProcessId = self.root.after(10, self.__proceedProcess)
            
    def __updateStatusMessage(self, isEnabled):
        if not isEnabled:
            self.statusMessage["text"] = "Учебните занятия са приключили!"
            self.statusMessage["fg"] = "red"
            return
        
        # Get the current message
        currentStatus = self.statusMessage["text"]
        currentStatus
        if currentStatus.endswith("...") or len(currentStatus) is 0: 
            currentStatus = "Учебните занятия са започнали"
        else: 
            currentStatus += "."
        
        # Update the message
        self.statusMessage["text"] = currentStatus
        
        # After 1 second, update the status
        self.statusMessageProcessId = self.root.after(250,lambda: self.__updateStatusMessage(True))
        
    def onExit(self):
        print("Closing application")
        self.scheduler.releaseResourses()
        root.destroy()
    def __disableAllButtons(self):
        self.buttonSchedule1["state"] = DISABLED
        self.buttonSchedule2["state"] = DISABLED
        self.buttonSchedule3["state"] = DISABLED
        self.buttonSchedule4["state"] = DISABLED
        self.buttonSchedule5["state"] = DISABLED
        self.buttonSchedule6["state"] = DISABLED
    def __enableAllButtons(self):
        self.buttonSchedule1["state"] = NORMAL
        self.buttonSchedule2["state"] = NORMAL
        self.buttonSchedule3["state"] = NORMAL
        self.buttonSchedule4["state"] = NORMAL
        self.buttonSchedule5["state"] = NORMAL
        self.buttonSchedule6["state"] = NORMAL
    
class ScheduleSupervisor:
    def __init__(self):
        self.listOfScheduleElements = deque()
        self.arduino = Arduino(PORT, BAUD)
        if self.isInitialSettingsApplied():
            self.__loadComSettings()
            self.__initialiseCommunication()
    def isCommunicationOnGoing(self):
        return self.arduino.connected  
    def loadScheduleNumber(self, number):
        #Check is the number from 1 to 6
        if number < 1 or number > 6:
            return False
        #Check if file exists and if its empty
        scheduleFileName = "Schedule"+str(number)+".txt"
        if not os.path.isfile(scheduleFileName) or os.path.getsize(scheduleFileName) < 0:
            return False
        scheduleInputFile = open(scheduleFileName, "r")
        ringTimesArray = ""
        for line in scheduleInputFile:
            ringTimesArray = str(line).rstrip().split(sep="-", maxsplit=1)
            timeFormat = '%H:%M:%S'
            startTimeObject = datetime.strptime(ringTimesArray[0], timeFormat)
            stopTimeObject = datetime.strptime(ringTimesArray[1], timeFormat)
            elementEnableBell = ScheduleElement(startTimeObject, True)
            elementDisableBell = ScheduleElement(stopTimeObject, False)
            self.listOfScheduleElements.append(elementEnableBell)
            self.listOfScheduleElements.append(elementDisableBell)
        scheduleInputFile.close() 
    def releaseResourses(self):
        #disconnect arduino board serial communication
        self.arduino.stop_bell()
        self.arduino.stop_communication()
        pass
    def isInitialSettingsApplied(self):
        settingsFileName = "settings.cfg"
        if not os.path.isfile(settingsFileName) or os.path.getsize(settingsFileName) < 0:
            return False
        else:
            return True
    def setComPort(self, comNumber):
        settingsFile = open("settings.cfg", 'w')
        settingsFile.write(str(comNumber))
        self.arduino.set_comport_str(comNumber)
        self.__initialiseCommunication()
    def __initialiseCommunication(self):
        #start serial com by invocing arduinoBoard object method
        self.arduino.start_communication()

    def __loadComSettings(self):
        #if COMport settings exists, this method loads them from file
        settingsFile = open("settings.cfg", 'r')
        self.arduino.set_comport_str(settingsFile.readline())
        settingsFile.close()
    def __popExpiredElements(self):
        bellNewState = False
        expiredElementsCount = 0
        for element in self.listOfScheduleElements:
            today = datetime.today()
            today = today.replace(year=element.time.year, month=element.time.month, day=element.time.day)
            deltaTime = element.time - today
            if deltaTime.total_seconds() <= 0:  
                bellNewState = element.state
                expiredElementsCount+=1
            else:
                break
        for i in range(0 , expiredElementsCount):
            self.listOfScheduleElements.popleft()
        if expiredElementsCount > 0:
            return bellNewState
        return self.arduino.bellState
    def checkTime(self):
        if len(self.listOfScheduleElements) is 0:
            return
        isRingingTime = self.__popExpiredElements()
        
        if isRingingTime is self.arduino.bellState:
            return
                
        if isRingingTime:
            print("Ringing at " + str(datetime.now().time()))
            self.arduino.ring_bell()
        else:
            print("Stop at " + str(datetime.now().time()))
            self.arduino.stop_bell()   
    def isScheduleComplited(self):
        if len(self.listOfScheduleElements) is 0:
            return True
        else:
            return False
    
    
class ScheduleElement:
    def __init__(self, dateTime, state):
        self.queue = deque()
        self.time = dateTime
        self.state = state
    def __repr__(self):
        return "<ScheduleElement time:%s state:%s >" % (str(self.time), self.state)
    def __str__(self):
        return "Time: " + str(self.time) + "State: " + self.state

    
root = Tk()
root.wm_title("School Bells")
root.resizable(width=FALSE, height=FALSE)
root.wm_iconbitmap(bitmap = "bell_icon.ico")

application = UI(root)

#Used to set the window in center
root.withdraw()
root.update_idletasks()  # Update "requested size" from geometry manager

x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
root.geometry("+%d+%d" % (x, y))

# This seems to draw the window frame immediately, so only call deiconify()
# after setting correct window position
root.deiconify()

root.protocol('WM_DELETE_WINDOW', application.onExit)

root.mainloop()

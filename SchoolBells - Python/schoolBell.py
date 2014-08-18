import time, json
from tkinter import *
from arduinocom import Arduino
import os.path
from _collections import deque
from datetime import datetime, date
from time import mktime
from _datetime import MINYEAR

PORT = "COM44"
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
        
    def __activateProcess(self, scheduleId):
        self.scheduler.loadScheduleNumber(scheduleId)
        self.backgroundProcessId = self.root.after(1, self.__proceedProcess)

    def __proceedProcess(self):
        self.scheduler.checkTime()
        if self.scheduler.isScheduleComplited():
            print("Schedule complited!")
            return
        else:
            self.backgroundProcessId = self.root.after(10, self.__proceedProcess)
        
    def onExit(self):
        print("Closing application")
        '''
        f = open("settings.cfg", 'w')
	    max_points = int(self.arduino.max_points)
        com_port = int(self.arduino.get_comport())
        json.dump(json.dumps([["comport",com_port],["maxpoints",max_points]]), f)
        f.flush()
        f.close() 
        '''

        self.scheduler.releaseResourses()
        root.destroy()

class ScheduleSupervisor:
    def __init__(self):
        self.listOfScheduleElements = deque()
        self.arduino = Arduino(PORT, BAUD)
        # self.arduinoPort = PORT
        #To Do:Read settings for com port 
        pass
    def loadScheduleNumber(self, number):
        #Check is the number from 1 to 6
        if number < 1 or number > 6:
            return False
        #Check if file exists and if its empty
        scheduleFileName = "Програма"+str(number)+".txt"
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
           
            #deltaTime =  stopTimeObject - today
            #print(deltaTime.days)
            #print(deltaTime.total_seconds())
            #if deltaTime.days < 0 or deltaTime.seconds:
            #    pass
            #print(deltaTime.seconds - deltaTime.max.seconds)
            #print(deltaTime.days)
           
            #startScheduleElement = ScheduleElement()
            #stopScheduleElement = ScheduleElement()
            #self.listOfScheduleElements.append()
        scheduleInputFile.close() 
    def releaseResourses(self):
        #disconnect arduino board serial communication
        self.arduino.stop_bell()
        self.arduino.stop_communication()
        pass
    def isInitialSettingsApplied(self):
        #check for COMport setting file
        pass
    def setComSettings(self, com):
        pass
    def __checkCommunicationStatus(self):
        #checking is arduino connected by serial
        pass
    def __initialiseCommunication(self):
        #start serial com by invocing arduinoBoard object method
        pass
    def __loadComSettings(self):
        #if COMport settings exists, this method loads them from file
        pass
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
    '''
	def deserialize_settings(self):
        print("deser")
        try:
            f = open("settings.cfg", 'r')
        except FileNotFoundError:
            f = open("settings.cfg", 'w')
            json.dump(json.dumps([["comport",60],["maxpoints",10]]), f)
            f.flush()
            f.close()
        
        f = open("settings.cfg", 'r')
        try:
            deser = json.load(f)
        except ValueError:
            f = open("settings.cfg", 'w')
            json.dump(json.dumps([["comport",60],["maxpoints",10]]), f)
            f.flush()
        f = open("settings.cfg", 'r')
        deser = json.load(f)
        f.close()
        return json.loads(deser)      
	def set_comport_to_arduino(self, event):
        try:
            float(com_port)
            if int(comport):
                raise ValueError
        except ValueError:
            self.comport_entry.delete(0, END)
            return False
        
        self.arduino.set_comport(int(com_port))
        print("Arduino comport: " + com_port)
        return True 
        '''
    
    
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
root.wm_title("School Bell")
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

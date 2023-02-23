from tkinter import *
from tkinter.ttk import *
from pyModbusTCP.client import *

class NumPad(Frame):


    def __init__(self, master, confFileName: str):
        super().__init__(master)

        for idx_row in range(12):
            Grid.rowconfigure(self, idx_row, weight=1)

        for idx_col in range(8):
            Grid.columnconfigure(self, idx_col, weight=1)

        self.setpoint = StringVar()
        self.power    = StringVar()

        self.refreshRate = 1500 # ms

        self.inverter_name = None
        self.ip_addres     = None
        self.port          = None
        self.maxpower      = None

        self._Conf(confFileName)

        # Modbus client
        self.modbus = ModbusClient(host=self.ip_addres, port=self.port, timeout=0.5, auto_open=True, auto_close=True)

        # Styles
        # ------

        # Commonstyle
        self.font_bold    = ('Helvetica', 16, 'bold')
        self.font_regular = ('Helvetica', 16,)
        s = Style()        
        s.configure('.', font=self.font_bold)

        
        # Widgets
        # -------
        # Row 0
        self.label_invertername = Label(self, text=self.inverter_name, font=self.font_regular)
        self.label_invertername.grid(row=0, column=0, columnspan=8, sticky=EW)

        # Row 1
        self.label_realpower = Label(self, text='Real Power', font=self.font_regular)
        self.label_realpower.grid(row=1, column=0, columnspan=4, sticky=W)
        
        self.label_setpoint = Label(self, text='Setpoint Watts', font=self.font_regular)
        self.label_setpoint.grid(row=1, column=4, columnspan=4, sticky=W)

        # Row 2
        self.label_measpower = Label(self, text='INITIATE COMMS', textvariable=self.power)
        self.label_measpower.grid(row=2, column=0, columnspan=4, sticky=W)
        self.label_measpower.after(1000, self.ReadPower)

        self.entry_setpoint = Entry(self, font = self.font_bold, textvariable = self.setpoint)
        self.entry_setpoint.grid(row=2, column=4, columnspan=4, sticky=EW)

        # Row 3,4
        self.btn_7 = Button(self, text='7', command=lambda : self.concatinate('7'))
        self.btn_7.grid(row=3, column=0, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_8 = Button(self, text='8', command=lambda : self.concatinate('8'))
        self.btn_8.grid(row=3, column=2, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_9 = Button(self, text='9', command=lambda : self.concatinate('9'))
        self.btn_9.grid(row=3, column=4, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_BS = Button(self, text='BS', command=self.BackSpace)
        self.btn_BS.grid(row=3, column=6, rowspan=2, columnspan=2, sticky=W+E+N+S)

        # Row 5,6
        self.btn_4 = Button(self, text='4', command=lambda : self.concatinate('4'))
        self.btn_4.grid(row=5, column=0, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_5 = Button(self, text='5', command=lambda : self.concatinate('5'))
        self.btn_5.grid(row=5, column=2, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_6 = Button(self, text='6', command=lambda : self.concatinate('6'))
        self.btn_6.grid(row=5, column=4, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_CLR = Button(self, text='CLR', command=self.Clear)
        self.btn_CLR.grid(row=5, column=6, rowspan=2, columnspan=2, sticky=W+E+N+S)

        # Row 7,8
        self.btn_1 = Button(self, text='1', command=lambda : self.concatinate('1'))
        self.btn_1.grid(row=7, column=0, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_2 = Button(self, text='2', command=lambda : self.concatinate('2'))
        self.btn_2.grid(row=7, column=2, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_3 = Button(self, text='3', command=lambda : self.concatinate('3'))
        self.btn_3.grid(row=7, column=4, rowspan=2, columnspan=2, sticky=W+E+N+S)

        self.btn_SET = Button(self, text='SET', command=self.WriteSetpoint)
        self.btn_SET.grid(row=7, column=6, rowspan=4, columnspan=2, sticky=W+E+N+S)

        # Row 9,10
        self.btn_0 = Button(self, text='0', command=lambda : self.concatinate('0'))
        self.btn_0.grid(row=9, column=0, rowspan=2, columnspan=4, sticky=W+E+N+S)

        self.btn_comma = Button(self, text=',', command=lambda : self.concatinate('.'))
        self.btn_comma.grid(row=9, column=4, rowspan=2, columnspan=2, sticky=W+E+N+S)

         # Row 11
        self.label_ip = Label(self, text='IP: '+self.ip_addres, font=self.font_regular)
        self.label_ip.grid(row=11, column=0, columnspan=8, sticky=W)   
   
    def concatinate(self, what: str):
        self.setpoint.set( self.setpoint.get() + what )

    def BackSpace(self):
        self.setpoint.set( self.setpoint.get()[0:-1] )

    def Clear(self):
        self.setpoint.set('')
    
    def WriteSetpoint(self):

        try:
            p = float(self.setpoint.get())
        except:
            self.setpoint.set('Invalid input!')
            return

        if p > self.maxpower:
            self.setpoint.set(f'Error! P > {self.maxpower}!')
            return

        setpoint = int(p/self.maxpower * 100 * 100) #Percents multiplied by 100, i.e. 50% = 5000
        print(f'The setpoint is {setpoint}')

        # Set the power register
        reg_addr = 40232
        success = self.modbus.write_single_register(reg_addr, setpoint)

        if success:
            print(f'[{self.inverter_name}] ', f'Power register set to {p/self.maxpower*100} %')
        else:
            print(f'[{self.inverter_name}] ', 'CONNECTION ERROR! Power register could not be set!')

        # Confirm the power setpoint
        reg_value = 1
        reg_addr = 40236
        success = self.modbus.write_single_register(reg_addr, reg_value)

        if success:
            print(f'[{self.inverter_name}] ', f'Setpoint confirmed')
        else:
            print(f'[{self.inverter_name}] ', 'CONNECTION ERROR! Setpoint could not be confirmed!')

        print('')

    def ReadPower(self):

        # reg_addr_p = 40083 # In the table is 40084
        # reg_addr_f = 40085 # In the table is 40086
        # reg_addr_q = 40089 # In the table is 40090
        # reg_addr_pf= 40091 # In the table is 40092

        power = self.modbus.read_holding_registers(40083, reg_nb=1)

        if power is not None:
            self.power.set('{} W  ({:05.2f} %)'.format(
                            int(power[0]/10),
                            power[0]/self.maxpower*10,
            ))
        else:
            self.power.set('CONNECTION ERROR!')
            

        self.label_measpower.after(self.refreshRate, self.ReadPower)
        
        #print('Shit')

    def _Conf(self, confFileName: str):
        
        with open(confFileName, 'r') as configFile:
            configs = configFile.readlines()        

        self.inverter_name = configs[0].strip()
        self.ip_addres     = configs[1].strip()
        self.port          = int(configs[2].strip())
        self.maxpower      = float(configs[3].strip())


# =============================
# Run the interface
# =============================
master = Tk()
#master.title('Inverter control')
#master.iconbitmap('python_18894.ico')

Grid.rowconfigure(master, 0, weight=1)
Grid.columnconfigure(master, 0, weight=1)
Grid.columnconfigure(master, 1, weight=0)
Grid.columnconfigure(master, 2, weight=1)

# PV inverter frame
numpad_PV = NumPad(master, 'conf_pv.txt')
numpad_PV.grid(row=0, column=0, sticky=NSEW)

sep = Separator(master, orient=VERTICAL)
sep.grid(row=0, column=1, sticky=NS)

# Wind inverter frame
numpad_WG = NumPad(master, 'conf_wind.txt')
numpad_WG.grid(row=0, column=2, sticky=NSEW)


master.mainloop()

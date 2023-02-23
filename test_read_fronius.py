from pyModbusTCP.client import *

c = ModbusClient(host='10.1.65.66', port=502, timeout=0.4, auto_open=True, auto_close=True)

# Set the power register
reg_addr_p = 40083 # In the table is 40084
reg_addr_f = 40085 # In the table is 40086
reg_addr_q = 40089 # In the table is 40090
reg_addr_pf= 40091 # In the table is 40092

regs = c.read_holding_registers(reg_addr_p, reg_nb=1)

print(f'Register value is {regs}')


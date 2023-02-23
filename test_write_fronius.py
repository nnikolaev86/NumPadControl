from pyModbusTCP.client import *

c = ModbusClient(host='10.1.65.66', port=502, timeout=1, auto_open=True, auto_close=True)

# Set the power register
power_percents = 2000 #Percents multiplied by 100, i.e. 50% = 5000
reg_addr = 40232
success = c.write_single_register(reg_addr, power_percents)

print(f'Setting power register is {success}')

# Confirm the power setpoint
reg_value = 1
reg_addr = 40236
success = c.write_single_register(reg_addr, reg_value)

print(f'Confirmation of the power register is {success}')

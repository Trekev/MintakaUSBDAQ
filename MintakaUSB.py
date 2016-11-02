import time
import serial
import os
import pandas as pd
from time import gmtime, strftime
import Calculations as c
import numpy as np




def Pressure2DB(pA,pB, p1):
    t = strftime("%m-%d %H:%M:%S", gmtime())
    
    df2 = pd.DataFrame([[t, pA, pB,  p1]], columns=['Time','Mintaka PA','Mintaka PB', 'Paro P'])
    return(df2)
    
df = pd.DataFrame(columns=['Time','Mintaka PA','Mintaka PB', 'Paro P'])

serA = serial.Serial(
    port='COM18',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    xonxoff = False,     #disable software flow control
    rtscts = False,     #disable hardware (RTS/CTS) flow control
    dsrdtr = False,       #disable hardware (DSR/DTR) flow control
    writeTimeout = 2,     #timeout for write

)

serB = serial.Serial(
    port='COM20',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    xonxoff = False,     #disable software flow control
    rtscts = False,     #disable hardware (RTS/CTS) flow control
    dsrdtr = False,       #disable hardware (DSR/DTR) flow control
    #writeTimeout = 2,     #timeout for write

)


ser1 = serial.Serial(
    port='COM4',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    xonxoff = False,     #disable software flow control
    rtscts = False,     #disable hardware (RTS/CTS) flow control
    dsrdtr = False,       #disable hardware (DSR/DTR) flow control
    #writeTimeout = 2,     #timeout for write
    timeout=1
)

serA.timeout = 1
serB.timeout = 1
ser1.timeout = 1

DurM = input("How long in minutes will the program run?")
Inter = input("How often (seconds) would you like to sample the data? (min is 10)")

DurS = float(DurM)*60

InterLoop = int(DurS)/(float(Inter))

SMD = [serA,serB]

for x in SMD:
    #x.write('asq'.encode())
    x.write(('as '+Inter+' \r\n').encode())
    print(x.readlines())

for i in range(int(InterLoop)):
    time.sleep(1)
    ser1.write('*0100P3'.encode())
    re1 = ser1.readlines()
    reA = serA.readlines()
    reB = serB.readlines()
    print(len(reA),len(reB),len(re1))
    print(i)
    if len(reA) and len(reB) and len(re1) > 0:
        pA = reA[0].decode("utf-8")[9:16]
        pB = reB[0].decode("utf-8")[9:16]
        p1 = re1[0].decode("utf-8")[5:14]
        print(pA, pB,  p1)
        df = df.append(Pressure2DB(pA, pB, p1))
    #time.sleep(int(Inter))



df[['Mintaka PA', 'Mintaka PB', 'Paro P']] = df[['Mintaka PA', 'Mintaka PB', 'Paro P']].apply(pd.to_numeric, args=('coerce',))
df['Mintaka PA'] = df['Mintaka PA']*1000
df['Mintaka PB'] = df['Mintaka PB']*1000
df['Mintaka Avg'] = (df['Mintaka PA']+df['Mintaka PB'])/2


c.FPDifference(df)
fprmsd = c.FPRMSD(df)
c.OICDifference(df, df['Mintaka PA'], df['Mintaka PB'], df['Paro P'])
oicrmsd = c.OICRMSD(df, df['Mintaka Avg'], df['Paro P'])
df['A OOS']=np.nan
mask = (abs(df['A - REF'])>0.11)
df['A OOS'][mask] = df['Paro P'][mask]

df['B OOS']=np.nan
mask = (abs(df['A - REF'])>0.11)
df['B OOS'][mask] = df['Paro P'][mask]

print('The FP Root Mean Deviation Squared from this test is: ' + str(fprmsd))
print('The OIC Root Mean Deviation Squared from this test is: ' + str(oicrmsd))
print('The Standard Error for the Mintaka (A): ' + str(c.SE(df['Mintaka PA'])))
print('The Standard Error for Mintaka (B): ' + str(c.SE(df['Mintaka PB'])))
print('The Standard Error for Paroscientific: ' + str(c.SE(df['Paro P'])))


a = df['Paro P']
bins = np.array([870,900,930,960,990,1020])
groups = df.groupby(pd.cut(a, bins))
print(groups.mean())
gmean = groups.mean()

statlistname = ['FP RMSD','OIC RMSD', 'SE Mintaka (A)', 'SE Mintaka (B)', 'SE Ref']
statlistdata = [fprmsd,oicrmsd,c.SE(df['Mintaka PA']),c.SE(df['Mintaka PB']),str(c.SE(df['Paro P']))]


dfstat = pd.DataFrame(data=statlistdata, index=statlistname)
df.to_csv('LastTest')
dfstat.to_csv('LastTest_Stat')
gmean.to_csv('LastTest_Groups')


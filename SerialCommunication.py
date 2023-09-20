import tkinter
from tkinter import Tk, filedialog, font
import pandas as pd
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
import tkinter.messagebox as msgbox

class videoGUI:
    def __init__(self,window,window_title):
        self.window=window
        self.window.title(window_title)
        #self.window.geometry("520x620")
        self.window.geometry("620x620")
        self.window.resizable(False,False)

        # ------------버튼------------

        self.openbtn=tkinter.Button(self.window,text="LaserOn",width=20,command=lambda:self.LaserOn())
        self.openbtn.place(x=50,y=10)

        self.openbtn=tkinter.Button(self.window,text="LaserOff",width=20,command=lambda:self.LaserOff())
        self.openbtn.place(x=50,y=50)

        self.stopbtn=tkinter.Button(self.window,text="CntinusAuto",width=20,command=lambda:self.th())
        self.stopbtn.place(x=50,y=90)
        
        self.stopbtn=tkinter.Button(self.window,text="Stop",width=20,command=lambda:self.stopFile())
        self.stopbtn.place(x=230,y=10)

        self.savebtn=tkinter.Button(self.window,text="Save",width=20,command=lambda:self.saveFile())
        self.savebtn.place(x=230, y=50)

        self.savebtn=tkinter.Button(self.window,text="Clear",width=20,command=lambda:self.delete())
        self.savebtn.place(x=230, y=90)
        # ------------ListBox------------

        self.bar=tkinter.Frame(self.window)
        self.bar.pack(side="bottom")

        self.scrollbar=tkinter.Scrollbar(self.bar,orient="vertical")
        self.scrollbar.pack(side="right",fill="y")

        self.vallist=tkinter.Listbox(self.bar,width=70,height=27,selectmode='extended',yscrollcommand=self.scrollbar.set)
        self.vallist.pack(side="left")

        self.size=font.Font(size=12)
        self.vallist.config(font=self.size)

        self.scrollbar.config(command=self.vallist.yview)

        # ------------포트 번호, baudrate 설정------------
        
        comlist=serial.tools.list_ports.comports()
        self.connected=[]
        for elemenet in comlist:
            self.connected.append(elemenet.device)
        self.list1=tkinter.StringVar(value=self.connected)
        self.list=tkinter.Listbox(self.window,width=24,height=8,selectmode='extended',listvariable=self.list1)
        self.list.place(x=400,y=10)

        self.baudrate=19200

        self.ser=0

        self.time_list=[]
        self.dist_list=[]
        self.sq_list=[]
        self.elapsed_time=[]

        self.start=True

        self.index=0

        self.window.mainloop()

    def LaserOn(self):
        try:
            self.comp_selected=self.list.get(self.list.curselection())
            print(self.comp_selected)

            self.ser=serial.Serial(port=self.comp_selected,baudrate=self.baudrate)

            command = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
            self.ser.write(command)

            self.ser.readline(9)
            self.vallist.insert(tkinter.END,"Laser On")
            self.vallist.see(tkinter.END)

            self.start=True

        except serial.SerialException:
            command = b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1'
            self.ser.write(command)

            self.ser.readline(9)
            self.vallist.insert(tkinter.END,"Laser On")
            self.vallist.see(tkinter.END)
    
    def LaserOff(self):
        command = b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0'
        self.ser.write(command)

        off=self.ser.readline(9)
        #print(off)
        self.vallist.insert(tkinter.END,"Laser Off")
        self.vallist.see(tkinter.END)

    def th(self):
        th=threading.Thread(target=self.CntinusAuto)
        th.daemon=True
        th.start()

    def CntinusAuto(self):
        try:
            command = b'\xAA\x00\x00\x20\x00\x01\x00\x04\x25'
            self.ser.write(command)
            
            #self.ser.readline(9)
            while True:
                
                if self.start==False:
                    break
                

                byte1=self.ser.readline(1)
                value1=str(bytes.hex(byte1,' '))
                print(value1)

                if value1=='ee':
                    if self.start==False:
                        break

                    state=self.ser.readline(8)
                    hexvalue=str(bytes.hex(state,' '))
                    print(hexvalue)
                    self.error(hexvalue)
                
                else:
                    if self.start==False:
                        break
                    res=self.ser.readline(12)
                    value=str(bytes.hex(res, ' '))
                    print(value)
                    
                    if len(value)<35: #중간에 읽다가 오류
                        value=value.replace(" ","")
                        cnt=24-len(value)
                        res=self.ser.readline(int(cnt/2)) 
                        # print(res)
                        # print(value)
                        continue

                    now = datetime.now()
                    date_s = (now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]) #문자열
                    date_p=datetime.strptime(date_s,'%Y-%m-%d %H:%M:%S.%f') #date형식
                    self.time_list.append(date_p)
                    
                    if self.index==0:
                        self.elapsed_time.append(0)
                    else:
                        elptime=self.time_list[self.index]-self.time_list[self.index-1]
                        elptime=elptime.total_seconds()
                        self.elapsed_time.append(elptime)
                    
                    #print(value[15:26])
                    val=int(value[15:26].replace(" ",""),16)
                    #print("distance:",val,end=' ')
                    self.dist_list.append(val)

                    #print(value[27:32])
                    val2=int(value[27:32].replace(" ",""),16) #sq_dec
                    #print("sq:",val2)
                    self.sq_list.append(val2)

                    self.index+=1
                    self.vallist.insert(tkinter.END,"["+str(self.index)+"] "+date_s+str(" distance: %d" %val)+str(" sq: %d " %val2)+"interval: "+str(self.elapsed_time[self.index-1])+"s")
                    self.vallist.see(tkinter.END)

        except ValueError:
            pass
        except AttributeError:
            pass
        except serial.SerialException:
            pass
    
    def error(self,hexvalue):
        dcp=hexvalue[15:20].replace(" ","")
        
        if dcp=='0000':
            self.vallist.insert(tkinter.END,"No error")
            self.vallist.see(tkinter.END)
        elif dcp=='0001':
            self.vallist.insert(tkinter.END,"Power input too low, power voltage should>=2.2V")
            self.vallist.see(tkinter.END)
        elif dcp=='0002':
            self.vallist.insert(tkinter.END,"Internal error, don't care")
            self.vallist.see(tkinter.END)
        elif dcp=='0003':
            self.vallist.insert(tkinter.END,"Module temperature is too low(<-20C)")
            self.vallist.see(tkinter.END)
        elif dcp=='0004':
            self.vallist.insert(tkinter.END,"Module temperature is too high(>+40C)")
            self.vallist.see(tkinter.END)
        elif dcp=='0005':
            self.vallist.insert(tkinter.END,"Target out of range")
            self.vallist.see(tkinter.END)
        elif dcp=='0006':
            self.vallist.insert(tkinter.END,"Invalid measure result")
            self.vallist.see(tkinter.END)
        elif dcp=='0007':
            self.vallist.insert(tkinter.END,"Background light too strong")
            self.vallist.see(tkinter.END)
        elif dcp=='0008':
            self.vallist.insert(tkinter.END,"Laser signal too weak")
            self.vallist.see(tkinter.END)
        elif dcp=='0009':
            self.vallist.insert(tkinter.END,"Laser signal too strong")
            self.vallist.see(tkinter.END)
        elif dcp=='000a':
            self.vallist.insert(tkinter.END,"Hardware fault 1")
            self.vallist.see(tkinter.END)
        elif dcp=='000b':
            self.vallist.insert(tkinter.END,"Hardware fault 2")
            self.vallist.see(tkinter.END)
        elif dcp=='000c':
            self.vallist.insert(tkinter.END,"Hardware fault 3")
            self.vallist.see(tkinter.END)
        elif dcp=='000d':
            self.vallist.insert(tkinter.END,"Hardware fault 4")
            self.vallist.see(tkinter.END)
        elif dcp=='000e':
            self.vallist.insert(tkinter.END,"Hardware fault 5")
            self.vallist.see(tkinter.END)
        elif dcp=='000f':
            self.vallist.insert(tkinter.END,"Laser signal not stable")
            self.vallist.see(tkinter.END)
        elif dcp=='0010':
            self.vallist.insert(tkinter.END,"Hardware fault 6")
            self.vallist.see(tkinter.END)
        elif dcp=='0011':
            self.vallist.insert(tkinter.END,"Hardware fault 7")
            self.vallist.see(tkinter.END)
        elif dcp=='0081':
            self.vallist.insert(tkinter.END,"Invalid Frame")
            self.vallist.see(tkinter.END)
        
    
    def stopFile(self):
        
        self.start=False
        command = b'\x58'
        self.ser.write(command)
        self.ser.close()

    def saveFile(self):
        outfilename=filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[('Excel files','*.xlsx')])
        if outfilename:
            df=pd.DataFrame({'time':pd.Series(self.time_list), 'distance':pd.Series(self.dist_list),'sq':pd.Series(self.sq_list),'elapsed_time':pd.Series(self.elapsed_time)}) #,'elapsed_time':pd.Series(self.elapsed_time_list)
            df.to_excel(outfilename,index=False)

    def delete(self):
        response=msgbox.askokcancel("확인","삭제하시겠습니까?")

        if response==1:
            self.vallist.delete(0,tkinter.END)

            self.time_list=[]
            self.dist_list=[]
            self.sq_list=[]
            self.elapsed_time=[]
            self.index=0
        else:
            pass
        

if __name__=="__main__":
    
    videoGUI(Tk(),"Laser")
    pass
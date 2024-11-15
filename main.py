from customtkinter import *
import socket
import kthread #pip install kthread
from time import sleep
import subprocess
import re
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

root = CTk()
root.geometry("600x200")
root.geometry("+400+200")
root.title("JOPA - Журнал Определения ПК Адресов")

class ScrollableLabelButtonFrame(CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, note):
        address = CTkLabel(self, text=item, compound="left", padx=5, anchor="w")
        notelabel = CTkLabel(self, text=note, compound="left", padx=5, anchor="w")
        button = CTkButton(self, text="Заметка", width=100, height=24)
        if self.command is not None:
            button.configure(command= lambda:makenote(item))
        address.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        notelabel.grid(row=len(self.label_list),column=1,pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=2, pady=(0, 10), padx=5)
        self.label_list.append(address)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

def parse_net():
    global iplist 
    iplist = ScrollableLabelButtonFrame(master=root, width=430, command=lambda:makenote, corner_radius=0)
    ipadressen = {}
    def ping(ipadresse):
        
        try:
            outputcap = subprocess.run([f'ping', ipadresse, '-n', '1'], capture_output=True) #sends only one package, faster
            ipadressen[ipadresse] = outputcap
        except Exception as Fehler:
            print(Fehler)
    t = [kthread.KThread(target = ping, name = f"ipgetter{ipend}", args=(f'192.168.0.{ipend}',)) for ipend in range(255)] #prepares threads
    [kk.start() for kk in t] #starts 255 threads
    while len(ipadressen) < 255:
        sleep(.3)
    alldevices = []
    for key, item in ipadressen.items():
        if not 'unreachable' in item.stdout.decode('utf-8') and 'failure' not in item.stdout.decode('utf-8'): #checks if there wasn't neither general failure nor 'unrechable host'
            alldevices.append(key)
    for i in range(0,len(alldevices)):
        try:
            f = open("notes.dat", mode="r+")
            for line in f:
                if line != "\n":
                    if re.search(str(alldevices[i]),line):
                        notestr = line.split(' ',1)[1]
                    else : notestr = " - "
                    iplist.add_item(alldevices[i],notestr)
        except IOError:
            notestr = " - "
            iplist.add_item(alldevices[i],notestr)
           
    iplist.place(x=150,y=5,anchor=NW)


def makenote(targetip):
    vari = ""
    
    def define(vari):
        file = open("notes.dat",mode="w+")
        vari=entrynote.get()
        file.write("\n" + str(targetip) + " " + vari)
        file.close()
        toplevel.destroy()
        iplist.place_forget
        parse_net()
        
    
    toplevel=CTkToplevel(root)
    toplevel.geometry("200x100")
    entrynote = CTkEntry(toplevel,placeholder_text="Запишите свою заметку")
    entrynote.pack()
    btnnote = CTkButton(toplevel,width=30, text="OK", command=lambda:define(vari))
    btnnote.pack()
    

butt = CTkButton(root, text="Scan IPs", width=120, command=parse_net)
butt.place(x=5,y=15,anchor=NW)

root.mainloop()
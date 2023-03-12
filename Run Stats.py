from tkinter import *
import time, os

os.system('cls')

username = os.getlogin()

folder = "C:\\Users\ " + username + "\Documents\ " + "Github\ " + "SN_Stats\ "

main = folder + "Stats_Main.py"
mainPath = main.replace(" ", "")

info = folder + "Stats_Info.py"
infoPath = info.replace(" ", "")

choice = input('What would you like to run?: ')

if(choice.lower() == 'main'):
    os.system('py -m streamlit run ' + mainPath +  ' --theme.base dark')
    print('main chosen')

elif(choice.lower() == 'info'):
    os.system('py -m streamlit run ' + infoPath +  ' --theme.base dark')
    print('info chosen')

else:
    print('invalid response')
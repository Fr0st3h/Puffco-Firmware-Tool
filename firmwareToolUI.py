from py_cui import py_cui, colors, popups
import os
import asyncio
import traceback
import threading
from puffco import *

os.system('mode con: cols=120 lines=30')

class FirmwareToolUI:
    
    def showMenuPopup(self, title: str, menu_items, command):
        self.root._popup = popups.MenuPopup(self.root, menu_items, title, colors.WHITE_ON_BLACK, command, self.root._renderer, self.root._logger, False)
        self.root._popup.set_selected_color(colors.RED_ON_BLACK)
    
    def getTitle(self):
        title = ""
        title += ' ______          ___    ___              _______ _                                        _______          _ \n'
        title += '(_____ \        / __)  / __)            (_______|_)                                      (_______)        | | \n'
        title += ' _____) )   _ _| |__ _| |__ ____ ___     _____   _  ____ ____  _ _ _ _____  ____ _____       _  ___   ___ | | \n'
        title += '|  ____/ | | (_   __|_   __) ___) _ \   |  ___) | |/ ___)    \| | | (____ |/ ___) ___ |     | |/ _ \ / _ \| | \n'
        title += '| |    | |_| | | |    | | ( (__| |_| |  | |     | | |   | | | | | | / ___ | |   | ____|     | | |_| | |_| | | \n'
        title += '|_|    |____/  |_|    |_|  \____)___/   |_|     |_|_|   |_|_|_|\___/\_____|_|   |_____)     |_|\___/ \___/ \_)\n'
        title += '\nBy Fr0st3h#9889                                                                                             '
        return title

    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        self.root.toggle_unicode_borders()
        

        self.mainMenu = self.root.create_new_widget_set(8,8)
        self.root.set_refresh_timeout(0.5)
        
        self.root.set_title("Puffco Firmware Tool - Created By Fr0st3h#9889 - v1.2")
        
        title = self.mainMenu.add_block_label(self.getTitle(), 0, 0, 2, 8, center=True)
        title.set_color(colors.RED_ON_BLACK)
        
        searchBtn = self.mainMenu.add_button("Search For Puffco", 2, 2, 1, 2, command=self.searchForPuffco)
        searchBtn.set_color(colors.RED_ON_BLACK)
        
        searchBtn = self.mainMenu.add_button("Search For DFU Puffco", 2, 4, 1, 2, command=self.searchForDFUPuffco)
        searchBtn.set_color(colors.RED_ON_BLACK)
        
        self.outputConsole = self.mainMenu.add_scroll_menu("Output Console:", 3, 0, 5, 8)
        self.outputConsole.set_selected_item_index(-1)
        self.outputConsole.add_text_color_rule('\[(.*?)\]', py_cui.RED_ON_BLACK, 'contains', match_type='regex')
        self.outputConsole.set_border_color(colors.RED_ON_BLACK)
        
        self.puffco = Puffco(self.outputConsole)
        
        self.root.apply_widget_set(self.mainMenu)
        
    def addOutput(self, msg):
        self.outputConsole.add_item(f'[PFT] {msg}')
        self.outputConsole._top_view = (len(self.outputConsole.get_item_list()) - 1) - self.outputConsole.get_viewport_height()
        
    def findDeviceThread(self):
        self.name, self.address = asyncio.run(self.puffco.findPuffco())
        self.root.stop_loading_popup()
        if(self.address):
            self.name = list(self.name)[0]
            self.root.show_yes_no_popup(f"Is {self.name} your Puffco Name?", self.handleYesNo)
            self.addOutput(f"Found puffco named {self.name} ({self.address})")
        else:
            self.addOutput("No Puffco found. Please make sure it's not connected to your phone.")        
            
    def findDFUDeviceThread(self):
        self.name, self.address, self.firmware = asyncio.run(self.puffco.findpuffcoDFU())
        self.root.stop_loading_popup()
        if(self.firmware == "Firmware W"):
            self.root.show_message_popup(f"Found Puffco in DFU", "Firmware W is installed, Puffco booting in 5 seconds.")
            self.addOutput(f"Found DFU Puffco named {self.name} ({self.firmware})")
        elif(self.firmware == "Firmware X"):
            self.root.show_message_popup(f"Found Puffco in DFU", "Firmware X is installed, Puffco booting in 5 seconds.")
            self.addOutput(f"Found DFU Puffco named {self.name} ({self.firmware})")
        elif(self.firmware == "No Firmware"):
            self.root.show_message_popup(f"Found Puffco in DFU", "No firmware installed. Installing Firmware W")
            self.addOutput(f"Found DFU Puffco named {self.name} ({self.firmware})")
            asyncio.run(self.puffco.fixBrickedPuffco(self.address, "FirmwareW.gbl"))
        else:
            self.addOutput(f"No DFU Puffco found. ({self.firmware})")
            
    async def doFirmwareInstall(self, firmware):
        try:
            if(firmware == "X"):
                if(await self.device.getFirmware() == "X"):
                    self.addOutput("Firmware X Detected! Running Firmware Authentication..")
                    await self.device.authenticateWithFirmware()
        except:
            traceback.print_exc()
                
    def handleFirmwareSelectionThread(self, selection):
        try:
            if(selection == "Firmware X"):
                file = "FirmwareX.gbl"
            elif(selection == "Firmware W"):
                file = "FirmwareW.gbl"
            asyncio.run(self.puffco.startInstallationProcess(self.address, file))
        except:
            traceback.print_exc()
            
    def handleFirmwareSelection(self, selection):
        thread = threading.Thread(target=self.handleFirmwareSelectionThread, args=(selection,))
        thread.start()
        
    def handleYesNo(self, res):
        if(res):
            firmwares = list()
            firmwares.append("Firmware W")
            firmwares.append("Firmware X")
            self.showMenuPopup("Select firmware to install", firmwares, self.handleFirmwareSelection)
        else:
            self.addOutput(f"Canceling Action..")
        

    def searchForPuffco(self):
        self.outputConsole.clear()
        self.root.show_loading_icon_popup("Searching for Puffco..", "Please wait while I look for your Puffco.")
        thread = threading.Thread(target=self.findDeviceThread)
        thread.start()
        
    def searchForDFUPuffco(self):
        self.outputConsole.clear()
        self.root.show_loading_icon_popup("Searching for DFU Puffco..", "Please wait while I look for your Puffco.")
        thread = threading.Thread(target=self.findDFUDeviceThread)
        thread.start()
        
        

root = py_cui.PyCUI(8, 8)
wrapper = FirmwareToolUI(root)
root.start()
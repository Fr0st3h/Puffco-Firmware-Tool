import asyncio
from bleak import BleakScanner, BleakClient
import subprocess
import pathlib
import re

scanner = BleakScanner()

def addToConsole(console, msg):
    console.add_item(f'[PFT] {msg}')
    console._top_view = (len(console.get_item_list()) - 1) - console.get_viewport_height()
    
def updateUploadStatus(console, percent):
    console.get_item_list()[len(console.get_item_list())-1] = f"[PFT] Uploading Firmware... {percent}%"

class PuffcoDevice:
    def __init__(self, mac, console):
        self.client = BleakClient(mac)
        self.mac = mac
        self.console = console
        
        
    async def connectToPuffco(self):
        try:
            await self.client.connect()
            return True
        except Exception as e:
            return False
            
    async def getDeviceName(self):
        try:
            return await self.client.read_gatt_char('f9a98c15-c651-4f34-b656-d100bf58004d', response=True)
        except Exception as e:
            return
    
    async def getFirmware(self):
        try:
            firmware = await self.client.read_gatt_char('00002A28-0000-1000-8000-00805F9B34FB', response=True)
            return firmware.decode("utf-8")
        except:
            return
    
    async def getFirmwareApploader(self):
        try:
            firmware = await self.client.read_gatt_char('0D77CC11-4AC1-49F1-BFA9-CD96AC7A92F8', response=True)
            return firmware
        except:
            return
    
    async def getAccessSeedKey(self):
        try:
            accessSeedKey = list(await self.client.read_gatt_char('F9A98C15-C651-4F34-B656-D100BF5800E0', response=True))
            accessSeedKey = ",".join(str(num) for num in accessSeedKey)
            return accessSeedKey
        except:
            return
    
    async def enterOTADFU(self):
        try:
            await self.client.write_gatt_char('F7BF3564-FB6D-4E53-88A4-5E37E0326063', bytearray([0x01]), response=True)
        except:
            return
    
    async def authenticateWithFirmware(self):
        addToConsole(self.console, "Getting accessSeedKey key..")
        key = await self.getAccessSeedKey()
        if(key == False):
            addToConsole(self.console, "Please make sure you've paired your Puffco in your PC's bluetooth settings.")
            return
        addToConsole(self.console, "Getting authentication key..")
        key = key.replace(',', " ")
        decryptFilePath = str(pathlib.Path(__file__).parent)+"\\resources\\decrypt.js"
        proc = subprocess.Popen(f'node {decryptFilePath} ' + key, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        key = out.decode('utf-8').split(',')
        finalKey = ""
        for item in key:
            item = item.replace('\n', '')
            item = item.replace('   ', ' ')
            item = item.replace('  ', ' ')
            finalKey += item
        finalKey = finalKey.split('[ ')[1].replace("]", '') 
        addToConsole(self.console, "Writing authentication key..")
        await self.sendDecryptionKey(finalKey)
        if(await self.getDeviceName()):
            return True
        else:
            return False
    
    async def sendDecryptionKey(self, key):
        key = key.split(' ')
        key = list(map(int, key))
        key = bytes(key)
        try:
            await self.client.write_gatt_char("F9A98C15-C651-4F34-B656-D100BF5800E0", key, response=True)
        except Exception as e:
            print(e)
            
    async def uploadFirmware(self, file):
        await self.client.write_gatt_char('F7BF3564-FB6D-4E53-88A4-5E37E0326063', bytearray([0x00]), response=True)
        uploaded = 0
        with open(str(pathlib.Path(__file__).parent)+"\\resources\\firmwares\\"+file, "rb") as f:
            total = pathlib.Path(str(pathlib.Path(__file__).parent)+"\\resources\\firmwares\\"+file).stat().st_size
            addToConsole(self.console, "[PFT] Uploading Firmware... 0%")
            while True:
                data = f.read(100)
                if(data):
                    try:
                        await self.client.write_gatt_char('984227F3-34FC-4045-A5D0-2C581F81A153', bytearray(data), response=False)
                    except Exception as e:
                        addToConsole(self.console, f"Error while uploading firmware: {e}")
                        return False
                    uploaded += len(data)
                else:
                    addToConsole(self.console, f"Uploaded Firmware! ({uploaded} bytes)")
                    addToConsole(self.console, f"Finalizing firmware install.. please wait.")
                    await self.client.write_gatt_char('F7BF3564-FB6D-4E53-88A4-5E37E0326063', bytearray([0x03]), response=True)
                    break
                try:
                    updateUploadStatus(self.console, f"{int(round((uploaded/total)*100, 1))}")
                except Exception as e:
                    addToConsole(self.console, f"Error: {e}")
                    return False
                await asyncio.sleep(0.03)
        return True
    
    async def exitDFU(self):
        for x in range(0,5):
            try:
                await self.client.write_gatt_char('F7BF3564-FB6D-4E53-88A4-5E37E0326063', bytearray([x]), response=True)
            except Exception as e:
                pass
        addToConsole(self.console, "Done..")
        
class Puffco:
    def __init__(self, console):
        self.console = console
        
    async def connectToPuffco(self, mac):
        try:
            device = PuffcoDevice(mac, self.console)
            await device.connectToPuffco()
            if(await device.getFirmware() == "X"):
                addToConsole(self.console, "Device is on firmware x.. Authenticating firmware.")
                result = await device.authenticateWithFirmware()
                if(result):
                    addToConsole(self.console, "Authentication successful")
                elif(result == False):
                    addToConsole(self.console, "Authentication failed. Please try again.")
                    return
                else:
                    return
            else:
                addToConsole(self.console, "Firmware W Detected! Skipping Firmware Authentication..")
            addToConsole(self.console, "Entering DFU.. Your Puffco will reboot.")
            await device.enterOTADFU()
            await device.client.disconnect()
            return True
        except Exception as e:
            addToConsole(self.console, e)


    async def findPuffco(self):
        devices = await scanner.discover()
        for d in devices:
            if d.rssi <= -75:
                continue

            if('06caf9c0-74d3-454f-9be9-e30cd999c17a' in d.metadata.get("uuids")):
                return ({str(d).split(': ')[1]}, d.address)
        return ("", False)

    async def findpuffcoDFU(self):
        devices = await scanner.discover()
        for d in devices:
            if d.rssi <= -75:
                continue
            
            x = re.search("(([0-9A-F]{2}[:-]?){6})", d.name)
            if(x):
                #print(f"Could be a puffco: {d.rssi} {d.address} {d.name} {len(d.name)}")
                client = BleakClient(d.address)
                if(await client.connect()):
                    try:
                        firmware = await client.read_gatt_char('0D77CC11-4AC1-49F2-BFA9-CD96AC7A92F8', response=True)
                        await client.disconnect()
                        if(firmware[0] == 18):
                            return (d.name, d.address, "Firmware W")
                        elif(firmware[0] == 19):
                            return (d.name, d.address, "Firmware X")
                        elif(firmware[0] == 0):
                            return (d.name, d.address, "No Firmware")
                        else:
                            return (d.name, d.address, firmware[0])
                    except:
                        pass

        return ("", False)

    async def findDFUPuffco(self, originalMac):
        devices = await scanner.discover()
        for d in devices:
            if d.rssi <= -75:
                continue
            if(d.name == originalMac.replace(":", "")):
                return d.address
        return False
            
    async def startInstallationProcess(self, mac, file):
        if(mac):
            addToConsole(self.console, "Connecting to Puffco..")
            connected = await self.connectToPuffco(mac)
            if(connected == True):
                addToConsole(self.console, "Looking for Puffco in DFU..")
                newMac = await self.findDFUPuffco(mac)
                if(newMac):
                    addToConsole(self.console, f"Found Puffco in DFU ({newMac})")
                    device = PuffcoDevice(newMac, self.console)
                    if(await device.connectToPuffco()):
                        if(await device.uploadFirmware(file)):
                            addToConsole(self.console, f"Exiting DFU..")
                            await device.exitDFU()
                            addToConsole(self.console, "Firmware should be installed. Please allow up to 10 seconds for Puffco to boot.")
                            await device.client.disconnect()
                        else:
                            addToConsole(self.console, "Firmware didnt install.")
                    else:
                        addToConsole(self.console, "Couldn't connect.")
                else:
                    addToConsole(self.console, "Couldn't find Puffco.")
            elif(connected == False):
                addToConsole(self.console, "Couldn't connect to Puffco.")
        else:
            addToConsole(self.console, "Couldn't find Puffco.")
            
    async def fixBrickedPuffco(self, mac, file):
        if(mac):
            addToConsole(self.console, f"Found Puffco in DFU ({mac})")
            device = PuffcoDevice(mac, self.console)
            if(await device.connectToPuffco()):
                if(await device.uploadFirmware(file)):
                    addToConsole(self.console, f"Exiting DFU..")
                    await device.exitDFU()
                    addToConsole(self.console, "Firmware should be installed. Please allow up to 10 seconds for Puffco to boot.")
                    await device.client.disconnect()
                else:
                    addToConsole(self.console, "Firmware didnt install.")
            else:
                addToConsole(self.console, "Couldn't connect.")
        else:
            addToConsole(self.console, "Couldn't find Puffco.")
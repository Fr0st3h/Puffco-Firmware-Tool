# Puffco-Firmware-Tool
A tool that lets you install Firmwares W and X to your Puffco.

--------
# How to use:

Before you start, make sure you have node.js installed. Once you have it installed download the tool below and put the exe on your desktop. Go to bluetooth settings on your PC and pair your puffco device.
Once its paired, open the tool. Make sure the puffco isnt in bluetooth mode, click the button on the back of your puffco to select a profile to make sure the puffco is awake. Next on the tool click "Search For Puffco". If all goes well it will prompt you with a question asking if the device it found is the puffco you're wanting to install the firmware to, if it is click Y. The tool will then put your puffco in DFU mode and will upload the firmware. Once uploaded the tool will finalize the install and boot your puffco, once it boots it will be on the firmware you selected.

If anything goes wrong let me know, you wont brick the puffco using this tool as theres 2 layers to the puffco, an apploader and an application. worst case senario is the puffco has no application to boot and you just need to install the firmware using an app on your phone. I will have an update out later that will automatically detect a puffco in this state and have it install a firmware. 
If after going into DFU it fails to connect, your puffco will automatically boot back up, just give it 30 seconds or so.

if the tool isnt finding the puffco, forget the device in bluetooth settings and pair again.
You can also disable your phone bluetooth and try with that off.

# Screenshot
https://i.imgur.com/MOsW1wU.png

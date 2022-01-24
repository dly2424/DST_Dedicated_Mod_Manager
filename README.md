# DST_Dedicated_Mod_Manager
A mod manager for Don't Starve Together Dedicated server. Linux and Windows compatible. Written in Python.

This is a mod manager for Don't Starve Together Dedicated servers. This is geared towards Linux users, though completely supported for Windows users.

Written and tested in Python3.

The program includes a usable interface the newbiest of people can use. This is not final release, in fact this is still very much so in Beta.
The program is currently in a very usable state, though i would recommend backing up your modoverrides.lua and dedicated_server_mods_setup.lua files before using just in case. 

**The program will:**
```
•Add mods to your dedicated server, and they will install when you run your server.

•Remove mods from your dedicated server.

•Automatically generate configurations for your mods using their default values.

•Configure your mod options according to your liking.

•Assist you in your setup of the program.
```



**What can i expect from final release?**
```
•Bug fixes and stability. More error handling.

•Cut down redundant code, for a smaller filesize.

•Optimization on the interface and in code.

•Full OS dependent path recommendation.

•More readable code (okay maybe not this, i kinda suck with variable names/usage)

•A more consistent parsing of already existing lua files.
```

Special thanks to Fluxistence from the Official Klei Entertainment Discord for helping me understand how DST operates, and how Lua config files are structured and parsed.
![bandicam 2022-01-23 18-37-20-174](https://user-images.githubusercontent.com/46138781/150702837-561f6236-296e-4e7a-a32a-b5e8a853f556.jpg)
![bandicam 2022-01-23 18-37-30-421](https://user-images.githubusercontent.com/46138781/150702839-08fb1ae2-9f20-461c-954c-39f629d5f01b.jpg)
![bandicam 2022-01-23 18-37-52-411](https://user-images.githubusercontent.com/46138781/150702840-495fd787-c71e-4f58-a0dc-01c875e47fa9.jpg)

# Setup
Simply download the DST_mod_manager.py file and run it on your target machine with `python DST_mod_manager.py` or `python3 DST_mod_manager.py`
Or by using something like Git, or Wget:
`wget https://github.com/dly2424/DST_Dedicated_Mod_Manager/blob/main/DST_mod_manager.py`

The program uses Python3, so install it with your respective linux distro's package manager.
Debian example:
`sudo apt get python3`
Also ensure you have pip installed for python3 as well!
`sudo apt get python3-pip`


Tags for search:
dont starve mod manager
dont starve together mod manager
dont starve together dedicated mod manager
dst mod manager
dst dedicated mod manager
dst dedicated server mod manager

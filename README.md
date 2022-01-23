# DST_Dedicated_Mod_Manager
A mod manager for Don't Starve Together Dedicated server. Linux and Windows compatible. Written in Python.

This is a mod manager for Don't Starve Together Dedicated servers. This is geared towards Linux users, though completely supported for Windows users.

Written and tested in Python3.

The program includes a usable interface the newbiest of people can use. This is not final release, in fact this is still very much so in Beta.
The program is currently in a very usable state, though i would recommend backing up your modoverrides.lua and dedicated_server_mods_setup.lua files before using just in case. 

The program will:
•Add mods to your dedicated server, and they will install when you run your server.
•Remove mods from your dedicated server.
•Automatically generate configurations for your mods using their default values.
•Configure your mod options according to your liking.
•Assist you in your setup of the program.


What can i expect from final release?
•Bug fixes and stability. More error handling.
•Cut down redundant code, for a smaller filesize.
•Optimization on the interface and in code.
•Full OS dependent path recommendation.
•More readable code (okay maybe not this, i kinda suck with variable names/usage)
•A more consistent parsing of already existing lua files.


Special thanks to Fluxistence from the Official Klei Entertainment Discord for helping me understand how DST operates, and how Lua config files are structured and parsed.

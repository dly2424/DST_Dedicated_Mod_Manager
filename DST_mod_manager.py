import sys

if sys.version[0] != "3":
    print("You must use Python 3.x (Any version of python3) to run this program. You are using {}.".format(sys.version))
    print("yes/y - no/n")
    try_to_run = raw_input("Try to run it anyways? (It wont work. Too many dependencies rely on Python3. You may edit this program if you wish to run it, otherwise it will crash instantly.)\n>")
    if try_to_run in ["yes", "y"]:
        print("Okay, you've been warned!")
    else:
        print("Exiting...")
        sys.exit()

import pickle, os, time, traceback, re, six
from numbers import Number
from urllib.request import urlopen
from os import name, system



try:
    from bs4 import BeautifulSoup
except:
    get_bs4 = input("You seem to be missing the required package 'bs4' (aka BeautifulSoup4) May i install it for you?\nyes/y - no/n\n>").lower().strip()
    if get_bs4 in ["yes", "y"]:
        try:
            os.system("python3 -m pip install bs4")
            from bs4 import BeautifulSoup
        except:
            os.system("python -m pip install bs4")
            from bs4 import BeautifulSoup
    else:
        print("Unable to continue. Please install bs4 with: python -m pip install bs4")
        sys.exit()

try:
    import lupa
    from lupa import LuaRuntime
except:
    get_lupa = input("You seem to be missing the required package 'lupa' May i install it for you?\nyes/y - no/n\n>").lower().strip()
    if get_lupa in ["yes", "y"]:
        try:
            os.system("python3 -m pip install lupa")
            import lupa
            from lupa import LuaRuntime
        except:
            os.system("python -m pip install lupa")
            import lupa
            from lupa import LuaRuntime
    else:
        print("Unable to continue. Please install lupa with: python -m pip install lupa")
        sys.exit()
        
lua = LuaRuntime(unpack_returned_tuples=True)


print("This is mod manager for Dont Starve Together. Made in Python 3 by Zenzerker.\n")
print("For help, type help or h. To quit, type quit or q, for config, type config or c")
global config, mods, configured, mod_dict, table_parse_function
config = {"configured": False, "dedicated_server_mods_setup": "", "modoverrides_path": "", "modoverrides_path2": ""}
mods = []
mod_configs = {}


table_parse_function = """
function printTable(t, f)

   new_string = ''
   local function printTableHelper(obj, cnt)

      local cnt = cnt or 0

      if type(obj) == "table" then

         new_string = new_string .. "\\n" .. string.rep("\\t", cnt) .. "{\\n"
         cnt = cnt + 1

         for k,v in pairs(obj) do

            if type(k) == "string" then
               new_string = new_string .. string.rep("\\t",cnt) .. '["'..k..'"]' .. ' = '
            end

            if type(k) == "number" then
               new_string = new_string .. ''
            end

            printTableHelper(v, cnt)
            new_string = new_string .. ",\\n"
         end

         cnt = cnt-1
         new_string = new_string .. string.rep("\\t", cnt) .. "}"

      elseif type(obj) == "string" then
         new_string = new_string .. string.format("%q", obj)

      else
         new_string = new_string .. tostring(obj)
      end 
	  return new_string
   end

   if f == nil then
      var = printTableHelper(t)
	  return var
   else
      io.output(f)
      io.write("return")
      printTableHelper(t)
      io.output(io.stdout)
   end
end

new_string2 = printTable(configuration_options)
"""



ERRORS = {                                                                        #From this line a fair bit down is code from: https://github.com/SirAnthony/slpp. Part of the lua parsing this script uses.
    'unexp_end_string': u'Unexpected end of string while parsing Lua string.',    #Code is slightly modified.
    'unexp_end_table': u'Unexpected end of table while parsing Lua string.',
    'mfnumber_minus': u'Malformed number (no digits after initial minus).',
    'mfnumber_dec_point': u'Malformed number (no digits after decimal point).',
    'mfnumber_sci': u'Malformed number (bad scientific format).',
}

def sequential(lst):
    length = len(lst)
    if length == 0 or lst[0] != 0:
        return False
    for i in range(length):
        if i + 1 < length:
            if lst[i] + 1 != lst[i+1]:
                return False
    return True


class ParseError(Exception):
    pass


class SLPP(object):

    def __init__(self):
        self.text = ''
        self.ch = ''
        self.at = 0
        self.len = 0
        self.depth = 0
        self.space = re.compile('\s', re.M)
        self.alnum = re.compile('\w', re.M)
        self.newline = '\n'
        self.tab = '\t'

    def decode(self, text):
        if not text or not isinstance(text, six.string_types):
            return
        self.text = text
        self.at, self.ch, self.depth = 0, '', 0
        self.len = len(text)
        self.next_chr()
        result = self.value()
        return result

    def encode(self, obj):
        self.depth = 0
        return self.__encode(obj)

    def __encode(self, obj):
        s = ''
        tab = self.tab
        newline = self.newline

        if isinstance(obj, str):
            s += '"%s"' % obj.replace(r'"', r'\"')
        elif six.PY2 and isinstance(obj, unicode):
            s += '"%s"' % obj.encode('utf-8').replace(r'"', r'\"')
        elif six.PY3 and isinstance(obj, bytes):
            s += '"{}"'.format(''.join(r'\x{:02x}'.format(c) for c in obj))
        elif isinstance(obj, bool):
            s += str(obj).lower()
        elif obj is None:
            s += 'nil'
        elif isinstance(obj, Number):
            s += str(obj)
        elif isinstance(obj, (list, tuple, dict)):
            self.depth += 1
            if len(obj) == 0 or (not isinstance(obj, dict) and len([
                    x for x in obj
                    if isinstance(x, Number) or (isinstance(x, six.string_types) and len(x) < 10)
               ]) == len(obj)):
                newline = tab = ''
            dp = tab * self.depth
            s += "%s{%s" % (tab * (self.depth - 2), newline)
            if isinstance(obj, dict):
                key_list = ['[%s]' if isinstance(k, Number) else '["%s"]' for k in obj.keys()]
                contents = [dp + (key + ' = %s') % (k, self.__encode(v)) for (k, v), key in zip(obj.items(), key_list)]
                s += (',%s' % newline).join(contents)
            else:
                s += (',%s' % newline).join(
                    [dp + self.__encode(el) for el in obj])
            self.depth -= 1
            s += "%s%s}" % (newline, tab * self.depth)
        return s

    def white(self):
        while self.ch:
            if self.space.match(self.ch):
                self.next_chr()
            else:
                break
        self.comment()

    def comment(self):
        if self.ch == '-' and self.next_is('-'):
            self.next_chr()
            # TODO: for fancy comments need to improve
            multiline = self.next_chr() and self.ch == '[' and self.next_is('[')
            while self.ch:
                if multiline:
                    if self.ch == ']' and self.next_is(']'):
                        self.next_chr()
                        self.next_chr()
                        self.white()
                        break
                # `--` is a comment, skip to next new line
                elif re.match('\n', self.ch):
                    self.white()
                    break
                self.next_chr()

    def next_is(self, value):
        if self.at >= self.len:
            return False
        return self.text[self.at] == value

    def prev_is(self, value):
        if self.at < 2:
            return False
        return self.text[self.at-2] == value

    def next_chr(self):
        if self.at >= self.len:
            self.ch = None
            return None
        self.ch = self.text[self.at]
        self.at += 1
        return True

    def value(self):
        self.white()
        if not self.ch:
            return
        if self.ch == '{':
            return self.object()
        if self.ch == "[":
            self.next_chr()
        if self.ch in ['"',  "'",  '[']:
            return self.string(self.ch)
        if self.ch.isdigit() or self.ch == '-':
            return self.number()
        return self.word()

    def string(self, end=None):
        s = ''
        start = self.ch
        if end == '[':
            end = ']'
        if start in ['"',  "'",  '[']:
            double = start=='[' and self.prev_is(start)
            while self.next_chr():
                if self.ch == end and (not double or self.next_is(end)):
                    self.next_chr()
                    if start != "[" or self.ch == ']':
                        if double:
                            self.next_chr()
                        return s
                if self.ch == '\\' and start == end:
                    self.next_chr()
                    if self.ch != end:
                        s += '\\'
                s += self.ch
        raise ParseError(ERRORS['unexp_end_string'])

    def object(self):
        o = {}
        k = None
        idx = 0
        numeric_keys = False
        self.depth += 1
        self.next_chr()
        self.white()
        if self.ch and self.ch == '}':
            self.depth -= 1
            self.next_chr()
            return o  # Exit here
        else:
            while self.ch:
                self.white()
                if self.ch == '{':
                    o[idx] = self.object()
                    idx += 1
                    continue
                elif self.ch == '}':
                    self.depth -= 1
                    self.next_chr()
                    if k is not None:
                        o[idx] = k
                    if len([key for key in o if isinstance(key, six.string_types + (float,  bool, tuple))]) == 0:
                        so = sorted([key for key in o])
                        if sequential(so):
                            ar = []
                            for key in o:
                                ar.insert(key, o[key])
                            o = ar
                    return o  # or here
                else:
                    if self.ch == ',':
                        self.next_chr()
                        continue
                    else:
                        k = self.value()
                        if self.ch == ']':
                            self.next_chr()
                    self.white()
                    ch = self.ch
                    if ch in ('=', ','):
                        self.next_chr()
                        self.white()
                        if ch == '=':
                            o[k] = self.value()
                        else:
                            o[idx] = k
                        idx += 1
                        k = None
        raise ParseError(ERRORS['unexp_end_table'])  # Bad exit here

    words = {'true': "true&Zenzerker_Value", 'false': "false&Zenzerker_Value", 'nil': "nil&Zenzerker_Value"}
    def word(self):
        s = ''
        if self.ch != '\n':
            s = self.ch
        self.next_chr()
        while self.ch is not None and self.alnum.match(self.ch) and s not in self.words:
            s += self.ch
            self.next_chr()
        return self.words.get(s, s)

    def number(self):
        def next_digit(err):
            n = self.ch
            self.next_chr()
            is_num = True
            try:
                int(self.ch)
            except:
                is_num = False
            if not self.ch or not self.ch.isdigit() or is_num == False:
                raise ParseError(err)
            return n
        n = ''
        try:
            if self.ch == '-':
                n += next_digit(ERRORS['mfnumber_minus'])
            n += self.digit()
            if n == '0' and self.ch in ['x', 'X']:
                n += self.ch
                self.next_chr()
                n += self.hex()
            else:
                if self.ch and self.ch == '.':
                    n += next_digit(ERRORS['mfnumber_dec_point'])
                    n += self.digit()
                if self.ch and self.ch in ['e', 'E']:
                    n += self.ch
                    self.next_chr()
                    if not self.ch or self.ch not in ('+', '-'):
                        raise ParseError(ERRORS['mfnumber_sci'])
                    n += next_digit(ERRORS['mfnumber_sci'])
                    n += self.digit()
        except ParseError:
            t, e = sys.exc_info()[:2]
            print(e)
            return 0
        try:
            return int(n, 0)
        except:
            pass
        return float(n)

    def digit(self):
        n = ''
        while self.ch and self.ch.isdigit():
            n += self.ch
            self.next_chr()
        return n

    def hex(self):
        n = ''
        while self.ch and (self.ch in 'ABCDEFabcdef' or self.ch.isdigit()):
            n += self.ch
            self.next_chr()
        return n


slpp = SLPP()

__all__ = ['slpp']                            #Here ends the code from: https://github.com/SirAnthony/slpp.





try:
    with open('Mod_Manager_Config.pickle', 'rb') as var1:
        config = pickle.load(var1)
except:
    with open('Mod_Manager_Config.pickle', 'wb') as var2:
        pickle.dump(config, var2)

def write_to_pickle():
    global config
    with open('Mod_Manager_Config.pickle', 'wb') as var3:
        pickle.dump(config, var3)

def read_file(file_path):
    with open(file_path, 'r', encoding="utf8", errors="ignore") as file:
        return file.read()
        
def write_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')
    
def setup():
    print("You have entered the config\n")
    print("1/3\n")
    config["dedicated_server_mods_setup"] = input("Where is your mod dedicated_server_mods_setup.lua file located?\n\nIf you are uncertain, you may have installed it via this guide:\nhttps://dontstarve.fandom.com/wiki/Guides/Don%E2%80%99t_Starve_Together_Dedicated_Servers\nand it is likely located somewhere such as /home/(user)/steamapps/DST/mods/dedicated_server_mods_setup.lua\n\nExample path (dont use quotes): '/home/steam/steamapps/DST/mods/dedicated_server_mods_setup.lua'\n>")
    if config["dedicated_server_mods_setup"] == "q" or config["dedicated_server_mods_setup"] == "quit":
        sys.exit()    
    if os.path.isfile(config["dedicated_server_mods_setup"]) == False:
        print("That is incorrect. '{}' is not a valid path. You may have made a typo. Resetting config.".format(config["dedicated_server_mods_setup"]))
        setup()
    elif "dedicated_server_mods_setup.lua" not in config["dedicated_server_mods_setup"]:
        print("That is incorrect. Please point me to the right file. What you type should end in 'dedicated_server_mods_setup.lua'. You may have made a typo. Resetting config.".format(config["dedicated_server_mods_setup"]))
        setup()
    else:
        print("Sweet! Looks like that was it.\n")
        print("2/3\n")
        config["modoverrides_path"] = input("Now i just need to know where your MASTER (aka overworld) modoverrides.lua is located.\n\nLocated at something like ~/.klei/DoNotStarveTogether/YourServerNameHere/Master/modoverrides.lua.\n\nExample path (dont use quotes): '/home/steam/.klei/DoNotStarveTogether/MyDediServer/Master/modoverrides.lua'\n>")
        if config["modoverrides_path"] == "q" or config["dedicated_server_mods_setup"] == "quit":
            sys.exit()    
        if os.path.isfile(config["modoverrides_path"]) == False:
            #clear()
            print("That is incorrect. '{}' is not a valid path. You may have made a typo. Resetting config.".format(config["modoverrides_path"]))
            setup()
        elif "modoverrides.lua" not in config["modoverrides_path"]:
            print("That is incorrect. Please point me to the right file. What you type should end in 'modoverrides.lua'. You may have made a typo. Resetting config.")
            setup()
        else:
            #clear()
            print(">{}\n".format(config["modoverrides_path"]))
            print("Sweet! Looks like that was it.\n")
            print("3/3\n")
            config["modoverrides_path2"] = input("Now i just need to know where your CAVES modoverrides.lua is located.\n\nLocated at something like ~/.klei/DoNotStarveTogether/YourServerNameHere/Caves/modoverrides.lua.\n\nExample path (dont use quotes): '/home/steam/.klei/DoNotStarveTogether/MyDediServer/Caves/modoverrides.lua'\n>")
            if config["modoverrides_path2"] == "q" or config["dedicated_server_mods_setup"] == "quit":
                sys.exit()    
            if os.path.isfile(config["modoverrides_path2"]) == False:
                #clear()
                print("That is incorrect. '{}' is not a valid path. You may have made a typo. Resetting config.".format(config["modoverrides_path2"]))
                setup()
            elif "modoverrides.lua" not in config["modoverrides_path2"]:
                print("That is incorrect. Please point me to the right file. What you type should end in 'modoverrides.lua'. You may have made a typo. Resetting config.")
                setup()
    clear()
    config["configured"] = True
    write_to_pickle()
    print("Looks like youre all set! Enjoy your fun, just make sure you dont starve!")
    print("Exiting config!\n")

def apply_operation(id, options):
    modoverride = read_file(config["modoverrides_path"])
    modoverride2 = read_file(config["modoverrides_path2"])
    modsettings = read_file(config["dedicated_server_mods_setup"])
    if modoverride == '' or os.stat(config["modoverrides_path"]).st_size == 0:
        modoverride = "return {\n\n}"
    if modoverride2 == '' or os.stat(config["modoverrides_path2"]).st_size == 0:
        modoverride2 = "return {\n\n}"
    new_str_modsettings = 'ServerModSetup("{}")\n'.format(id) + modsettings
    new_str_modoverride = 'return {\n["workshop-%s"]={ configuration_options={  }, enabled=true },\n'%id + modoverride.replace("return {\n", "").replace("return {","").replace("return{","")
    new_str_modoverride2 = 'return {\n["workshop-%s"]={ configuration_options={  }, enabled=true },\n'%id + modoverride2.replace("return {\n", "").replace("return {","").replace("return{","")
    str_options = ""
    if len(options) > 0:
        for option in options:
            str_options += "{}={}, ".format(option, options[option]) #Key - value
        new_str_modoverride2.replace("configuration_options={  }","configuration_options=" + "{ " + str_options + " }")
    write_file(config["dedicated_server_mods_setup"], new_str_modsettings)
    write_file(config["modoverrides_path"], new_str_modoverride)
    write_file(config["modoverrides_path2"], new_str_modoverride2)

def fix_files():
    open(config["modoverrides_path"], 'w').close()
    open(config["modoverrides_path2"], 'w').close()
    write_file(config["modoverrides_path"], "return {\n\n}")
    write_file(config["modoverrides_path2"], "return {\n\n}")
    open(config["dedicated_server_mods_setup"], 'w').close()

def generate_configs():
    global generated_configs, table_parse_function
    generated_configs = {}
    dir_path = os.path.dirname(config["dedicated_server_mods_setup"]) #workshop-378160973 is the mod folder format

    for x in mod_dict:
        temp_read = """
                    configuration_options = {}
        """
        try:
            if name == 'nt':
                temp_read = read_file("{}\workshop-{}\modinfo.lua".format(dir_path, x)) #imports the modinfo.lua as string
            else:
                temp_read = read_file("{}/workshop-{}/modinfo.lua".format(dir_path, x)) #imports the modinfo.lua as string
        except Exception as e:
            pass
        

        if "configuration_options =" not in temp_read and "configuration_options=" not in temp_read:
            lua.execute("configuration_options = {}")
        lua.execute(temp_read)                   #Execute the lua file
        lua.execute(table_parse_function)  #Execute my lua function
        temp_read = "configuration_options =" + lua.eval('new_string2')     #Get the string of lua table data!

        
        new_code = temp_read.replace("  ","").strip()
        if "configuration_options=" in new_code:
            list1 = slpp.decode(new_code.split("configuration_options=")[1].strip())
        elif "configuration_options =" in new_code:
            list1 = slpp.decode(new_code.split("configuration_options =")[1].strip()) #list1 is the list of dictionaries.
        else:
            list1 = {}

        generated_configs[x] = list1

def read_config():
    global cur_config
    modoverride = read_file(config["modoverrides_path"])
    modoverride2 = read_file(config["modoverrides_path2"])
    red_code = modoverride.replace("return", "").strip()#.replace("  ", "")
    red_code2 = modoverride.replace("return", "").strip()#.replace("  ", "")
    try:
        cur_config = slpp.decode(red_code)
        slpp.decode(red_code2)
    except Exception as e:
        print(e)
        z = input("Looks like you have a corrupt lua file. Would you like to reset your lua mod files?\nyes/y or no/n\n>")
        if z.strip().lower() in ["yes", "y"]:
            fix_files()
            print("Files fixed! Please restart program...")
            sys.exit()
        else: 
            print("Cant continue... exiting. Please fix the files yourself or allow this program to wipe the files.")
            sys.exit()
    

def write_config(id):
    global generated_configs, cur_config
    
    with open(config["modoverrides_path"], 'r') as fr: #Read the file and check where are all the lines are for this mod (id)
        lines = fr.readlines()
        startop = -1
        endop = -1
        t = -1
        remove_lines = []
        for to_remove in lines:
            t = t + 1
            if '["workshop-{}"]'.format(id) in to_remove:
                startop = t
            if ('["workshop' in to_remove and startop != -1 and '["workshop-{}"]'.format(id) not in to_remove) or (t == len(lines) and startop != -1 and '["workshop-{}"]'.format(id) not in to_remove):
                if t == len(lines):
                    endop = t + 1
                else:
                    endop = t
        if startop != -1 and endop == -1:
            endop = len(lines)
        if startop != -1 and endop != -1:
            for x in range(startop, endop):
                remove_lines.append(x)
        lp = 0
        with open(config["modoverrides_path"], 'w') as fw: #delete the lines for the mod
            for line in lines:
                if lp not in remove_lines:
                    fw.write(line)
                lp += 1
                
    with open(config["modoverrides_path2"], 'r') as fr: #Read the file and check where are all the lines are for this mod (id)
        lines = fr.readlines()
        startop = -1
        endop = -1
        t = -1
        remove_lines = []
        for to_remove in lines:
            t = t + 1
            if '["workshop-{}"]'.format(id) in to_remove:
                startop = t
            if ('["workshop' in to_remove and startop != -1 and '["workshop-{}"]'.format(id) not in to_remove) or (t == len(lines) and startop != -1 and '["workshop-{}"]'.format(id) not in to_remove):
                if t == len(lines):
                    endop = t + 1
                else:
                    endop = t
        if startop != -1 and endop == -1:
            endop = len(lines)
        if startop != -1 and endop != -1:
            for x in range(startop, endop):
                remove_lines.append(x)
        lp = 0
        with open(config["modoverrides_path2"], 'w') as fw: #delete the lines for the mod
            for line in lines:
                if lp not in remove_lines:
                    fw.write(line)
                lp += 1
                

    modoverride = read_file(config["modoverrides_path"])
    modoverride2 = read_file(config["modoverrides_path2"])
    if modoverride == '' or os.stat(config["modoverrides_path"]).st_size == 0:
        modoverride = "return {\n\n}"
    if modoverride2 == '' or os.stat(config["modoverrides_path2"]).st_size == 0:
        modoverride2 = "return {\n\n}"
    
    new_str_modoverride = 'return {\n["workshop-%s"]={ configuration_options={  }, enabled=true },\n'%id + modoverride.replace("return {\n", "").replace("return {","").replace("return{","")
    new_str_modoverride2 = 'return {\n["workshop-%s"]={ configuration_options={  }, enabled=true },\n'%id + modoverride2.replace("return {\n", "").replace("return {","").replace("return{","")
    str_options = ""
    line_to_append = ""
    try:
        cur_config["workshop-{}".format(id)]['configuration_options']
    except Exception as e:
        print(e)
        z = input("Looks like you have a corrupt lua file. Would you like to reset your lua mod files?\nyes/y or no/n\n>")
        if z.strip().lower() in ["yes", "y"]:
            fix_files()
            print("Files fixed! Please restart program...")
            sys.exit()
        else: 
            print("Cant continue... exiting. Please fix the files yourself or allow this program to wipe the files.")
            sys.exit()        
        
    if len(cur_config["workshop-{}".format(id)]['configuration_options']) > 0:
        for option in cur_config["workshop-{}".format(id)]['configuration_options']:
            if isinstance(cur_config["workshop-{}".format(id)]['configuration_options'][option], str) and "&Zenzerker_Value" not in cur_config["workshop-{}".format(id)]['configuration_options'][option]:
                str_options += '["{}"]={}, '.format(option, '"{}"'.format(cur_config["workshop-{}".format(id)]['configuration_options'][option])) #Key - value
            elif cur_config["workshop-{}".format(id)]['configuration_options'][option] == "true&Zenzerker_Value":
                str_options += '["{}"]=true, '.format(option) #Key - value
            elif cur_config["workshop-{}".format(id)]['configuration_options'][option] == "false&Zenzerker_Value":
                str_options += '["{}"]=false, '.format(option) #Key - value
            elif cur_config["workshop-{}".format(id)]['configuration_options'][option] == "nil&Zenzerker_Value":
                str_options += '["{}"]=nil, '.format(option) #Key - value
            else:
                str_options += '["{}"]={}, '.format(option, cur_config["workshop-{}".format(id)]['configuration_options'][option])
        new_str_modoverride2 = new_str_modoverride2.replace('["workshop-%s"]={ configuration_options={  '%id,'["workshop-%s"]={ configuration_options={  '%id + str_options)
        new_str_modoverride = new_str_modoverride.replace('["workshop-%s"]={ configuration_options={  '%id,'["workshop-%s"]={ configuration_options={  '%id + str_options)
    elif len(cur_config["workshop-{}".format(id)]['configuration_options']) == 0 and len(generated_configs[id]) > 0:
        for iter in generated_configs[id]:
            try:
                iter["default"]
            except:
                continue
            if isinstance(iter["default"], str) and "&Zenzerker_Value" not in iter["default"]:
                if iter["name"] != "":
                    value_to_append = '["{}"]={}, '.format(iter["name"], '"{}"'.format(iter["default"]))
            elif iter["default"] == "true&Zenzerker_Value":
                value_to_append = '["{}"]=true, '.format(iter["name"]) #Key - value
            elif iter["default"] == "false&Zenzerker_Value":
                value_to_append = '["{}"]=false, '.format(iter["name"]) #Key - value
            elif iter["default"] == "nil&Zenzerker_Value":
                value_to_append = '["{}"]=nil, '.format(iter["name"]) #Key - value
            else:
                if iter["name"] != "":
                    value_to_append = '["{}"]={}, '.format(iter["name"], iter["default"])
            line_to_append += value_to_append
        new_str_modoverride2 = new_str_modoverride2.replace('["workshop-%s"]={ configuration_options={  }'%id,'["workshop-%s"]={ configuration_options={  '%id + line_to_append + "  }")
        new_str_modoverride = new_str_modoverride.replace('["workshop-%s"]={ configuration_options={  }'%id,'["workshop-%s"]={ configuration_options={  '%id + line_to_append + "  }")

    if new_str_modoverride.replace("\n","").replace("\r","").replace(" ","").replace("\t","")[-1] != "}":
        write_file(config["modoverrides_path"], new_str_modoverride+"\n}")
        write_file(config["modoverrides_path2"], new_str_modoverride2+"\n}")
    else:
        write_file(config["modoverrides_path"], new_str_modoverride+"\n")
        write_file(config["modoverrides_path2"], new_str_modoverride2+"\n")

def config_mods_submenu(id):
    global mod_dict, generated_configs, cur_config
    clear()
    print("You have entered the configuration for {}  -  {}\n".format(id, mod_dict[id]))
    try:
        while True:
            i_dict = {}
            i = 0
            dict_config = {}
            for items in generated_configs[id]:
                append_string = '\noptions ='
                for options in items["options"]:
                    append_string += (' [{} = {}] '.format(options['data'], options['description']))
                try:
                    dict_config[items["name"]] = 'Info: {}{}'.format(items["hover"], append_string).replace("&Zenzerker_Value","")
                except KeyError as e:
                    try:
                        dict_config[items["name"]] = 'Info: {}{}'.format(items["label"], append_string).replace("&Zenzerker_Value","")
                    except:
                        dict_config[items["name"]] = "Sorry, the author included no info for this setting."
                except Exception as e:
                    dict_config[items["name"]] = "Sorry, i ran into an error there. Looks like i am either a terrible programmer, or your modinfo.lua is missing information. Sorry about that."
            for mod_option in cur_config["workshop-{}".format(id)]["configuration_options"]:
                i+=1
                i_dict[i] = mod_option
                print("\n{}. {} = {}   {}".format(i, mod_option, str(cur_config["workshop-{}".format(id)]["configuration_options"][mod_option]).replace("&Zenzerker_Value",""), dict_config[mod_option]))
            grab_item = input("\n\nWhat setting would you like to configure? (Enter number only)\n>")
            if grab_item in ["q", "quit"]:
                clear()
                break
            try:
                grab_item = int(grab_item)
                i_dict[int(grab_item)]
            except Exception as e:
                clear()
                print(e)
                print("Whoa! '{}' Is not an option. Please type the number of the option you would like.".format(grab_item))
                continue
            new_value = input('Please set the value, or leave blank to cancel.\n{} = '.format(i_dict[grab_item])).strip()
            
            if new_value == "":
                continue
            if '.' in new_value:
                try:
                    new_value = float(new_value)   #All this stuff procedurally recognizes if the input is a float, int, string, bool or none. Which are the only types that matter for identifying.
                except:
                    pass
            else:
                try:
                    new_value = int(new_value)
                except:
                    pass
            if "&Zenzerker_Value" in str(cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]]) and new_value == "true":
                cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]] = "{}&Zenzerker_Value".format(new_value)
            elif "&Zenzerker_Value" in str(cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]]) and new_value == "false":
                cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]] = "{}&Zenzerker_Value".format(new_value)
            elif "&Zenzerker_Value" in str(cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]]) and new_value == "nil":
                cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]] = "{}&Zenzerker_Value".format(new_value)
            else:    
                cur_config["workshop-{}".format(id)]["configuration_options"][i_dict[grab_item]] = new_value
            
            for id in mod_dict:
                write_config(id)
            read_config()
            clear()
    except Exception as e:
        #clear()
        traceback.print_exc()
        print(e)
        print("Some sort of error occured with the configuration. Maybe lua files are corrupt? I can attempt to regenerate your configs.")
        ques = input('May i wipe your mod settings to regenerate them?\n>')
        if ques.strip().lower() in ["yes", "y"]:
            fix_files()
        else:
            print("Not wiping mods. I will be unable to continue without fixing them. Exiting...")
            sys.exit()
            


def config_mods():
    global mod_dict, generated_configs, cur_config
    clear()
    print("You have entered configuration.\nHere you can configure your mod's settings.\n")
    while True:
        print("help/h for help - quit/q to return to main screen\n")
        for x in mod_dict:
            print("{} - {}".format(x, mod_dict[x]))
        var3 = input("\nType the ID of which mod you would like to configure settings for:\n>").replace(" ","")
        if var3 == "q" or var3 == "quit":
            clear()
            print(">{}".format(var3))
            return
        try:
            mod_dict[var3]
        except Exception as e:
            clear()
            print(e)
            print("Whoops! There was an error. {} Does not exist in your installed mods. Make sure you are typing the listed mod ID".format(var3))
            continue
        config_mods_submenu(var3)
        generate_configs()
        read_config()
        for id in mod_dict:
            write_config(id)

def main_run():
    global mods, config, configured, mod_dict
    if config["configured"] == False:
        #clear()
        print("Hey there! Looks like this is your first time using the program. This program automatically installs, removes and configures mods for DST dedicated servers.\n\nI just need some basic information about your DST server.")
        print("\nJust a heads up, i recommend backing up your dedicated_server_mods_setup.lua and modoverrides.lua files before using this program, as it does TRY to parse human edited text files, it isn't perfect (yet). This program is still in development and is only available right now for testing purposes before release. With that said, it is currently very stable and works well- with some smaller bugs. Enjoy the program!\n")
        setup()
    else:
        clear()
    temp = read_file(config["dedicated_server_mods_setup"]).split("\n")
    mods = []
    for x in temp:
        if "ServerModSetup(" in x and "--" not in x:
            mods.append(x.split('"')[1])
    print("\nhelp/h for help - setup/s for setup - quit/q to exit\nremove/r to remove a mod - fix/f to clear all mod files (recommended if using for first time or issues)\n")
    print("You currently have {} mods.\n".format(len(mods)))
    mod_dict = {}
    for x in mods:
        try:
            url='https://steamcommunity.com/sharedfiles/filedetails/?id={}'.format(x)
            content = urlopen(url).read()
            soup = BeautifulSoup(content, "html.parser")
            rows = soup.find_all('div',attrs={"class" : "workshopItemTitle"})
            nx = rows[0].text
        except Exception as e:
            nx = "Unknown mod - cant reach page 'https://steamcommunity.com/sharedfiles/filedetails/?id={}'".format(x)
        mod_dict[x] = nx
        print("{} - {}".format(x, nx))
    generate_configs()
    read_config()
    for id in mod_dict:
        write_config(id)
    var = input("\nWhat mod would you like to add? (Input steam workshop id only)\n>").replace(" ","")
    if var == "s" or var == "setup":
        clear()
        setup()
        main_run()
    elif var == "c" or var == "config":
        config_mods()
    elif var == "h" or var == "help":
        clear()
        print("""Go to your browser and go to https://steamcommunity.com/app/322330/workshop/ from there, look for a mod you would like. 
Click that mod, and in the URL you will find the mod ID after ?id= make sure to only copy the numbers. Paste that into this program to install the mod and have it automatically configured. 
Make sure to only install server-only mods. From there, to configure the mod you must first run the server, so it can download all the mod data. 
After doing so, run this program again and you shall find configuration options available if the mod has configurable options. If this program is behaving unexpectedly, you may need to reformat your mods. 
To do so, type 'f' or 'fix' into the program and all mod data will be wiped. From there just re-enter the mod ids for it to reinstall them. If you are still having trouble after that,
It may be that your modinfo.luas are corrupt in some way. Perhaps a mod creator uploaded an incomplete/incorrect modinfo.lua with their mod. 
You can go to {} and delete all the workshop-MODIDHERE folders. Dont worry, the server will automatically reinstall these files once run again. 
Also, make sure you set the correct paths for your DST server lua files during this program's setup. To start the setup again, type 's' or 'setup'.""".format(os.path.dirname(config["dedicated_server_mods_setup"])))
        main_run()
    elif var == "f" or var == "fix":
        clear()
        print("fixing!")
        fix_files()
        main_run()
    elif var == "q" or var == "quit":
        sys.exit()
    elif var == "r" or var == "remove":
        print("Current mods:")
        mod_dict = {}
        for x in mods:
            try:
                url='https://steamcommunity.com/sharedfiles/filedetails/?id={}'.format(x)
                content = urlopen(url).read()
                soup = BeautifulSoup(content, "html.parser")
                rows = soup.find_all('div',attrs={"class" : "workshopItemTitle"})
                nx = rows[0].text
            except Exception as e:
                nx = "Unknown mod - cant reach page 'https://steamcommunity.com/sharedfiles/filedetails/?id={}'".format(x)
            mod_dict[x] = nx
            print("{} - {}".format(x, nx))

        var2 = input("What mod would you like to remove? (type ID number)\n>").replace(" ","")
        if var == "h" or var == "help":
            clear()
            print("""Go to your browser and go to https://steamcommunity.com/workshop/browse/?appid=322330&requiredtags[]=server_only_mod from there, look for a mod you would like. 
Click that mod, and in the URL you will find the mod ID after ?id= make sure to only copy the numbers. Paste that into this program to install the mod and have it automatically configured. 
Make sure to only install server-only mods. From there, to configure the mod you must first run the server, so it can download all the mod data. 
After doing so, run this program again and you shall find configuration options available if the mod has configurable options. If this program is behaving unexpectedly, you may need to reformat your mods. 
To do so, type 'f' or 'fix' into the program and all mod data will be wiped. From there just re-enter the mod ids for it to reinstall them. If you are still having trouble after that,
It may be that your modinfo.luas are corrupt in some way. Perhaps a mod creator uploaded an incomplete/incorrect modinfo.lua with their mod. 
You can go to {} and delete all the workshop-MODIDHERE folders. Dont worry, the server will automatically reinstall these files once run again. 
Also, make sure you set the correct paths for your DST server lua files during this program's setup. To start the setup again, type 's' or 'setup'.""".format(os.path.dirname(config["dedicated_server_mods_setup"])))
            main_run()
        try:
            int(var2)
            temp2 = read_file(config["dedicated_server_mods_setup"]).replace('ServerModSetup("{}")\n'.format(var2), "")
            temp3 = read_file(config["modoverrides_path"])
            temp4 = read_file(config["modoverrides_path2"])
            with open(config["modoverrides_path"], 'r') as fr:
                lines = fr.readlines()
                startop = -1
                endop = -1
                t = -1
                remove_lines = []
                for to_remove in lines:
                    t = t + 1
                    if '["workshop-{}"]'.format(var2) in to_remove:
                        startop = t
                    if ('["workshop' in to_remove and startop != -1 and '["workshop-{}"]'.format(var2) not in to_remove) or (t == len(lines) and startop != -1 and '["workshop-{}"]'.format(var2) not in to_remove):
                        if t == len(lines):
                            endop = t + 1
                        else:
                            endop = t
                if startop != -1 and endop == -1:
                    endop = len(lines)
                if startop != -1 and endop != -1:
                    for x in range(startop, endop):
                        remove_lines.append(x)
                lp = 0
                with open(config["modoverrides_path"], 'w') as fw:
                    for line in lines:
                        if lp not in remove_lines:
                            fw.write(line)
                        lp += 1
            with open(config["modoverrides_path2"], 'r') as fr:
                lines = fr.readlines()
                startop = -1
                endop = -1
                t = -1
                remove_lines = []
                for to_remove in lines:
                    t = t + 1
                    if '["workshop-{}"]'.format(var2) in to_remove:
                        startop = t
                    if ('["workshop' in to_remove and startop != -1 and '["workshop-{}"]'.format(var2) not in to_remove) or (t == len(lines) and startop != -1 and '["workshop-{}"]'.format(var2) not in to_remove):
                        if t == len(lines):
                            endop = t + 1
                        else:
                            endop = t
                if startop != -1 and endop == -1:
                    endop = len(lines)
                if startop != -1 and endop != -1:
                    for x in range(startop, endop):
                        remove_lines.append(x)
                lp = 0
                with open(config["modoverrides_path2"], 'w') as fw:
                    for line in lines:
                        if lp not in remove_lines:
                            fw.write(line)
                        lp += 1
            write_file(config["dedicated_server_mods_setup"], temp2)
            for id in mod_dict:
                write_config(id)
            clear()
            print("Mod {} - '{}' removed.\n".format(var2, mod_dict[var2]))
            main_run()
        except Exception as e:
            clear()
            print(e)
            print(">"+var2)
            print("Whoa there! '{}' is incorrect input. Please type one of the number IDs listed above. Restarting...".format(var2))
            main_run()
    else:
        try:
            int(var)
        except:
            clear()
            print(">"+var)
            print("Whoa there! '{}' is incorrect input. For examples and help, type help or h.".format(var))
            main_run()
        apply_operation(var, {})
        clear()
        print("Mod {} added!".format(var))
        main_run()
    clear()
    main_run()
    
#clear()
print("Welcome to Zenzerker's Mod Manager for Don't Starve Together!\n")
main_run()
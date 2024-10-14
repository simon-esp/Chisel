global vars
vars = {}
global blacklist
blacklist = [
    'os.system(',           
    'os.popen(',            
    'os.spawn(',            
    'os.exec(',             
    'os.startfile(',        
    'subprocess.Popen(',    
    'subprocess.call(',     
    'subprocess.run(',      
    'subprocess.check_output(', 
    'shutil.rmtree(',       
    'shutil.move(',         
    'shutil.copyfile(',     
    'os.remove(',           
    'os.rmdir(',            
    'os.unlink(',           
    'os.rename(',           
    'os.chmod(',            
    'os.chown(',            
    'socket.socket(',       
    'threading.Thread(',    
    'multiprocessing.Process(', 
    'eval(',                
    'exec(',                
    'open(',                
    'ctypes.CDLL(',         
    'ctypes.windll(',       
    'ctypes.cdll(',         
    'ctypes.create_string_buffer(', 
]

def parse(p):
    """ I forgot how this works, i just know it works
        Splits by `;`, removes indents, and removes comments formatted like ~comment~
        Comments are multi or single line
        This took me a couple hours to cook up  """

    s = ''.join(p.splitlines())
    nesting = 0
    final = []
    comment = False
    string = ''
    indent = True
    for l, i in enumerate(s):
        if not l == len(s) - 1:
            if i == '~':
                comment = not comment
        if i == '{' and not comment:
            nesting += 1
        if i == '}' and not comment:
            nesting -= 1
        if i == '[' and not comment:
            nesting += 1
        if i == ']' and not comment:
            nesting -= 1
        if i == '(' and not comment:
            nesting += 1
        if i == ')' and not comment:
            nesting -= 1
        if not i == ' ':
            indent = False
        if i == ';' and nesting == 0 and not comment:
            final.append(string)
            string = ''
            indent = True
        elif not indent and not comment and not i == '~':
            string += i
    return final

def find_functions(p):
    funcs_temp = {}
    for i in p:
        if i.startswith('fn '):
            func_name = i.split(' ')[1].split(':')[0]
            func_body = ':'.join(i.split(':')[1:])[1:-1]
            parsed_body = parse(func_body)
            funcs_temp[func_name] = parsed_body
    return funcs_temp

def contains_any(string, array):
    # Loop through each item in the array
    for item in array:
        if item in string:
            return True
    return False

def evalf(expression):
    # This didnt take very long surprisingly
    global vars
    # Replace all vars with their corresponding value in the vars dict
    expr = expression
    for i in vars:
        expr = expr.replace(i, str(vars[i]))

    # Check if expression is dangerous
    if contains_any(expr, blacklist):
        raise Exception("Blacklisted expression")
    else:
        pass

    try:
        # Try to literal_eval the expression
        result = eval(expr)
        return result
    except (ValueError, SyntaxError):
        # Chatgpt forced me to include error handling
        # Help me get my testicles back by making stable code
        raise Exception(f"Invalid expression or unsupported operation with `{expr}`")

def parse_args(a):
    # This shit took me 2 hours and the problem wasnt even here
    # I hated every second of it
    # Splits arguments by commas but is dynamicly typed like `1,      2,skibidi,4,  5` outputs `[1,2,skibidi,4,5]`
    nest1 = 0
    nest2 = 0
    nest3 = 0
    quotes = False
    string = ""
    product = []
    
    for i in a:
        if i == '(':
            nest1 += 1
        elif i == ')':
            nest1 -= 1
        elif i == '[':
            nest2 += 1
        elif i == ']':
            nest2 -= 1
        elif i == '{':
            nest3 += 1
        elif i == '}':
            nest3 -= 1
        elif i == '"':
            quotes = not quotes

        #  ↑  Checked for quotes / brackets

        if not quotes:
            if i == ',' and not (nest1 or nest2 or nest3): #Basicly `ìf its a comma and not nested`
                product.append(string.strip()) #
                string = ""
            elif not i.isspace() or string: # Chatgpt made this line, i have no clue what it means
                string += i
        else:
            string += i
    
    # Add the last argument if not empty then return
    if string:
        product.append(string.strip())
    return product

def exec(l):
    global vars
    # Get args and cmd
    cmd = l.split(' ')[0]
    args = parse_args(' '.join(l.split(' ')[1:]))
    # Execute with cmd as command and args (array) for arguments
    if cmd == "log":
        print(evalf(args[0]))
    if cmd == "var":
        vars[evalf(args[0])] = f'"{evalf(args[1])}"'
    if cmd == "pyeval":
        eval(evalf(args[0]))

def lbl(a):
    # Do line-by-line execution
    for i in a:
        # This is how to run a single line btw
        exec(i)

lbl(parse('var "hello","world"; log hello; pyeval "print(\'hello verden\')";'))

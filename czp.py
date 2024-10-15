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
    quotes = False
    # Go through each character in the string
    for i, char in enumerate(string):
        # Check for opening or closing quotes
        if char == '"' or "'":
            quotes = not quotes  # Toggle the quotes
        
        # If not in quotes, check for niggalist words
        if not quotes:
            for item in array:
                if item in string[i:i+len(item)]:
                    return item
    
    return False

def replace_vars_in_expr(expr, vars):
    in_quotes = False
    modified_expr = []
    i = 0

    while i < len(expr):
        char = expr[i]

        if char == '"':
            in_quotes = not in_quotes

        if not in_quotes:
            for var in vars:
                var_len = len(var)
                if expr[i:i + var_len] == var and (i + var_len == len(expr) or not expr[i + var_len].isalnum()):
                    # Directly append the value, leaving it as an int/float or string
                    modified_expr.append(vars[var])  # Append the variable's value
                    i += var_len - 1  # Skip the length of the variable
                    break
            else:
                modified_expr.append(char)  # Keep the character as is
        else:
            modified_expr.append(char)  # Keep the character as is

        i += 1

    # Now we evaluate the expression
    # Use a list comprehension to construct a proper expression string for eval
    expression = ''.join(str(x) if isinstance(x, (str, int, float)) else x for x in modified_expr)
    
    return expression  # Return the final expression to be evaluated

def evalf(expression):
    global vars
    # Replace all vars with their corresponding value in the vars dict
    expr = replace_vars_in_expr(expression, vars)

    # Check if expression is dangerous
    blacklisted = contains_any(expr, blacklist)
    if blacklisted:
        raise Exception(f"Blacklisted expression: `{expr}`\nIssue: {blacklisted} is blacklisted (dangerous)")
    else:
        pass

    try:
        # If expression is a single character or string, return it as is
        if expr.isalpha() and len(expr) == 1:
            return expr
        # Handle numerical values directly
        if expr.strip('-').strip('.').isnumeric():
            return int(expr)
        # Handle expressions with eval
        result = eval(expr)
        return result
    except (ValueError, SyntaxError) as e:
        # Handle literal strings or expressions
        if isinstance(expr, str):
            return expr
        raise Exception(f"Invalid expression or unsupported operation with `{expr}`\nError code: {e}")

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
    # Get args and cmd
    cmd = l.split(' ')[0]
    args = parse_args(' '.join(l.split(' ')[1:]))
    # Execute with cmd as command and args (array) for arguments
    if cmd == "print":
        print(evalf(args[0]))
    if cmd == "var":
        vars[args[0]] = f'"{evalf(args[1])}"'
    if cmd == "pyeval":
        eval(evalf(args[0]))
    if cmd == "if":
        if evalf(args[0]):
            lbl(parse(args[1][1:-1]))
        else:
            if len(args) >= 4:
                if args[2] == 'else':
                    lbl(parse(args[3][1:-1]))
    if cmd == "while":
        while evalf(args[0]):
            lbl(parse(args[1][1:-1]))
    if cmd == "for":
        for i in evalf(args[1]):
            vars[args[0]] = i
            lbl(parse(args[2][1:-1]))
    if cmd == "rep":
        for i in range(evalf(args[0])):
            lbl(parse(args[1][1:-1]))

def lbl(a):
    # Do line-by-line execution
    for i in a:
        # This is how to run a single line btw
        exec(i)

with open('test.czp', 'r') as f:
    script = f.read()
lbl(parse(script))

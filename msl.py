def parse(p):
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

def parse_args(a):
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

        if not quotes:  # Check if we are not inside quotes
            if i == ',' and not (nest1 or nest2 or nest3):
                # Only add to product if not inside any nests or quotes
                product.append(string.strip())
                string = ""
            elif not i.isspace() or string:  # Handle spaces and empty string
                string += i
        else:
            # If inside quotes, just add the character to string
            string += i
    
    # Add the last argument if not empty
    if string:
        product.append(string.strip())
    
    return product

def exec(l):
    cmd = l.split(' ')[0]
    args = parse_args(' '.join(l.split(' ')[1:]))
    if cmd == "log":
        print(args[0])

def lbl(a):
    for i in a:
        exec(i)

lbl(parse('log Hello World;'))
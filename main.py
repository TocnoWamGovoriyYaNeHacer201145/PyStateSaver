import inspect

def save_state(filename, globals):
    code = []
    for obj in globals:
        if obj in ('save_state', 'load_state', 'state', 
                   '__name__', '__package__', '__file__', 
                   '__cached__', '__doc__', '__loader__', 
                   '__spec__', '__builtins__'):
            continue

        globl_obj = globals[obj]
        if isinstance(globl_obj, int):
            code.append(f'{obj}:{globl_obj}')
        elif isinstance(globl_obj, str):
            code.append(f's:{obj}:{int.from_bytes(globl_obj.encode('utf-8'), byteorder='big')}')
        else:
            fun_source = inspect.getsource(globl_obj).encode('utf-8')
            code.append(f'fun:{obj}:{int.from_bytes(fun_source, byteorder='big')}')
    with open(filename, 'w') as f:
        f.write('\n'.join(code))

def load_state(filename, globals):
    with open(filename, 'r') as f:
        content = f.readlines()

    for line in content:
        line_objs = line.split(':')
        if len(line_objs) > 2:
            if line_objs[0] == 'fun':
                function_int = int(line_objs[-1])
                _source = function_int.to_bytes((function_int.bit_length() + 7) // 8, byteorder='big')
                var_content = _source.decode('utf-8')
            else:
                str_int = int(line_objs[-1])
                _source = str_int.to_bytes((str_int.bit_length() + 7) // 8, byteorder='big').decode('utf-8')
                var_content = f'{line_objs[1]} = {repr(_source)}'
        else:
            if line_objs[1].isdigit():
                line_objs[1] = int(line_objs[1])
            else:
                line_objs[1] = repr(line_objs[1])
            var_content = f'{line_objs[0]} = {line_objs[1]}'
        exec(var_content, globals=globals)

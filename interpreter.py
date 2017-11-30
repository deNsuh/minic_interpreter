import os
import re
import sys
import yacc
import operator
from astree import *
from symbol_table import Scope, Symbol


class SemanticError(Exception):
    def __init__(self, msg):
        self.msg = msg

# path where script exists
cfile_dir = './cfiles'
input_file = 'typecast.c'
input_file = os.path.join(cfile_dir, input_file)
parser = yacc.parser  # import the parser

# regular expression for id
id_regex = re.compile('[a-zA-Z_][a-zA-Z_0-9]*')

code_lines = []  # keep track of lines of code
try:
    s = ''
    with open(input_file, 'r') as f:
        for l in f.readlines():
            s += l
            code_lines.append(l)
except EOFError:
    print('EOFError')
code_lines.append('EOF')

# parsing step
try:
    ast_root = parser.parse(s, tracking=True)
    if len(parser.errorlines) > 0:
        for errorline in parser.errorlines:
            print('Parse Error at line :{}\n{}'.format(errorline, code_lines[errorline - 1]))
        raise Exception
except Exception as e:
    print('Parse Error')
    sys.exit(0)  # terminate the program...

if parser.main_func is None:
    raise SemanticError('No main function!')

errorlines =  parser.errorlines  # lines where syntax error occurred
print('Result AST tree')
ast_root.show()

# mark the starting line
curr_lineno = parser.main_func.linespan[0]  # starting line number of main()

# register function names - interpreter only recognizes the name
# and does not have function closure
root_scope = Scope(symbol_table={})
for func in parser.functions:
    root_scope.add_symbol(
            symbol_name=func.name(),
            symbol_info=Symbol(name=func.name(), astnode=func))
scope = root_scope  # current evaluation scope
root_scope.return_lineno = len(code_lines) - 1

# evaluation stack - initial stack with function call of main
main_call = FunctionCall(func_name=Id('main'), argument_list=ArgList([]))
main_call.linespan = (curr_lineno, len(code_lines))

exec_stack = [main_call]
call_stack = []
env = ExecutionEnvironment(exec_stack, curr_lineno, scope, call_stack)

# evalutaion loop
total_line = 0
numlines = 0
log = '--' * 10 + '\n'
while True:
    if numlines == 0:
        # get command
        print('Next line : {}'.format(code_lines[env.currline - 1]))
        command = input('Command:')  # next line

        # parse and do appropriate action per command
        if command == '':
            commandlst = ['next', '1']
        else:
            commandlst = command.strip().split()
        cmd = commandlst[0]

        if cmd == 'next':
            numlines = int(commandlst[1])
            log = '--' * 10 + '\n' # reset log
        elif cmd == 'print':
            symbolname = commandlst[1]

            # see if input variable is proper
            doesmatch = id_regex.match(symbolname)
            if not doesmatch:
                print('Invalid typing of the variable name')
            else:
                val = env.scope.getvalue(symbolname)
                if val is None:
                    print('Invisible variable')
                else:
                    print(val.printval())
            continue
        elif cmd == 'trace':
            varname = commandlst[1]
            symbol = env.scope.getsymbol(varname)
            if symbol is None:
                print('Invisible variable')
            else:
                for val, line_num in symbol.val_history:
                    val_print = val.printval()
                    print('{} = {} at line {}'.format(symbol.name, val_print, line_num))
            continue
        elif cmd == 'scope':
            # show scope stack of this environment
            env.scope.show()
            continue
        elif cmd == 'log':
            print(log)  # show log for value stack and execution stack
            continue

    # if it reaches this point, the intepreter is proceeding the lines
    currline = env.currline  # store the current execution line
    # handle syntax error
    if env.currline in errorlines:
        print('Syntax Error at line {} for line {}'.format(env.currline, total_line))
        break

    while True:
        stacklen = len(exec_stack)
        if stacklen == 0:  # indicates end of program
            break

        log += '***Executing {} - {}\n'.format(exec_stack[-1], exec_stack[-1].linespan)
        exec_done, env = exec_stack[-1].execute(env)

        # print stack values for debugging
        stack_val_print = ''
        for stack_val in env.value_stack:
            stack_val_print += (stack_val.__repr__() + ' :: ')
        log += 'value stack : {}\n'.format(stack_val_print)
        log += 'exec stack : {}\n'.format(env.exec_stack)

        if (not exec_done and len(exec_stack) == stacklen) or (currline != env.currline):
            break
    print(log)

    # update line number
    if currline == env.currline:
        env.update_currline(1)  # 1 line just for now
        # keep track of line numbers
        numlines -= 1
        total_line += 1

    # do booked updates (++, -- used as postfixes)
    env.exec_booked_updates()

    # end of program indicator
    if env.currline >= len(code_lines) or len(env.exec_stack) == 0:
        print('End of Program')
        break

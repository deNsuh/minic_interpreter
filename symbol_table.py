class Value:
    def __init__(self, vtype, val=None):
        assert isinstance(vtype, TypeVal)
        self.vtype = vtype  # TypeVal instance
        self.val = val  # the actual value (numbers, string literals, or None)

    def cast(self, casttype):
        if casttype.typename == 'float':
            self.val = float(val)
        elif casttype.typename == 'int':
            self.val = int(val)


class TypeVal:
    def __init__(self, typename: str, ptr=0):
        self.typename = typename  # boolean, int, float, type, string, function, void
        self.ptr = ptr  # pointer order

    def __eq__(self, other):
        pass

    def castable(self, other):
        # true if other can be casted to self
        pass


class Symbol:
    def __init__(self, name, astnode):
        self.name = name
        self.address = 0  # TODO: generate memory address
        self.astnode = astnode  # corresponding AST node
        self.val_history = []
        self.value = None  # Value instance


class FunctionVal(Value):
    def __init__(self, rtype, params, body):
        super().__init__(TypeVal('function'))
        self.rtype = rtype  # return type
        self.params = prams  # list of (type, symbolname) pairs
        self.body = body  # ast root of body (compound statement)


class Scope:
    """
    Scope node for scope tree.
    """
    def __init__(self, symbol_table: dict):
        self.symbol_table = symbol_table
        self.parent_scope = None
        self.return_type = None  #  TypeVal instance
        self.return_scope = None
        self.return_lineno = None
        self.return_val = False

    def get_return_val(self):
        if not self.return_val:
            return False  # the function has not been executed and returned yet
        return self.return_val


    def add_symbol(self, symbol_name: str, symbol_info: Symbol):
        if symbol_name not in self.symbol_table:
            self.symbol_table[symbol_name] = symbol_info
            return True
        return False  # already exists

    def getsymbol(self, sym_name):
        if sym_name in self.symbol_table:
            return self.symbol_table
        elif self.parent_scope is None:
            return None
        else:
            return self.parent_scope.getsymbol(sym_name)

    def set_value(self, sym_name, val, lineno):
        self.getsymbol(sym_name).value = val
        self.getsymbol(sym_name).val_history.append((val, lineno))

    def getvalue(self, sym_name):
        symbol = self.getsymbol(sym_name)
        if self.symbol is None:
            return None
        return symbol.value

    def root_scope(self):
        # returns the root scope of the program
        if self.parent_scope is None:
            return self
        else:
            return self.parent_scope.root_scope()
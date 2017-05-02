from case_ins_dict import CaseInsensitiveDict


class ExprType(object):
    def __init__(self, type: str, specific=None):
        self.type = type
        self.specific = specific

    def __cmp__(self, other):
        return self.type == other.type and self.specific == other.name

    def __str__(self):
        if self.specific:
            return "{}-{}".format(self.type, self.specific)
        return self.type

int_type = ExprType("int")
bool_type = ExprType("bool")
char_type = ExprType("char")
string_type = ExprType("string")
void_type = ExprType("void")
array_type = ExprType("array")


class Symbol(object):
    def __init__(self, name, mode, declaration=None):
        self.name = name
        self.mode = mode
        self.declaration = declaration


class SymbolTable(CaseInsensitiveDict):
    """
    Class representing a symbol table. It should
    provide functionality for adding and looking
    up nodes associated with identifiers.
    """
    def __init__(self, decl=None):
        super().__init__()
        self.decl = decl

    def add(self, name, value):
        self[name] = value

    def lookup(self, name):
        return self.get(name, None)

    def return_type(self):
        if self.decl:
            return self.decl.mode
        return None


class Environment(object):
    def __init__(self, root_dict:CaseInsensitiveDict=None):
        self.stack = []
        self.root = SymbolTable()
        self.stack.append(self.root)
        if root_dict:
            self.root.update(root_dict)
    def push(self, enclosure):
        self.stack.append(SymbolTable(decl=enclosure))
    def pop(self):
        self.stack.pop()
    def peek(self):
        return self.stack[-1]
    def scope_level(self):
        return len(self.stack)
    def add_local(self, name, value):
        self.peek().add(name, value)
    def add_root(self, name, value):
        self.root.add(name, value)
    def lookup(self, name):
        for scope in reversed(self.stack):
            hit = scope.lookup(name)
            if hit is not None:
                return hit
        return None
    def find(self, name):
        if name in self.stack[-1]:
            return True
        else:
            return False


class Context:
    def __init__(self):
        self.mode_env = self.get_default_mode_env()
        self.var_env = self.get_default_var_env()

    def reset(self):
        self.mode_env = self.get_default_mode_env()
        self.var_env = self.get_default_var_env()

    @staticmethod
    def get_default_mode_env():
        return Environment(CaseInsensitiveDict({
            "int": int_type,
            "char": char_type,
            "string": string_type,
            "bool": bool_type,
            "void": void_type
        }))

    @staticmethod
    def get_default_var_env():
        return Environment()


cur_context = Context()
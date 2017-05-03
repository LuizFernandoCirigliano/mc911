from case_ins_dict import CaseInsensitiveDict


class ExprType(object):
    def __init__(self, expr_type: str, detail: object =None):
        self.type = expr_type
        self.detail = detail

    def __cmp__(self, other):
        return self.type == other.type and self.detail == other.detail

    def __str__(self):
        if self.detail:
            return "{}_{}".format(self.detail, self.type)
        return self.type

    @property
    def expr_type(self):
        return self

int_type = ExprType("int")
bool_type = ExprType("bool")
char_type = ExprType("char")
string_type = ExprType("string")
void_type = ExprType("void")
int_array_type = ExprType("array", int_type)
char_array_type = ExprType("array", char_type)


class Symbol(object):
    def __init__(self, name, mode: ExprType, declaration=None):
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
    def __init__(self, root_dict: CaseInsensitiveDict=None):
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
        self.var_env = Environment()

    def reset(self):
        self.mode_env = self.get_default_mode_env()
        self.var_env = Environment()

    @staticmethod
    def get_default_mode_env():
        return Environment(CaseInsensitiveDict({
            "int": int_type,
            "char": char_type,
            "string": string_type,
            "bool": bool_type,
            "void": void_type,
            "int_array": int_array_type,
            "char_array": char_array_type
        }))

    def insert_variables(self, var_list, var_mode: ExprType, declaration):
        if var_list is None:
            return True

        from errors import UndeclaredVariable, VariableRedeclaration
        valid_identifiers = True

        for identifier in var_list:
            identifier.issues = [x for x in identifier.issues if type(x) != UndeclaredVariable]
            if len(identifier.issues) == 0:
                identifier.__is_valid__ = True
            else:
                valid_identifiers = False

        for identifier in var_list:
            prev = self.var_env.find(identifier.name)
            if prev:
                prev_var = self.var_env.lookup(identifier.name)
                identifier.issues.append(
                    VariableRedeclaration(identifier.name,
                                          prev_var.declaration.line_number)
                )
                identifier.__is_valid__ = False
                valid_identifiers = False
            else:
                s = Symbol(identifier.name, var_mode, declaration)
                self.var_env.add_local(identifier.name, s)

        return valid_identifiers

cur_context = Context()

from case_ins_dict import CaseInsensitiveDict
from enum import Enum


class ExprType(object):
    def __init__(self, expr_type: str, detail: object =None):
        self.type = expr_type
        self.detail = detail

    def __eq__(self, other):
        return self.type == other.type and self.detail == other.detail

    def __str__(self):
        if self.detail:
            return "{}_{}".format(self.detail, self.type)
        return self.type

    @property
    def expr_type(self):
        return self

    @staticmethod
    def array_of_type(expr_type: object):
        return ExprType("array", expr_type)


class SymbolCategory(Enum):
    PROCEDURE = 1
    MODE = 2
    VARIABLE = 3
    ACTION = 4


class Symbol(object):
    def __init__(self, name, mode: ExprType, category: SymbolCategory, stack_level: int=None, stack_offset: int=None):
        self.name = name
        self.category = category
        self.expr_type = mode
        self.stack_level = stack_level
        self.stack_offset = stack_offset

    def __eq__(self, other):
        if self.category != other.category:
            return False
        if self.category == SymbolCategory.MODE:
            return self.expr_type == other.expr_type
        else:
            return self.name == other.name

    def __repr__(self):
        return "{} , name: {}, type: {}".format(self.category, self.name, self.expr_type)


class BuiltinSymbol(Symbol):
    def __init__(self, name, mode: ExprType, category: SymbolCategory):
        super().__init__(name, mode, category)


class VarSymbol(Symbol):
    def __init__(self, name, mode: ExprType, category: SymbolCategory, declaration=None):
        super().__init__(name, mode, category)
        self.declaration = declaration


int_symbol = BuiltinSymbol("int", ExprType("int"), SymbolCategory.MODE)
bool_symbol = BuiltinSymbol("bool", ExprType("bool"), SymbolCategory.MODE)
char_symbol = BuiltinSymbol("char", ExprType("char"), SymbolCategory.MODE)
string_symbol = BuiltinSymbol("string", ExprType("string", char_symbol.expr_type), SymbolCategory.MODE)
void_symbol = BuiltinSymbol("void", ExprType("void"), SymbolCategory.MODE)


class SymbolTable(CaseInsensitiveDict):
    """
    Class representing a symbol table. It should
    provide functionality for adding and looking
    up nodes associated with identifiers.
    """
    def __init__(self, decl=None):
        super().__init__()
        self.decl = decl
        self.var_count = 0

    def add(self, name: str, value: Symbol):
        if name in self:
            print("WARNING reassigning symbol")
        self[name] = value
        if value.category == SymbolCategory.VARIABLE:
            self.var_count += 1

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

    def add_local(self, name, symbol: Symbol):
        symbol.stack_offset = self.peek().var_count
        symbol.stack_level = self.scope_level() - 1
        self.peek().add(name, symbol)

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
        self.label_count = 0
        self.symbol_env = self.get_default_mode_env()

    def reset(self):
        self.symbol_env = self.get_default_mode_env()

    @staticmethod
    def get_default_mode_env():
        return Environment(CaseInsensitiveDict({
            int_symbol.name: int_symbol,
            char_symbol.name: char_symbol,
            string_symbol.name: string_symbol,
            bool_symbol.name: bool_symbol,
            void_symbol.name: void_symbol,
            'ABS': BuiltinSymbol('ABS', int_symbol.expr_type, SymbolCategory.PROCEDURE),
            'ASC': BuiltinSymbol('ASC', int_symbol.expr_type, SymbolCategory.PROCEDURE),
            'UPPER': BuiltinSymbol('UPPER', int_symbol.expr_type, SymbolCategory.PROCEDURE),
            'LOWER': BuiltinSymbol('LOWER', int_symbol.expr_type, SymbolCategory.PROCEDURE),
            'NUM': BuiltinSymbol('NUM', int_symbol.expr_type, SymbolCategory.PROCEDURE),
            'READ': BuiltinSymbol('READ', void_symbol.expr_type, SymbolCategory.PROCEDURE),
            'PRINT': BuiltinSymbol('PRINT', void_symbol.expr_type, SymbolCategory.PROCEDURE),
        }))

    def insert_symbol(self, var_list, var_mode: ExprType, category: SymbolCategory, declaration: object):
        if type(var_mode) != ExprType:
            raise TypeError(type(var_mode))

        if var_list is None:
            return True

        from errors import VariableRedeclaration
        valid_identifiers = True

        # for identifier in var_list:
        #     identifier.issues = [x for x in identifier.issues if type(x) != UndeclaredVariable]
        #     if len(identifier.issues) == 0:
        #         identifier.__is_valid__ = True
        #     else:
        #         valid_identifiers = False

        for identifier in var_list:
            prev = self.symbol_env.find(identifier.name)
            if prev:
                prev_var = self.symbol_env.lookup(identifier.name)
                line_number = prev_var.declaration.line_number if prev_var.declaration else None

                identifier.issues.append(VariableRedeclaration(identifier.name, line_number))
                identifier.__is_valid__ = False
                valid_identifiers = False
            else:
                s = VarSymbol(identifier.name, var_mode, category, declaration)
                self.symbol_env.add_local(identifier.name, s)

        return valid_identifiers

cur_context = Context()

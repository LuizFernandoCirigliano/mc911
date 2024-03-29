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
    ACTION = 3
    VARIABLE = 4
    VARIABLE_REF = 5
    PARAM = 6
    PARAM_REF = 7


class Symbol(object):
    def __init__(self, name, mode: ExprType, category: SymbolCategory,
                 stack_level: int=None, stack_offset: int=None, size=1):
        self.name = name
        self.category = category
        self.expr_type = mode
        self.display_level = stack_level
        self.offset = stack_offset
        self.size = size

    def __eq__(self, other):
        if self.category != other.category:
            return False
        if self.category == SymbolCategory.MODE:
            return self.expr_type == other.expr_type
        else:
            return self.name == other.name

    def __repr__(self):
        return "{} , name: {}, type: {}".format(self.category, self.name, self.expr_type)

    @property
    def loads_value(self):
        # ALL VARIABLES AND PARAMETERS
        return self.category.value >= SymbolCategory.VARIABLE.value

    @property
    def is_reference(self):
        return self.category == SymbolCategory.PARAM_REF or self.category == SymbolCategory.VARIABLE_REF


class ProcedureSymbol(Symbol):
    def __init__(self, name, mode: ExprType,
                 start_label: int =None,
                 formal_params: list =None,
                 builtin: bool =False):
        super().__init__(name, mode, SymbolCategory.PROCEDURE)
        self.start_label = start_label
        self.formal_params = formal_params
        self.builtin = builtin

    @property
    def num_args(self):
        if self.formal_params:
            return sum([len(param.identifier_list) for param in self.formal_params])
        else:
            return None


class BuiltinSymbol(Symbol):
    def __init__(self, name, mode: ExprType, category: SymbolCategory):
        super().__init__(name, mode, category)


class VarSymbol(Symbol):
    def __init__(self, name, mode: ExprType, category: SymbolCategory, declaration=None, size=1):
        super().__init__(name, mode, category, size=size)
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
        self.next_offset = 0

    def add(self, name: str, value: Symbol):
        if name in self:
            print("WARNING reassigning symbol")
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

    def add_local(self, name, symbol: Symbol, offset=None, level=None):
        symbol.offset = offset or self.peek().next_offset
        symbol.display_level = level or self.scope_level() - 1
        self.peek().add(name, symbol)
        if symbol.category == SymbolCategory.VARIABLE:
            self.peek().next_offset += symbol.size

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
        self.function_stack = []

    @staticmethod
    def get_default_mode_env():
        return Environment(CaseInsensitiveDict({
            int_symbol.name: int_symbol,
            char_symbol.name: char_symbol,
            string_symbol.name: string_symbol,
            bool_symbol.name: bool_symbol,
            void_symbol.name: void_symbol,
            'ABS': ProcedureSymbol('ABS', int_symbol.expr_type, builtin=True),
            'ASC': ProcedureSymbol('ASC', int_symbol.expr_type, builtin=True),
            'UPPER': ProcedureSymbol('UPPER', int_symbol.expr_type, builtin=True),
            'LOWER': ProcedureSymbol('LOWER', int_symbol.expr_type, builtin=True),
            'NUM': ProcedureSymbol('NUM', int_symbol.expr_type, builtin=True),
            'READ': ProcedureSymbol('READ', void_symbol.expr_type, builtin=True),
            'PRINT': ProcedureSymbol('PRINT', void_symbol.expr_type, builtin=True),
        }))

    def insert_symbol(self,
                      var_list,
                      var_mode: ExprType,
                      category: SymbolCategory,
                      declaration: object,
                      size=1):
        if var_list is None:
            return True

        from errors import VariableRedeclaration
        valid_identifiers = True

        for identifier in var_list:
            prev = self.symbol_env.find(identifier.name)
            if prev:
                # Verifica se variável já foi declarada
                prev_var = self.symbol_env.lookup(identifier.name)
                line_number = prev_var.declaration.line_number if prev_var.declaration else None

                identifier.issues.append(VariableRedeclaration(identifier.name, line_number))
                identifier.__is_valid__ = False
                valid_identifiers = False
            else:
                s = VarSymbol(identifier.name, var_mode, category, declaration, size=size)
                self.symbol_env.add_local(identifier.name, s)
                identifier.symbol = s

        return valid_identifiers

    def insert_procedure(self, proc_id_node, ret_type: ExprType,
                         start_label, declaration, formal_params,
                         display_level=1):
        from errors import VariableRedeclaration
        prev = self.symbol_env.find(proc_id_node.name)
        if prev:
            prev_var = self.symbol_env.lookup(proc_id_node.name)
            line_number = prev_var.declaration.line_number if prev_var.declaration else None
            proc_id_node.issues.append(VariableRedeclaration(proc_id_node.name, line_number))
            proc_id_node.__is_valid__ = False
            return None
        else:
            s = ProcedureSymbol(proc_id_node.name, ret_type,
                                start_label=start_label,
                                formal_params=formal_params)
            self.symbol_env.add_local(proc_id_node.name, s, level=display_level)
            return s


cur_context = Context()

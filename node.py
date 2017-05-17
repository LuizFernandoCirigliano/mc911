from environments import *
import errors
from typing import List
import LVM


class Node(object):
    def __init__(self, line_number):
        self.display_name = ''
        self.issues = []
        self.line_number = line_number
        self.__is_valid__ = None

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return "{}:{}".format(self.display_name, self.line_number)

    @property
    def children(self):
        return []

    @property
    def labels(self):
        return None

    @property
    def expr_type(self) -> ExprType:
        return void_symbol.expr_type

    @property
    def is_valid(self):
        return self.__is_valid__

    def validate_node(self) -> bool:
        self.issues = []

        for c in self.children:
            c.validate_node()

        self.__is_valid__ = self.__validate_node__()
        if not self.__is_valid__:
            return False

        for c in self.children:
            if not c.is_valid:
                self.__is_valid__ = False
                return False

        return self.__is_valid__

    def __validate_node__(self):
        return True

    def lvm_operators(self) -> List[LVM.LVMOperator]:
        return []

    def print_error(self):
        for issue in self.issues:
            print("{} line {} {}: {}".format(
                issue.issue_type.name,
                self.line_number,
                self.display_name,
                issue.message()
            ))


class PassNode(Node):
    def __init__(self, line_number, node_type, child):
        super().__init__(line_number)
        self.display_name = node_type
        self.child = child

    @property
    def children(self):
        return [self.child]


class ListNode(Node):
    def __init__(self, child_list, node_type='list'):
        super().__init__(None)
        self.display_name = node_type
        self.child_list = child_list

    @property
    def children(self):
        return self.child_list

    @property
    def is_valid(self):
        for c in self.child_list:
            if not c.is_valid:
                return False
        return True


class OperatorNode(Node):
    def __init__(self, line_number, symbol: str):
        super().__init__(line_number)
        self.symbol = symbol

    def __str__(self):
        return self.symbol


class BasicNode(Node):
    def __init__(self, line_number, value):
        super().__init__(line_number)
        self.value = value

    def __str__(self):
        return str(self.value)


class BasicMode(Node):
    def __init__(self, line_number, node_type: str):
        super().__init__(line_number)
        self.node_type = node_type

    def __str__(self):
        return str(self.expr_type)

    @property
    def expr_type(self) -> ExprType:
        return cur_context.symbol_env.lookup(self.node_type).expr_type


class Identifier(Node):
    def __init__(self, line_number, name: str):
        super().__init__(line_number)
        self.display_name = 'identifier'
        self.name = name

    def __str__(self):
        return "ID: " + self.name

    @property
    def expr_type(self) -> ExprType:
        return self.get_symbol().expr_type

    def __validate_node__(self):
        self.issues = []
        symbol = cur_context.symbol_env.lookup(self.name)
        valid = symbol is not None
        if not valid:
            self.issues.append(errors.UndeclaredVariable(self.name))
        return valid

    def get_symbol(self) -> Symbol:
        return cur_context.symbol_env.lookup(self.name) or void_symbol


class LiteralNode(Node):
    def __init__(self, line_number, value, type_name: str):
        super().__init__(line_number)
        self.value = value
        self.type_name = type_name

    def __str__(self):
        if self.expr_type.type == 'char':
            return chr(int(self.value))
        return str(self.value)

    @property
    def expr_type(self) -> ExprType:
        return cur_context.symbol_env.lookup(self.type_name).expr_type

    #TODO checar para string
    def lvm_operators(self):
        return [LVM.LoadConstantOperator(self.value)]


class Spec(Node):
    def __init__(self, line_number, spec_type, mode: Node, attribute=None):
        super().__init__(line_number)
        self.display_name = 'spec'
        self.spec_type = spec_type
        self.mode_node = mode
        self.attribute = attribute

    @property
    def children(self):
        c = [self.mode_node]
        if self.attribute:
            c.append(self.attribute)
        return c

    def __str__(self):
        return "{0}-{1}".format(self.display_name, self.spec_type)

    @property
    def expr_type(self):
        return self.mode_node.expr_type


class Program(Node):
    def __init__(self, line_number, statement_list):
        super().__init__(line_number)
        self.display_name = 'program'
        self.statement_list = statement_list

    @property
    def children(self):
        return self.statement_list


class IdentifierInitialization(Node):
    def __init__(self, line_number, identifier_list: list, mode: Node = None, initialization: Node = None):
        super().__init__(line_number)
        self.identifier_list = identifier_list
        self.mode_node = mode
        self.initialization = initialization

    @property
    def children(self):
        c = list()
        c.append(ListNode(self.identifier_list, 'identifiers'))
        if self.mode_node:
            c.append(self.mode_node)
        if self.initialization:
            c.append(self.initialization)
        return c

    @property
    def labels(self):
        l = ['ids']
        if self.mode_node:
            l.append('mode')
        if self.initialization:
            l.append('init')
        return l

    def __validate_node__(self):
        mode_node = self.mode_node or self.initialization
        valid_identifiers = cur_context.insert_symbol(self.identifier_list,
                                                      mode_node.expr_type,
                                                      SymbolCategory.VARIABLE,
                                                      self)
        if not (self.initialization and self.mode_node):
            return valid_identifiers
        valid = self.mode_node.expr_type == self.initialization.expr_type
        if not valid:
            self.issues.append(
                errors.TypeMismatch(self.mode_node.expr_type, self.initialization.expr_type)
            )

        return valid and valid_identifiers


class DeclarationStatement(Node):
    def __init__(self, line_number, declaration_list):
        super().__init__(line_number)
        self.display_name = 'dcl-stat'
        self.declaration_list = declaration_list

    @property
    def children(self):
        return self.declaration_list


class Declaration(IdentifierInitialization):
    def __init__(self, line_number, identifier_list, mode: Node, initialization: Node=None):
        super().__init__(line_number, identifier_list, mode=mode, initialization=initialization)
        self.display_name = 'dcl'

    def lvm_operators(self):
        return [LVM.AllocateOperator(len(self.identifier_list))]


class SynonymStatement(Node):
    def __init__(self, line_number, synonym_list: list):
        super().__init__(line_number)
        self.display_name = 'synonym-stat'
        self.synonym_list = synonym_list

    @property
    def children(self):
        return self.synonym_list


class Synonym(IdentifierInitialization):
    valid_types = ['int', 'string', 'char', 'bool']

    def __init__(self, line_number, identifier_list, expression: Node, mode: Node=None):
        super().__init__(line_number, identifier_list, mode=mode, initialization=expression)
        self.display_name = 'synonym'

    def __validate_node__(self):
        self.issues = []

        valid = super().__validate_node__()

        if not valid:
            return False

        if self.initialization.expr_type.type not in self.valid_types:
            self.issues.append(
                errors.InvalidType(self.initialization.expr_type)
            )
            return False

        return True


class UnOp(Node):
    valid_operators = CaseInsensitiveDict({
        'bool': ['!'],
        'int': ['-']
    })

    op_to_instr = {
        '!': [LVM.NotOperator()],
        '-': [LVM.NegateOperator()]
    }

    def __init__(self, line_number, operator: OperatorNode, operand: Node):
        super().__init__(line_number)
        self.display_name = 'un-op'
        self.operator = operator
        self.operand = operand

    @property
    def children(self):
        return [self.operator, self.operand]

    @property
    def expr_type(self) -> ExprType:
        return self.operand.expr_type

    def __validate_node__(self):
        self.issues = []
        valid = self.operator.symbol in self.valid_operators.get(self.operand.expr_type.type, [])
        if not valid:
            self.issues.append(
                errors.InvalidOperator(self.operator.symbol, self.operand.expr_type)
            )
        return valid

    def lvm_operators(self):
        return self.op_to_instr[self.operator.symbol]


class BinOp(Node):
    valid_operators = CaseInsensitiveDict({
        'int': ['+', '-', '*', '/', '%', '==', '!=', '>', '>=', '<', '>=', '<', '<='],
        'bool': ['==', '!=', '&&', '||'],
        'string': ['==', '!=', '+']
    })

    int_to_bool_ops = ['==', '!=', '>', '>=', '<', '>=', '<', '<=']

    op_to_instr = {
        '+': [LVM.AddOperator()],
        '-': [LVM.SubOperator()],
        '*': [LVM.MulOperator()],
        '/': [LVM.DivOperator()],
        '%': [LVM.ModOperator()],
        '&&': [LVM.LogicalAndOperator()],
        '||': [LVM.LogicalOrOperator()],
        '<': [LVM.LessOperator()],
        '<=': [LVM.LessOrEqualOperator()],
        '==': [LVM.EqualOperator()],
        '>=': [LVM.GreaterOrEqualOperator()],
        '>': [LVM.GreaterOperator()],
        '!=': [LVM.NotEqualOperator()]
    }

    def __init__(self, line_number, left: Node, op: OperatorNode, right: Node):
        super().__init__(line_number)
        self.display_name = 'bin-op'
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return str(self.op)

    @property
    def children(self):
        return [self.left, self.right]

    @property
    def expr_type(self) -> ExprType:
        if self.op.symbol in self.int_to_bool_ops:
            return bool_symbol.expr_type
        else:
            return self.left.expr_type

    def __validate_node__(self):
        self.issues = []
        equal_types = self.left.expr_type == self.right.expr_type
        if not equal_types:
            self.issues.append(
                errors.TypeMismatch(self.left.expr_type, self.right.expr_type)
            )
            return False

        valid_operator = self.op.symbol in self.valid_operators.get(self.left.expr_type.type, [])
        if not valid_operator:
            self.issues.append(
              errors.InvalidOperator(self.op.symbol, self.left.expr_type)
            )
        return valid_operator

    def lvm_operators(self):
        return self.op_to_instr[self.op.symbol]


class ReferenceMode(Node):
    def __init__(self, line_number, mode):
        super().__init__(line_number)
        self.display_name = 'ref-mode'
        self.mode_node = mode

    @property
    def children(self):
        return [self.mode_node]

    @property
    def expr_type(self):
        return ExprType("reference", self.mode_node.expr_type)


class LiteralRange(Node):
    def __init__(self, line_number, lb, ub):
        super().__init__(line_number)
        self.display_name = 'literal-range'
        self.lower_bound = lb
        self.upper_bound = ub

    @property
    def children(self):
        return [self.lower_bound, self.upper_bound]

    @property
    def labels(self):
        return ['from', 'to']


class DiscreteRangeMode(Node):
    def __init__(self, line_number, mode, literal_range):
        super().__init__(line_number)
        self.display_name = 'discrete-range-mode'
        self.mode_node = mode
        self.literal_range = literal_range

    @property
    def children(self):
        return [self.mode_node, self.literal_range]

    @property
    def expr_type(self):
        return ExprType("discrete range", self.mode_node.expr_type)


class StringMode(Node):
    def __init__(self, line_number, length):
        super().__init__(line_number)
        self.display_name = 'string-mode'
        self.length = length

    @property
    def children(self):
        return [self.length]

    @property
    def expr_type(self):
        return string_symbol.expr_type


class ArrayMode(Node):
    def __init__(self, line_number, index_mode_list: list, mode: Node=None):
        super().__init__(line_number)
        self.display_name = 'array-mode'
        self.index_mode_list = index_mode_list
        self.mode_node = mode

    @property
    def children(self):
        c = list()
        c.append(ListNode(self.index_mode_list, 'index_mode_list'))
        if self.mode_node:
            c.append(self.mode_node)
        return c

    @property
    def labels(self):
        l = ['']
        if self.mode_node:
            l.append('mode')
        return l

    @property
    def expr_type(self) -> ExprType:
        return ExprType("array", self.mode_node.expr_type)


class NewModeStatement(Node):
    def __init__(self, line_number, new_mode_list):
        super().__init__(line_number)
        self.display_name = 'new-mode-stat'
        self.new_mode_list = new_mode_list

    @property
    def children(self):
        return self.new_mode_list


class ModeDefinition(Node):
    def __init__(self, line_number, identifier_list, mode: Node):
        super().__init__(line_number)
        self.display_name = 'mode-def'
        self.mode_node = mode
        self.identifier_list = identifier_list

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'identifiers'), self.mode_node]

    @property
    def labels(self):
        return ['', 'mode']

    def validate_node(self):
        cur_context.insert_symbol(self.identifier_list, self.mode_node.expr_type, SymbolCategory.MODE, self)
        return super().validate_node()


class FormalParameter(Node):
    def __init__(self, line_number, id_list, parameter_spec: Spec):
        super().__init__(line_number)
        self.display_name = 'formal-param'
        self.parameter_spec = parameter_spec
        self.identifier_list = id_list

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'id_list'), self.parameter_spec]

    @property
    def expr_type(self):
        return self.parameter_spec.mode_node.expr_type


class ProcedureDefinition(Node):
    def __init__(self,
                 line_number,
                 statement_list=None,
                 formal_parameter_list: List[FormalParameter]=None,
                 result_spec: Spec=None):
        super().__init__(line_number)
        self.display_name = 'proc-def'
        self.statement_list = statement_list
        self.formal_parameter_list = formal_parameter_list
        self.result_spec = result_spec

    @property
    def children(self):
        c = []
        if self.statement_list:
            c.append(ListNode(self.statement_list, 'statements'))
        if self.formal_parameter_list:
            c.append(ListNode(self.formal_parameter_list, 'params'))
        if self.result_spec:
            c.append(self.result_spec)
        return c

    def __validate_node__(self):
        result_mode_node = self.result_spec or void_symbol
        result_expr_type = result_mode_node.expr_type

        valid = True
        for statement in self.statement_list:
            # Check return action against expected return type
            if type(statement) == ActionStatement and type(statement.action) == ReturnAction:
                ret_action = statement.action
                if ret_action.expr_type != result_expr_type:
                    ret_action.issues.append(
                        errors.TypeMismatch(result_expr_type, ret_action.expr_type)
                    )
                    valid = False
        return valid


class ProcedureStatement(Node):
    def __init__(self, line_number, label_id: Identifier, procedure_definition: ProcedureDefinition):
        super().__init__(line_number)
        self.display_name = 'proc-stat'
        self.label_id = label_id
        self.procedure_definition = procedure_definition

        result = self.procedure_definition.result_spec
        self.mode = result.mode_node if result else void_symbol

    @property
    def children(self):
        return [self.label_id, self.procedure_definition]

    def validate_node(self) -> bool:
        cur_context.insert_symbol([self.label_id], self.mode.expr_type, SymbolCategory.PROCEDURE, self)
        cur_context.symbol_env.push(self)

        formal_params = self.procedure_definition.formal_parameter_list
        if formal_params:
            for param in formal_params:
                cur_context.insert_symbol(param.identifier_list,
                                          param.expr_type,
                                          SymbolCategory.VARIABLE,
                                          self)
        valid = super().validate_node()

        cur_context.symbol_env.pop()

        return valid


class ReferenceLocation(Node):
    def __init__(self, line_number, location):
        super().__init__(line_number)
        self.display_name = 'ref-loc'
        self.location = location

    @property
    def children(self):
        return [self.location]

    @property
    def expr_type(self):
        return ExprType("reference", self.location.expr_type)


class DereferenceLocation(Node):
    def __init__(self, line_number, location):
        super().__init__(line_number)
        self.display_name = 'deref-loc'
        self.location = location

    @property
    def children(self):
        return [self.location]

    @property
    def expr_type(self):
        return self.location.expr_type.detail


class Slice(Node):
    def __init__(self, line_number, data_type, location, exp_begin, exp_end):
        super().__init__(line_number)
        self.display_name = 'slice'
        self.data_type = data_type
        self.location = location
        self.exp_begin = exp_begin
        self.exp_end = exp_end

    @property
    def children(self):
        return [self.data_type, self.location, self.exp_begin, self.exp_end]


class StringElement(Node):
    def __init__(self, line_number, location, element):
        super().__init__(line_number)
        self.display_name = 'string-element'
        self.location = location
        self.element = element

    @property
    def children(self):
        return [self.location, self.element]

    @property
    def labels(self):
        return ['string', 'element']

    @property
    def expr_type(self) -> ExprType:
        return char_symbol.expr_type


class ArrayElement(Node):
    def __init__(self, line_number, location, exp_list: list):
        super().__init__(line_number)
        self.display_name = 'array-element'
        self.location = location
        self.exp_list = exp_list

    @property
    def children(self):
        return [self.location, ListNode(self.exp_list, 'elements')]

    @property
    def labels(self):
        return ['array', '']

    @property
    def expr_type(self) -> ExprType:
        my_array_type = self.location.expr_type
        # Se tiver mais de um elemento, retorna outro array
        return my_array_type.detail if len(self.exp_list) == 1 else my_array_type


class ElsIf(Node):
    def __init__(self, line_number, condition, action):
        super().__init__(line_number)
        self.display_name = 'elsif'
        self.condition = condition
        self.action = action

    @property
    def children(self):
        return [self.condition, self.action]

    @property
    def expr_type(self):
        return self.action.expr_type


class ConditionalExpression(Node):
    def __init__(self, line_number, condition_exp: Node, action_exp: Node, else_exp: Node, elsif_list=None):
        super().__init__(line_number)
        self.display_name = 'cond-expr'
        self.condition_exp = condition_exp
        self.action_exp = action_exp
        self.else_exp = else_exp
        self.elsif_list = elsif_list

    @property
    def children(self):
        c = [self.condition_exp, self.action_exp]
        if self.elsif_list:
            c.append(ListNode(self.elsif_list, 'elsif'))
        c.append(self.else_exp)
        return c

    @property
    def labels(self):
        c = ['if', 'then']
        if self.elsif_list:
            c.append('elsif')
        c.append('else')
        return c

    @property
    def expr_type(self) -> ExprType:
        return self.action_exp.expr_type

    def __validate_node__(self):
        if self.action_exp.expr_type != self.else_exp.expr_type:
            self.issues.append(
                errors.TypeMismatch(self.action_exp.expr_type, self.else_exp.expr_type)
            )
            return False
        return True


class ActionStatement(Node):
    def __init__(self, line_number, action: Node, label_id: str =None):
        super().__init__(line_number)
        self.display_name = 'action-sttmnt'
        self.action = action
        self.label_id = label_id

    @property
    def children(self):
        c = list()
        c.append(self.action)
        if self.label_id:
            c.append(self.label_id)
        return c

    def validate_node(self):
        if self.label_id:
            cur_context.insert_symbol([self.label_id], self.action.expr_type, SymbolCategory.ACTION, self)
        return super().validate_node()


class AssignmentAction(Node):
    def __init__(self, line_number, location, operator, expression):
        super().__init__(line_number)
        self.display_name = 'assign-act'
        self.location = location
        self.operator = operator
        self.expression = expression

    @property
    def children(self):
        return [self.location, self.expression]

    @property
    def labels(self):
        return ['location', 'expr']

    def __str__(self):
        return str(self.operator)

    def __validate_node__(self):
        if self.location.expr_type != self.expression.expr_type:
            self.issues.append(
                errors.TypeMismatch(self.location.expr_type, self.expression.expr_type)
            )
            return False
        return True


class AssigningOperator(Node):
    def __init__(self, line_number, closed_dyadic_op=None):
        super().__init__(line_number)
        self.display_name = 'assign-op'
        self.closed_dyadic_op = closed_dyadic_op

    def __str__(self):
        return "{}=".format(self.closed_dyadic_op) if self.closed_dyadic_op else "="


class ReturnAction(Node):
    def __init__(self, line_number, expression=None):
        super().__init__(line_number)
        self.display_name = 'return'
        self.expression = expression

    @property
    def children(self):
        return [self.expression] if self.expression else []

    @property
    def expr_type(self):
        return self.expression.expr_type


class FuncCallBase(Node):
    def __init__(self, line_number, identifier: Identifier, exp_list=None):
        super().__init__(line_number)
        self.display_name = 'func-call'
        self.identifier = identifier
        self.arg_list = exp_list

    @property
    def children(self):
        c = list()
        c.append(self.identifier)
        if self.arg_list:
            c.append(ListNode(self.arg_list, 'args'))
        return c

    @property
    def labels(self):
        return ['id', '']

    @property
    def expr_type(self) -> ExprType:
        return self.identifier.expr_type

    def __validate_node__(self):
        if self.identifier.get_symbol().category != SymbolCategory.PROCEDURE:
            self.issues.append(
                errors.CallingNonCallable(self.identifier.name)
            )
            return False
        return True


class BuiltinCall(FuncCallBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.display_name = 'builtin-call'


class BuiltinName(Identifier):
    pass


class ProcedureCall(FuncCallBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.display_name = 'procedure-call'


class StepEnumeration(Node):
    def __init__(self, line_number, up, identifier, from_exp, to_exp, step_val=None):
        super().__init__(line_number)
        self.display_name = "enum-up" if up else "enum-down"
        self.up = up
        self.identifier = identifier
        self.from_exp = from_exp
        self.to_exp = to_exp
        self.step_val = step_val

    @property
    def children(self):
        c = [self.identifier, self.from_exp, self.to_exp]
        if self.step_val:
            c.append(self.step_val)
        return c

    @property
    def labels(self):
        e = ['id', 'from', 'to']
        if self.step_val:
            e.append('step-val')
        return e

    def validate_node(self):
        cur_context.insert_symbol([self.identifier], int_symbol.expr_type, SymbolCategory.VARIABLE, self)
        return super().validate_node()


class RangeEnum(Node):
    def __init__(self, line_number, up, identifier, discrete_mode):
        super().__init__(line_number)
        self.display_name = "rng-up" if up else "rng-down"
        self.up = up
        self.identifier = identifier
        self.discrete_mode = discrete_mode

    @property
    def children(self):
        return [self.identifier, self.discrete_mode]

    def validate_node(self) -> bool:
        cur_context.insert_symbol([self.identifier], int_symbol.expr_type, SymbolCategory.VARIABLE, self)
        return super().validate_node()


class ControlPart(Node):
    def __init__(self, line_number, for_ctrl=None, while_ctrl=None):
        super().__init__(line_number)
        self.display_name = 'ctrl-part'
        self.for_ctrl = for_ctrl
        self.while_ctrl = while_ctrl

    @property
    def children(self):
        c = []
        if self.for_ctrl:
            c.append(self.for_ctrl)
        if self.while_ctrl:
            c.append(self.while_ctrl)
        return c

    @property
    def labels(self):
        e = []
        if self.for_ctrl:
            e.append('for')
        if self.while_ctrl:
            e.append('while')
        return e


class DoAction(Node):
    def __init__(self, line_number, ctrl_part=None, action_st_list=None):
        super().__init__(line_number)
        self.display_name = 'do-act'
        self.ctrl_part = ctrl_part
        self.action_st_list = action_st_list

    @property
    def children(self):
        c = []
        if self.ctrl_part:
            c.append(self.ctrl_part)
        if self.action_st_list:
            c.append(ListNode(self.action_st_list))
        return c

    def validate_node(self) -> bool:
        cur_context.symbol_env.push(self)
        valid = super().validate_node()
        cur_context.symbol_env.pop()
        return valid


class IfAction(Node):
    def __init__(self, line_number, expression, then_clause, elsif_clause=None, else_clause=None):
        super().__init__(line_number)
        self.display_name = 'if-act'
        self.expression = expression
        self.then_clause = then_clause
        self.elsif_clause = elsif_clause
        self.else_clause = else_clause

    @property
    def children(self):
        c = [self.expression, self.then_clause]
        if self.elsif_clause:
            c.append(self.elsif_clause)
        if self.else_clause:
            c.append(self.else_clause)
        return c

    @property
    def labels(self):
        e = ['exp', 'then']
        if self.elsif_clause:
            e.append('elsif')
        if self.else_clause:
            e.append('else')
        return e

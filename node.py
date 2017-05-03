from case_ins_dict import CaseInsensitiveDict
from environments import cur_context, Symbol
import errors
from typing import List

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
    def expr_type(self):
        return cur_context.mode_env.lookup('void')

    @property
    def is_valid(self):
        return self.__is_valid__

    def validate_node(self):
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

    def print_error(self):
        for issue in self.issues:
            print("{} line {} {}: {}".format(
                issue.issue_type.name,
                self.line_number,
                self.display_name,
                issue.message()
            ))


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
    def __init__(self, line_number, node_type):
        super().__init__(line_number)
        self.node_type = node_type

    def __str__(self):
        return str(self.expr_type)

    @property
    def expr_type(self):
        return cur_context.mode_env.lookup(self.node_type)


class LiteralNode(Node):
    def __init__(self, line_number, value, type_name):
        super().__init__(line_number)
        self.value = value
        self.type_name = type_name

    def __str__(self):
        if self.expr_type.type == 'char':
            return chr(int(self.value))
        return str(self.value)

    @property
    def expr_type(self):
        return cur_context.mode_env.lookup(self.type_name)


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


class Program(Node):
    def __init__(self, line_number, statement_list):
        super().__init__(line_number)
        self.display_name = 'program'
        self.statement_list = statement_list

    @property
    def children(self):
        return self.statement_list


class IdentifierInitialization(Node):
    def __init__(self, line_number, identifier_list, mode: Node = None, initialization: Node = None):
        super().__init__(line_number)
        self.identifier_list = identifier_list
        self.mode = mode
        self.initialization = initialization

    @property
    def children(self):
        c = list()
        c.append(ListNode(self.identifier_list, 'identifiers'))
        if self.mode:
            c.append(self.mode)
        if self.initialization:
            c.append(self.initialization)
        return c

    @property
    def labels(self):
        l = ['ids']
        if self.mode:
            l.append('mode')
        if self.initialization:
            l.append('init')
        return l

    def __validate_node__(self):
        mode_node = self.mode or self.initialization
        valid_identifiers = cur_context.insert_variables(self.identifier_list, mode_node.expr_type, self)
        valid = self.mode.expr_type == self.initialization.expr_type if (self.initialization and self.mode) else True
        if not valid:
            self.issues.append(
                errors.TypeMismatch(self.mode.expr_type, self.initialization.expr_type)
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

    def __init__(self, line_number, operator: OperatorNode, operand: Node):
        super().__init__(line_number)
        self.display_name = 'un-op'
        self.operator = operator
        self.operand = operand

    @property
    def children(self):
        return [self.operator, self.operand]

    @property
    def expr_type(self):
        return self.operand.expr_type

    def __validate_node__(self):
        self.issues = []
        valid = self.operator.symbol in self.valid_operators.get(self.operand.expr_type.type, [])
        if not valid:
            self.issues.append(
                errors.InvalidOperator(self.operator.symbol, self.operand.expr_type)
            )
        return valid


class BinOp(Node):
    valid_operators = CaseInsensitiveDict({
        'int': ['+', '-', '*', '/', '%', '==', '!=', '>', '>=', '<', '>=', '<', '<='],
        'bool': ['==', '!='],
        'string': ['==', '!=', '+']
    })

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
    def expr_type(self):
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


class ReferenceMode(Node):
    def __init__(self, line_number, mode):
        super().__init__(line_number)
        self.display_name = 'ref-mode'
        self.mode = mode

    @property
    def children(self):
        return [self.mode]


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
        self.mode = mode
        self.literal_range = literal_range

    @property
    def children(self):
        return [self.mode, self.literal_range]


class Identifier(Node):
    def __init__(self, line_number, name: str):
        super().__init__(line_number)
        self.display_name = 'identifier'
        self.name = name

    def __str__(self):
        return "ID: " + self.name

    @property
    def expr_type(self):
        var = cur_context.var_env.lookup(self.name)
        return var.mode if var else cur_context.mode_env.lookup('void')

    def __validate_node__(self):
        self.issues = []
        symbol = cur_context.var_env.lookup(self.name)
        valid = symbol is not None
        if not valid:
            self.issues.append(errors.UndeclaredVariable(self.name))
        return valid


class StringMode(Node):
    def __init__(self, line_number, length):
        super().__init__(line_number)
        self.display_name = 'string-mode'
        self.length = length

    @property
    def children(self):
        return [self.length]


class ArrayMode(Node):
    def __init__(self, line_number, index_mode_list, mode: Node=None):
        super().__init__(line_number)
        self.display_name = 'array-mode'
        self.index_mode_list = index_mode_list
        self.mode = mode

    @property
    def children(self):
        c = list()
        c.append(ListNode(self.index_mode_list, 'index_mode_list'))
        if self.mode:
            c.append(self.mode)
        return c

    @property
    def labels(self):
        l = ['']
        if self.mode:
            l.append('mode')
        return l


class NewModeStatement(Node):
    def __init__(self, line_number, new_mode_list):
        super().__init__(line_number)
        self.display_name = 'new-mode-stat'
        self.new_mode_list = new_mode_list

    @property
    def children(self):
        return self.new_mode_list


class ModeDefinition(Node):
    def __init__(self, line_number, identifier_list, mode):
        super().__init__(line_number)
        self.display_name = 'mode-def'
        self.mode = mode
        self.identifier_list = identifier_list

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'identifiers'), self.mode]

    @property
    def labels(self):
        return ['', 'mode']


class FormalParameter(Node):
    def __init__(self, line_number, id_list, parameter_spec):
        super().__init__(line_number)
        self.display_name = 'formal-param'
        self.parameter_spec = parameter_spec
        self.identifier_list = id_list

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'id_list'), self.parameter_spec]


class ProcedureDefinition(Node):
    def __init__(self, line_number, statement_list=None,
                 formal_parameter_list: List[FormalParameter]=None, result_spec=None):
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


class ProcedureStatement(Node):
    def __init__(self, line_number, label_id: Identifier, procedure_definition: ProcedureDefinition):
        super().__init__(line_number)
        self.display_name = 'proc-stat'
        self.label_id = label_id
        self.procedure_definition = procedure_definition

        result = self.procedure_definition.result_spec
        self.mode = result.mode if result else cur_context.mode_env.lookup('void')

    @property
    def children(self):
        return [self.label_id, self.procedure_definition]

    def validate_node(self):
        cur_context.insert_variables([self.label_id], self.mode, self)
        cur_context.var_env.push(self)

        formal_params = self.procedure_definition.formal_parameter_list
        if formal_params:
            for param in formal_params:
                cur_context.insert_variables(param.identifier_list, param.parameter_spec.mode.expr_type, self)

        super().validate_node()

        cur_context.var_env.pop()

        return


class Spec(Node):
    def __init__(self, line_number, spec_type, mode, attribute=None):
        super().__init__(line_number)
        self.display_name = 'spec'
        self.spec_type = spec_type
        self.mode = mode
        self.attribute = attribute

    @property
    def children(self):
        c = [self.mode]
        if self.attribute:
            c.append(self.attribute)
        return c

    def __str__(self):
        return "{0}-{1}".format(self.display_name, self.spec_type)


class ReferenceLocation(Node):
    def __init__(self, line_number, location):
        super().__init__(line_number)
        self.display_name = 'ref-loc'
        self.location = location

    @property
    def children(self):
        return [self.location]


class DereferenceLocation(Node):
    def __init__(self, line_number, location):
        super().__init__(line_number)
        self.display_name = 'deref-loc'
        self.location = location

    @property
    def children(self):
        return [self.location]


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
    def expr_type(self):
        return cur_context.mode_env.lookup('char')


class ArrayElement(Node):
    def __init__(self, line_number, location, exp_list):
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


class ElsIf(Node):
    def __init__(self, line_number, condition, action):
        super().__init__(line_number)
        self.display_name = 'elsif'
        self.condition = condition
        self.action = action

    @property
    def children(self):
        return [self.condition, self.action]


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
    def expr_type(self):
        return self.action_exp.expr_type

    def __validate_node__(self):
        if self.action_exp.expr_type != self.else_exp.expr_type:
            self.issues.append(
                errors.TypeMismatch(self.action_exp.expr_type, self.else_exp.expr_type)
            )
            return False
        return True


class ActionStatement(Node):
    def __init__(self, line_number, action, label_id=None):
        super().__init__(line_number)
        self.display_name = 'action-sttmnt'
        self.action = action
        self.label_id = label_id

    @property
    def children(self):
        c = [self.action]
        if self.label_id:
            c.append(self.label_id)
        return c


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
    def expr_type(self):
        symbol = cur_context.var_env.lookup(self.identifier.name)
        mode = symbol.mode if symbol else cur_context.var_env.lookup('void')
        return mode.expr_type


class BuiltinCall(FuncCallBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.display_name = 'builtin-call'


class BuiltinName(Node):
    # TODO Verify Functions
    ret_types = CaseInsensitiveDict({
        'ABS': cur_context.mode_env.lookup('int'),
        'ASC': cur_context.mode_env.lookup('int'),
        'UPPER': cur_context.mode_env.lookup('string'),
        'LOWER': cur_context.mode_env.lookup('string'),
        'NUM': cur_context.mode_env.lookup('int'),
        'READ': cur_context.mode_env.lookup('string'),
        'PRINT': cur_context.mode_env.lookup('void')
    })

    def __init__(self, line_number, name):
        super().__init__(line_number)
        self.name = name

    @property
    def expr_type(self):
        return self.ret_types[self.name]

    def __str__(self):
        return str(self.name)


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

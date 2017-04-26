from case_ins_dict import CaseInsensitiveDict
from environments import var_env, mode_env, Symbol


def validate_list(my_list):
    for l in my_list:
        if not l.is_valid():
            return False
    return True


class Node(object):
    display_name = ''
    line_number = None
    expr_type = mode_env.lookup('void')
    valid_saved = None
    err_msg = None

    def __init__(self, line_number):
        self.line_number = line_number
        self.is_valid()

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

    def validate_node(self):
        return True

    def is_valid(self):
        if self.valid_saved is None:
            valid_children = validate_list(self.children)
            self.valid_saved = valid_children and self.validate_node()
        return self.valid_saved

    def print_error(self):
        from helpers import print_error
        print_error('semantic', self.line_number, self.err_msg)


class OperatorNode(Node):
    def __init__(self, line_number, symbol:str):
        self.symbol = symbol
        super().__init__(line_number)

    def __str__(self):
        return self.symbol


class BasicNode(Node):
    def __init__(self, line_number, value):
        self.value = value
        super().__init__(line_number)

    def __str__(self):
        return str(self.value)


class BasicMode(Node):
    def __init__(self, line_number, type):
        self.expr_type = mode_env.lookup(type)
        super().__init__(line_number)

    def __str__(self):
        return str(self.expr_type)


class LiteralNode(Node):
    def __init__(self, line_number, value, type_name):
        self.value = value
        self.expr_type = mode_env.lookup(type_name)
        super().__init__(line_number)

    def __str__(self):
        if self.expr_type.type == 'char':
            return chr(int(self.value))
        return str(self.value)


class PassNode(Node):
    def __init__(self, line_number, type, child):
        self.display_name=type
        self.child=child
        super().__init__(line_number)

    @property
    def children(self):
        return [self.child]


class ListNode(Node):
    def __init__(self, child_list, type='list'):
        self.display_name = type
        self.child_list = child_list
        super().__init__(None)

    @property
    def children(self):
        return self.child_list


class Program(Node):
    def __init__(self, line_number, statement_list):
        self.display_name = 'program'
        self.statement_list = statement_list
        super().__init__(line_number)

    @property
    def children(self):
        return self.statement_list


class DeclarationStatement(Node):
    def __init__(self, line_number, declaration_list):
        self.display_name = 'dcl-stat'
        self.declaration_list = declaration_list
        super().__init__(line_number)

    @property
    def children(self):
        return self.declaration_list


class Declaration(Node):
    def __init__(self, line_number, identifier_list, mode, initialization=None):
        self.display_name = 'dcl'
        self.identifier_list = identifier_list
        self.mode = mode
        self.initialization = initialization
        super().__init__(line_number)

        for identifier in identifier_list:
            if type(identifier) is not Identifier:
                raise TypeError
            s = Symbol(identifier.name, self.mode.expr_type, self)
            var_env.add_local(identifier.name, s)

    @property
    def children(self):
        c = [ListNode(self.identifier_list, 'identifiers'), self.mode]
        if self.initialization:
            c.append(self.initialization)
        return c

    def validate_node(self):
        valid = self.mode.expr_type == self.initialization.expr_type if self.initialization else True
        if not valid:
            self.err_msg = "Declaration expected type {} but received {}".\
                format(self.mode.expr_type, self.initialization.expr_type)
            self.print_error()
        return valid


class UnOp(Node):
    valid_operators = CaseInsensitiveDict({
        'bool': ['!'],
        'int': ['-']
    })

    def __init__(self, line_number, operator, operand):
        self.display_name = 'un-op'
        self.operator = operator
        self.operand = operand
        self.expr_type = self.operand.expr_type
        super().__init__(line_number)

    @property
    def children(self):
        return [self.operator, self.operand]

    def validate_node(self):
        valid = self.operator.symbol in self.valid_operators.get(self.operand.expr_type.type, [])
        if not valid:
            self.err_msg = "Invalid operator {} for un-op with {} operand".\
                        format(self.operator.symbol, self.operand.expr_type)
            self.print_error()
        return valid


class BinOp(Node):
    valid_operators = CaseInsensitiveDict({
        'int': ['+', '-', '*', '/', '%', '==', '!=', '>', '>=', '<', '>=', '<', '<=' ],
        'bool': ['==', '!='],
        'string': ['==', '!=', '+']
    })

    def __init__(self, line_number, left, op: OperatorNode, right):
        self.display_name = 'bin-op'
        self.left = left
        self.right = right
        self.op = op
        self.expr_type = self.left.expr_type
        super().__init__(line_number)

    def __str__(self):
        return str(self.op)

    @property
    def children(self):
        return [self.left, self.right]

    def validate_node(self):
        if self.left.expr_type != self.right.expr_type:
            self.err_msg = 'Binary Operation with mismatching types ({} and {})'\
                        .format(self.left.expr_type, self.right.expr_type)
            self.print_error()
            return False
        else:
            valid = self.op.symbol in self.valid_operators.get(self.left.expr_type.type, [])
            if not valid:
                self.err_msg = 'Invalid operator {} for bin-op with {} operands'.\
                    format(self.op.symbol, self.left.expr_type)
                self.print_error()
            return valid


class ReferenceMode(Node):
    def __init__(self, line_number, mode):
        self.display_name = 'ref-mode'
        self.mode = mode
        super().__init__(line_number)

    @property
    def children(self):
        return [self.mode]


class LiteralRange(Node):
    def __init__(self, line_number, lb, ub):
        self.display_name = 'literal-range'
        self.lower_bound = lb
        self.upper_bound = ub
        super().__init__(line_number)

    @property
    def children(self):
        return [self.lower_bound, self.upper_bound]

    @property
    def labels(self):
        return ['from', 'to']


class DiscreteRangeMode(Node):
    def __init__(self, line_number, mode, literal_range):
        self.display_name = 'discrete-range-mode'
        self.mode = mode
        self.literal_range = literal_range
        super().__init__(line_number)

    @property
    def children(self):
        return [self.mode, self.literal_range]


class Identifier(Node):
    def __init__(self, line_number, name):
        self.display_name = 'identifier'
        self.name = name
        super().__init__(line_number)

    def __str__(self):
        return "ID: " + self.name

    @property
    def expr_type(self):
        return var_env.lookup(self.name).mode or mode_env.lookup('void')

    def validate_node(self):
        symbol = var_env.lookup(self.name)
        valid = symbol is not None
        if not valid:
            self.err_msg = "Identifier {} not declared".format(self.name)
            self.print_error()
        return valid


class SynonymStatement(Node):
    def __init__(self, line_number, synonym_list: list):
        self.display_name = 'synonym-stat'
        self.synonym_list = synonym_list
        super().__init__(line_number)

    @property
    def children(self):
        return self.synonym_list

    def validate_node(self):
        return validate_list(self.synonym_list)


class Synonym(Node):
    valid_types = ['int', 'string', 'char', 'bool']

    def __init__(self, line_number, identifier_list, expression, mode=None):
        self.display_name = 'synonym'
        self.identifier_list = identifier_list
        self.expression = expression
        self.mode = mode
        super().__init__(line_number)

    @property
    def children(self):
        if self.mode:
            return [ListNode(self.identifier_list, 'identifiers'), self.expression, self.mode]
        else:
            return [ListNode(self.identifier_list, 'identifiers'), self.expression]

    @property
    def labels(self):
        return ['ids', 'expr', 'mode'] if self.mode else ['ids', 'expr']

    def validate_node(self):
        if self.expression.expr_type.type not in self.valid_types:
            self.err_msg = 'Invalid type for synonym expression'.\
                        format(self.expression.expr_type)
            self.print_error()
            return False
        if self.mode:
            valid = self.mode.expr_type == self.expression.expr_type
            if not valid:
                self.err_msg = 'Synonym expression expected type {} but received {}'.\
                            format(self.mode.expr_type, self.expression.expr_type)
                self.print_error()
            return valid
        return True


class StringMode(Node):
    def __init__(self, line_number, length):
        self.display_name = 'string-mode'
        self.length = length
        super().__init__(line_number)

    @property
    def children(self):
        return [self.length]


class ArrayMode(Node):
    def __init__(self, line_number, index_mode_list, mode=Node):
        self.display_name = 'array-mode'
        self.index_mode_list = index_mode_list
        self.mode = mode
        super().__init__(line_number)

    @property
    def children(self):
        c = [ListNode(self.index_mode_list, 'index_mode_list')]
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
    def __init__(self, line_number, newmode_list):
        self.display_name = 'new-mode-stat'
        self.newmode_list = newmode_list
        super().__init__(line_number)

    @property
    def children(self):
        return self.newmode_list


class ModeDefinition(Node):
    def __init__(self, line_number, identifier_list, mode):
        self.display_name = 'mode-def'
        self.mode = mode
        self.identifier_list = identifier_list
        super().__init__(line_number)

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'identifiers'), self.mode]

    @property
    def labels(self):
        return ['', 'mode']


class ProcedureStatement(Node):
    def __init__(self, line_number, label_id, procedure_definition):
        self.display_name = 'proc-stat'
        self.label_id = label_id
        self.procedure_definition = procedure_definition
        super().__init__(line_number)

    @property
    def children(self):
        return [self.label_id, self.procedure_definition]


class ProcedureDefintion(Node):
    def __init__(self, line_number, statement_list=None, formal_parameter_list=None, result_spec=None):
        self.display_name = 'proc-def'
        self.statement_list = statement_list
        self.formal_parameter_list = formal_parameter_list
        self.result_spec = result_spec
        super().__init__(line_number)

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


class FormalParameter(Node):
    def __init__(self, line_number, id_list, parameter_spec):
        self.display_name = 'formal-param'
        self.parameter_spec = parameter_spec
        self.identifier_list = id_list
        super().__init__(line_number)

    @property
    def children(self):
        return [ListNode(self.identifier_list, 'id_list'), self.parameter_spec]


class Spec(Node):
    def __init__(self, line_number, spec_type, mode, attribute=None):
        self.display_name = 'spec'
        self.spec_type = spec_type
        self.mode = mode
        self.attribute=attribute
        super().__init__(line_number)

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
        self.display_name = 'ref-loc'
        self.location = location
        super().__init__(line_number)

    @property
    def children(self):
        return [self.location]


class DereferenceLocation(Node):
    def __init__(self, line_number, location):
        self.display_name='deref-loc'
        self.location = location
        super().__init__(line_number)

    @property
    def children(self):
        return [self.location]


class Slice(Node):
    def __init__(self, line_number, data_type, location, exp_begin, exp_end):
        self.display_name = 'slice'
        self.data_type = data_type
        self.location = location
        self.exp_begin = exp_begin
        self.exp_end = exp_end
        super().__init__(line_number)

    @property
    def children(self):
        return [self.data_type, self.location, self.exp_begin, self.exp_end]


class StringElement(Node):
    def __init__(self, line_number, location, element):
        self.display_name = 'string-element'
        self.location = location
        self.element = element
        super().__init__(line_number)

    @property
    def children(self):
        return [self.location, self.element]

    @property
    def labels(self):
        return ['string', 'element']


class ArrayElement(Node):
    def __init__(self, line_number, location, exp_list):
        self.display_name = 'array-element'
        self.location = location
        self.exp_list = exp_list
        super().__init__(line_number)

    @property
    def children(self):
        return [self.location, ListNode(self.exp_list, 'elements')]

    @property
    def labels(self):
        return ['array', '']

class ElsIf(Node):
    def __init__(self, line_number, condition, action):
        self.display_name = 'elsif'
        self.condition = condition
        self.action = action
        super().__init__(line_number)

    @property
    def children(self):
        return [self.condition, self.action]


class ConditionalExpression(Node):
    def __init__(self, line_number, condition_exp, action_exp, else_exp, elsif_list=None):
        self.display_name = 'cond'
        self.condition_exp = condition_exp
        self.action_exp = action_exp
        self.else_exp = else_exp
        self.elsif_list = elsif_list
        super().__init__(line_number)

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


class ActionStatement(Node):
    def __init__(self, line_number, action, label_id=None):
        self.display_name = 'action-sttmnt'
        self.action = action
        self.label_id = label_id
        super().__init__(line_number)

    @property
    def children(self):
        c = [self.action]
        if self.label_id:
            c.append(self.label_id)
        return c


class AssignmentAction(Node):
    def __init__(self, line_number, location, operator, expression):
        self.display_name = 'assign-act'
        self.location = location
        self.operator = operator
        self.expression = expression
        super().__init__(line_number)

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
        self.display_name = 'assign-op'
        self.closed_dyadic_op = closed_dyadic_op
        super().__init__(line_number)

    def __str__(self):
        return "{}=".format(self.closed_dyadic_op) if self.closed_dyadic_op else "="


class ReturnAction(Node):
    def __init__(self, line_number, expression=None):
        self.display_name = 'return'
        self.expression=expression
        super().__init__(line_number)

    @property
    def children(self):
        return [self.expression] if self.expression else []


class FuncCall(Node):
    def __init__(self, line_number, name, exp_list=None):
        self.display_name='func-call'
        self.name = name
        self.arg_list = exp_list
        super().__init__(line_number)

    @property
    def children(self):
        c = [self.name]
        if self.arg_list:
            c.append(ListNode(self.arg_list, 'args'))
        return c

    @property
    def labels(self):
        return ['name', '']


class BuiltinCall(FuncCall):
    def __init__(self, *args):
        super().__init__(*args)
        self.display_name='builtin-call'


class BuiltinName(Node):
    # TODO Verificar essas funções
    ret_types = CaseInsensitiveDict({
        'ABS': mode_env.lookup('int'),
        'ASC': mode_env.lookup('int'),
        'UPPER': mode_env.lookup('string'),
        'LOWER': mode_env.lookup('string'),
        'NUM': mode_env.lookup('int'),
        'READ': mode_env.lookup('string'),
        'PRINT': mode_env.lookup('void')
    })

    def __init__(self, line_number, name):
        self.name = name
        self.expr_type = self.ret_types[name]
        super().__init__(line_number)

    def __str__(self):
        return str(self.name)


class ProcedureCall(FuncCall):
    def __init__(self, *args):
        super().__init__(*args)
        self.display_name = 'proc-call'


class StepEnumeration(Node):
    def __init__(self, line_number, up, identifier, from_exp, to_exp, step_val=None):
        self.display_name = "enum-up" if up else "enum-down"
        self.up = up
        self.identifier = identifier
        self.from_exp = from_exp
        self.to_exp = to_exp
        self.step_val = step_val
        super().__init__(line_number)

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
        self.display_name = "rng-up" if up else "rng-down"
        self.up = up
        self.identifier = identifier
        self.discrete_mode = discrete_mode
        super().__init__(line_number)

    @property
    def children(self):
        return [self.identifier, self.discrete_mode]


class ControlPart(Node):
    def __init__(self, line_number, for_ctrl=None, while_ctrl=None):
        self.display_name='ctrl-part'
        self.for_ctrl = for_ctrl
        self.while_ctrl = while_ctrl
        super().__init__(line_number)

    @property
    def children(self):
        c = []
        if self.for_ctrl:
            c.append( self.for_ctrl )
        if self.while_ctrl:
            c.append( self.while_ctrl )
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
        self.display_name='do-act'
        self.ctrl_part = ctrl_part
        self.action_st_list = action_st_list
        super().__init__(line_number)

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
        self.display_name='if-act'
        self.expression=expression
        self.then_clause=then_clause
        self.elsif_clause=elsif_clause
        self.else_clause=else_clause
        super().__init__(line_number)

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
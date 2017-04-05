class Node(object):
    type = ""
    lineno = None

    def __str__(self):
        return self.type

    def __repr__(self):
        return "{}{}".format(self.type, self.lineno)

    @property
    def children(self):
        return []


class BasicNode(Node):
    def __init__(self, lineno, value):
        self.lineno = lineno
        self.value = value


class ListNode(Node):
    def __init__(self, child_list):
        self.type = 'list'
        self.child_list = child_list

    @property
    def children(self):
        return self.child_list


class Program(Node):
    def __init__(self, lineno, statement_list):
        self.lineno = lineno
        self.type = 'program'
        self.statement_list = statement_list

    @property
    def children(self):
        return self.statement_list


class DeclarationStatement(Node):
    def __init__(self, lineno, declaration_list):
        self.lineno = lineno
        self.type = 'dcl-stat'
        self.declaration_list = declaration_list

    @property
    def children(self):
        return self.declaration_list


class Declaration(Node):
    def __init__(self, lineno, identifier_list, mode, initialization=None):
        self.lineno = lineno
        self.type = 'dcl'
        self.identifier_list = identifier_list
        self.mode = mode
        self.initialization = initialization

    @property
    def children(self):
        c = [ListNode(self.identifier_list), self.mode]
        if self.initialization:
            c.append(self.initialization)
        return c


class UnOp(Node):
    def __init__(self, lineno, operator, operand):
        self.lineno = lineno
        self.type = 'un-op'
        self.operator = operator
        self.operand = operand

    @property
    def children(self):
        return [self.operator, self.operand]


class BinOp(Node):
    def __init__(self, lineno, left, op, right):
        self.lineno = lineno
        self.type = 'bin-op'
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return str(self.op)

    @property
    def children(self):
        return [self.left, self.op, self.right]


class ReferenceMode(Node):
    def __init__(self, lineno, mode):
        self.lineno = lineno
        self.type = 'ref-mode'
        self.mode = mode

    @property
    def children(self):
        return [self.mode]


class LiteralRange(Node):
    def __init__(self, lineno, lb, ub):
        self.lineno = lineno
        self.type = 'literal-range'
        self.lower_bound = lb
        self.upper_bound = ub

    @property
    def children(self):
        return [self.lower_bound, self.upper_bound]


class DiscreteRangeMode(Node):
    def __init__(self, lineno, mode, literal_range):
        self.lineno = lineno
        self.type = 'discrete-range-mode'
        self.mode = mode
        self.literal_range = literal_range

    @property
    def children(self):
        return [self.mode, self.literal_range]


class Identifier(Node):
    def __init__(self, lineno, name):
        self.lineno = lineno
        self.type = 'identifier'
        self.name = name

    def __str__(self):
        return "ID: " + self.name


class SynonymStatement(Node):
    def __init__(self, lineno, synonym_list: list):
        self.lineno = lineno
        self.type = 'synonym-stat'
        self.synonym_list = synonym_list

    @property
    def children(self):
        return self.synonym_list


class Synonym(Node):
    def __init__(self, lineno, identifier_list, expression, mode=None):
        self.lineno = lineno
        self.type = 'synonym'
        self.identifier_list = identifier_list
        self.expression = expression
        self.mode = mode

    @property
    def children(self):
        if self.mode:
            return [ListNode(self.identifier_list), self.expression, self.mode]
        else:
            return [ListNode(self.identifier_list), self.expression]


class IConst(Node):
    def __init__(self, lineno, value):
        self.lineno = lineno
        self.type = 'iconst'
        self.value = value

    def __str__(self):
        return str(self.value)


class StringMode(Node):
    def __init__(self, lineno, length):
        self.lineno = lineno
        self.type = 'string-mode'
        self.length = length

    @property
    def children(self):
        return [self.length]


class ArrayMode(Node):
    def __init__(self, lineno, index_mode_list, mode=Node):
        self.lineno = lineno
        self.type = 'array-mode'
        self.index_mode_list = index_mode_list
        self.mode = mode

    @property
    def children(self):
        if self.mode:
            return [ListNode(self.index_mode_list), self.mode]
        else:
            return self.index_mode_list


class NewModeStatement(Node):
    def __init__(self, lineno, newmode_list):
        self.lineno = lineno
        self.type = 'new-mode-stat'
        self.newmode_list = newmode_list

    @property
    def children(self):
        return self.newmode_list


class ModeDefinition(Node):
    def __init__(self, lineno, identifier_list, mode):
        self.lineno = lineno
        self.type = 'mode-def'
        self.mode = mode
        self.identifier_list = identifier_list

    @property
    def children(self):
        return [ListNode(self.identifier_list), self.mode]


class ProcedureStatement(Node):
    def __init__(self, lineno, label_id, procedure_definition):
        self.lineno = lineno
        self.type = 'proc-stat'
        self.label_id = label_id
        self.procedure_definition = procedure_definition

    @property
    def children(self):
        return [self.label_id, self.procedure_definition]


class ProcedureDefintion(Node):
    def __init__(self, lineno, statement_list=None, formal_parameter_list=None, result_spec=None):
        self.lineno = lineno
        self.type = 'proc-def'
        self.statement_list = statement_list
        self.formal_parameter_list = formal_parameter_list
        self.result_spec = result_spec

    @property
    def children(self):
        c = []
        if self.statement_list:
            c.append(ListNode(self.statement_list))
        if self.formal_parameter_list:
            c.append(ListNode(self.formal_parameter_list))
        if self.result_spec:
            c.append(ListNode(self.formal_parameter_list))
        return c


class FormalParameter(Node):
    def __init__(self, lineno, id_list, parameter_spec):
        self.lineno = lineno
        self.type = 'formal-param'
        self.parameter_spec = parameter_spec
        self.identifier_list = id_list

    @property
    def children(self):
        return [ListNode(self.identifier_list), self.parameter_spec]


class Spec(Node):
    def __init__(self, lineno, spec_type, mode, attribute=None):
        self.lineno = lineno
        self.type = 'spec'
        self.spec_type = spec_type
        self.mode = mode
        self.attribute=attribute

    @property
    def children(self):
        c = [self.mode]
        if self.attribute:
            c.append(self.attribute)
        return c

    def __str__(self):
        return "{0}-{1}".format(self.type, self.spec_type)


class ReferenceLocation(Node):
    def __init__(self, lineno, location):
        self.lineno = lineno
        self.type = 'ref-loc'
        self.location = location

    @property
    def children(self):
        return [self.location]


class DereferenceLocation(Node):
    def __init__(self, lineno, location):
        self.lineno = lineno
        self.location = location

    @property
    def children(self):
        return [self.location]


class Slice(Node):
    def __init__(self, lineno, data_type, location, exp_begin, exp_end):
        self.lineno = lineno
        self.type = 'slice'
        self.data_type = data_type
        self.location = location
        self.exp_begin = exp_begin
        self.exp_end = exp_end

    @property
    def children(self):
        return [self.data_type, self.location, self.exp_begin, self.exp_end]


class Element(Node):
    def __init__(self, lineno, data_type, location, exp_list):
        self.lineno = lineno
        self.type = 'element'
        self.data_type = data_type
        self.location = location
        self.exp_list = exp_list

    @property
    def children(self):
        return [self.data_type, self.location, ListNode(self.exp_list)]


class ElsIf(Node):
    def __init__(self, lineno, condition, action):
        self.lineno = lineno
        self.type = 'elsif'
        self.condition = condition
        self.action = action

    @property
    def children(self):
        return [self.condition, self.action]


class ConditionalExpression(Node):
    def __init__(self, lineno, condition_exp, action_exp, else_exp, elsif_list=None):
        self.lineno = lineno
        self.type = 'cond'
        self.condition_exp = condition_exp
        self.action_exp = action_exp
        self.else_exp = else_exp
        self.elsif_list = elsif_list

    @property
    def children(self):
        c = [self.condition_exp, self.action_exp]
        if self.elsif_list:
            c.append(self.elsif_list)
        c.append(self.else_exp)
        return c


class ActionStatement(Node):
    def __init__(self, lineno, action, label_id=None):
        self.lineno = lineno
        self.type = 'action-sttmnt'
        self.action = action
        self.label_id = label_id

    @property
    def children(self):
        c = [self.action]
        if self.label_id:
            c.append(self.label_id)
        return c


class AssignmentAction(Node):
    def __init__(self, lineno, location, operator, expression):
        self.lineno = lineno
        self.location = location
        self.operator = operator
        self.expression = expression

    @property
    def children(self):
        return [self.location, self.operator, self.expression]


class AssigningOperator(Node):
    def __init__(self, lineno, closed_dyadic_op=None):
        self.lineno = lineno
        self.closed_dyadic_op = closed_dyadic_op

    @property
    def children(self):
        return [self.closed_dyadic_op] if self.closed_dyadic_op else []


class ReturnAction(Node):
    def __init__(self, lineno, expression=None):
        self.expression=expression

    @property
    def children(self):
        return [self.expression] if self.expression else []


class BuiltinCall(Node):
    def __init__(self, lineno, name, exp_list=None):
        self.lineno = lineno
        self.name = name
        self.exp_list = exp_list

    @property
    def children(self):
        c = [self.name]
        if self.exp_list:
            c.append(ListNode(self.exp_list))
        return c


class StepEnumeration(Node):
    def __init__(self, lineno, up, identifier, from_exp, to_exp, step_val=None):
        self.lineno = lineno
        self.type = "enum-up" if up else "enum-down"
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


class ProcedureCall(Node):
    def __init__(self, lineno, identifier, exp_list=None):
        self.lineno = lineno
        self.identifier = identifier
        self.exp_list = exp_list

    @property
    def children(self):
        c = [self.identifier]
        if self.exp_list:
            c.append(ListNode(self.exp_list))
        return c


class RangeEnum(Node):
    def __init__(self, lineno, up, identifier, discrete_mode):
        self.type = "rng-up" if up else "rng-down"
        self.up = up
        self.identifier = identifier
        self.discrete_mode = discrete_mode

    @property
    def children(self):
        return [self.identifier, self.discrete_mode]


class ControlPart(Node):
    def __init__(self, lineno, for_ctrl=None, while_ctrl=None):
        self.lineno = lineno
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


class DoAction(Node):
    def __init__(self, lineno, ctrl_part=None, action_st_list=None):
        self.lineno = lineno
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
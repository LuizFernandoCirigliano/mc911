class Node(object):
    type = ""

    # def __init__(self,type,children=None,leaf=None):
    #     self.type = type
    #     if children:
    #          self.children = children
    #     else:
    #          self.children = [ ]
    #     self.leaf = leaf

    def __str__(self):
        return self.type

    @property
    def children(self):
        return []


class ListNode(Node):
    def __init__(self, child_list):
        self.type = 'list'
        self.child_list = child_list

    @property
    def children(self):
        return self.child_list


class Program(Node):
    def __init__(self, statement_list):
        self.type = 'program'
        self.statement_list = statement_list

    @property
    def children(self):
        return self.statement_list


class DeclarationStatement(Node):
    def __init__(self, declaration_list):
        self.type = 'dcl-sttmnt'
        self.declaration_list = declaration_list

    @property
    def children(self):
        return self.declaration_list

class Declaration(Node):
    def __init__(self, identifier_list, mode, initialization=None):
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


class BinOp(Node):
    def __init__(self, left, op, right):
        self.type = 'bin-op'
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return str(self.op)

    @property
    def children(self):
        return [self.left, self.right]


class Reference(Node):
    def __init__(self, mode):
        self.type = 'reference'
        self.mode = mode

    @property
    def children(self):
        return [self.mode]


class BasicMode(Node):
    def __init__(self, mode_type):
        self.type = 'mode'
        self.mode_type = mode_type

    def __str__(self):
        return "Mode: " + self.mode_type

class LiteralRange(Node):
    def __init__(self, lb, ub):
        self.type = 'literal-range'
        self.lower_bound = lb
        self.upper_bound = ub

    @property
    def children(self):
        return [self.lower_bound, self.upper_bound]


class DiscreteRangeMode(Node):
    def __init__(self, mode, literal_range):
        self.type = 'discrete-range-mode'
        self.mode = mode
        self.literal_range = literal_range

    @property
    def children(self):
        return [self.mode, self.literal_range]


class Identifier(Node):
    def __init__(self, name):
        self.type = 'identifier'
        self.name = name

    def __str__(self):
        return "ID: " + self.name


class SynonymStatement(Node):
    def __init__(self, synonym_list: list):
        self.type = 'synonym-statement'
        self.synonym_list = synonym_list

    @property
    def children(self):
        return self.synonym_list


class Synonym(Node):
    def __init__(self, identifier_list, expression, mode=None):
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
    def __init__(self, value):
        self.type = 'iconst'
        self.value = value

    def __str__(self):
        return str(self.value)


class StringMode(Node):
    def __init__(self, length):
        self.type = 'string-mode'
        self.length = length

    @property
    def children(self):
        return [self.length]


class ArrayMode(Node):
    def __init__(self, index_mode_list, mode=Node):
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
    def __init__(self, newmode_list):
        self.type = 'new-mode-statement'
        self.newmode_list = newmode_list

    @property
    def children(self):
        return self.newmode_list


class ModeDefinition(Node):
    def __init__(self, identifier_list, mode):
        self.type = 'mode-definition'
        self.mode = mode
        self.identifier_list = identifier_list

    @property
    def children(self):
        return [ListNode(self.identifier_list), self.mode]


class ProcedureStatement(Node):
    def __init__(self, label_id, procedure_definition):
        self.type = 'procedure-statement'
        self.label_id = label_id
        self.procedure_definition = procedure_definition

    @property
    def children(self):
        return [self.label_id, self.procedure_definition]


class ProcedureDefintion(Node):
    def __init__(self, statement_list=None, formal_parameter_list=None, result_spec=None):
        self.type = 'procedure-definition'
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
    def __init__(self, id_list, parameter_spec):
        self.type = 'formal-parameter'
        self.parameter_spec = parameter_spec
        self.identifier_list = id_list

    @property
    def children(self):
        return [ListNode(self.identifier_list), self.parameter_spec]


class Spec(Node):
    def __init__(self, spec_type, mode, attribute=None):
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


class Attribute(Node):
    def __init__(self):
        self.type = 'attribute'

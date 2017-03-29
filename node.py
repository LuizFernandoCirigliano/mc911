class Node(object):
    type = ""
    # def __init__(self,type,children=None,leaf=None):
    #     self.type = type
    #     if children:
    #          self.children = children
    #     else:
    #          self.children = [ ]
    #     self.leaf = leaf
    def children(self):
        return []

    def __str__(self):
        return self.type

class Program(Node):
    def __init__(self, statement_list):
        self.type = 'program'
        self.statement_list = statement_list

    def children(self):
        return self.statement_list

class Declaration(Node):
    def __init__(self, identifier_list, mode, initialization=None):
        self.type = 'declaration'
        self.identifier_list = identifier_list
        self.mode = mode
        self.initialization = initialization


class BinOp(Node):
    def __init__(self, left, op, right):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        return str(self.op)

    def children(self):
        return [self.left, self.right]

class Mode(Node):
    def __init__(self, mode_type):
        self.mode_type = mode_type

class LiteralRange(Node):
    def __init__(self, lb, ub):
        self.
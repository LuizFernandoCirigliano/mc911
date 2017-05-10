import operator


class LVM:
    def __init__(self):
        self.sp = -1
        self.M = [None] * 100
        self.D = []
        self.P = []
        self.H = []

    def top_of_stack(self):
        return self.M[self.sp]

    def stack(self):
        return self.M[:self.sp+1]


class LVMOperator:
    op_name = None

    def __init__(self, op1=None, op2=None):
        self.op1 = op1
        self.op2 = op2

    @property
    def tuple(self):
        if self.op2 is not None:
            return (self.op_name, self.op1, self.op2)
        if self.op1 is not None:
            return (self.op_name, self.op1)
        else:
            return (self.op_name,)

    def __str__(self):
        return str(self.tuple)

    def __repr__(self):
        return str(self.tuple)

    def execute(self, lvm):
        pass


class LoadConstantOperator(LVMOperator):
    op_name = 'ldc'

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = self.op1


class BinOPOperator(LVMOperator):
    operator = None

    def execute(self, lvm):
        lvm.M[lvm.sp - 1] = self.operator(lvm.M[lvm.sp - 1], lvm.M[lvm.sp])
        lvm.sp -= 1


class AddOperator(BinOPOperator):
    op_name = 'add'
    operator = operator.add


class SubOperator(BinOPOperator):
    op_name = 'sub'
    operator = operator.sub


class MulOperator(BinOPOperator):
    op_name = 'mul'
    operator = operator.mul


class DivOperator(BinOPOperator):
    op_name = 'div'
    operator = operator.truediv


class LogicalAndOperator(BinOPOperator):
    op_name = 'and'
    operator = operator.and_

class LogicalOrOperator(BinOPOperator):
    op_name = 'or'
    operator = operator.or_

class LessOperator(BinOPOperator):
    op_name = 'les'
    operator = operator.lt

class EqualOperator(BinOPOperator):
    op_name = 'equ'
    operator = operator.eq

class NotEqualOperator(BinOPOperator):
    op_name = 'neq'
    operator = operator.ne

class LessOperator(BinOPOperator):
    op_name = 'les'
    operator = operator.lt

class UnOPOperator(LVMOperator):
    operator = None

    def execute(self, lvm):
        lvm.M[lvm.sp] = self.operator(lvm.M[lvm.sp])


class ModOperator(UnOPOperator):
    op_name = 'mod'
    operator = operator.mod


class NegateOperator(UnOPOperator):
    op_name = 'neg'
    operator = operator.neg


class AbsoluteOperator(UnOPOperator):
    op_name = 'abs'
    operator = operator.abs

class NotOperator(UnOPOperator):
    op_name = 'not'
    operator = operator.not_
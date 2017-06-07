import operator


class LVM:
    def __init__(self, operator_list):
        self.pc = 0
        self.sp = -1
        self.M = [None] * 10000
        self.bp = 0
        self.D = [None] * 10000
        self.P = operator_list
        self.H = []
        self.label_to_pc = {}

    def top_of_stack(self):
        return self.M[self.sp]

    def stack(self):
        return self.M[:self.sp + 1]

    def run(self):
        self.pc = 0
        while self.pc < len(self.P):
            self.P[self.pc].first_pass(lvm=self)
            self.pc += 1

        self.pc = 0
        while self.pc < len(self.P):
            # print(self.P[self.pc])
            self.P[self.pc].execute(lvm=self)
            self.pc += 1
            # print(self.stack())


class LVMOperator:
    op_name = None

    def __init__(self, op1=None, op2=None):
        self.op1 = op1
        self.op2 = op2

    @property
    def tuple(self):
        if self.op2 is not None:
            return self.op_name, self.op1, self.op2
        if self.op1 is not None:
            return self.op_name, self.op1
        else:
            return self.op_name,

    def __str__(self):
        return str(self.tuple)

    def __repr__(self):
        return str(self.tuple)

    def execute(self, lvm):
        pass

    def first_pass(self, lvm):
        pass


class StartOperator(LVMOperator):
    op_name = 'stp'

    def execute(self, lvm):
        lvm.sp = -1
        lvm.D[0] = 0


class LoadConstantOperator(LVMOperator):
    op_name = 'ldc'

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = self.op1


class LoadValueOperator(LVMOperator):
    op_name = 'ldv'

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = lvm.M[lvm.D[self.op1] + self.op2]


class LoadReferenceOperator(LVMOperator):
    op_name = 'ldr'

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = lvm.D[self.op1] + self.op2


class StoreValueOperator(LVMOperator):
    op_name = 'stv'

    def execute(self, lvm):
        lvm.M[lvm.D[self.op1] + self.op2] = lvm.M[lvm.sp]
        lvm.sp -= 1


class AllocateOperator(LVMOperator):
    op_name = 'alc'

    def execute(self, lvm):
        lvm.sp += self.op1


class DeallocateOperator(LVMOperator):
    op_name = 'dlc'

    def execute(self, lvm):
        lvm.sp -= self.op1


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


class LessOrEqualOperator(BinOPOperator):
    op_name = 'leq'
    operator = operator.le


class GreaterOperator(BinOPOperator):
    op_name = 'grt'
    operator = operator.gt


class GreaterOrEqualOperator(BinOPOperator):
    op_name = 'gte'
    operator = operator.ge


class EqualOperator(BinOPOperator):
    op_name = 'equ'
    operator = operator.eq


class NotEqualOperator(BinOPOperator):
    op_name = 'neq'
    operator = operator.ne


class ModOperator(BinOPOperator):
    op_name = 'mod'
    operator = operator.mod


class UnOPOperator(LVMOperator):
    operator = None

    def execute(self, lvm):
        lvm.M[lvm.sp] = self.operator(lvm.M[lvm.sp])


class NegateOperator(UnOPOperator):
    op_name = 'neg'
    operator = operator.neg


class AbsoluteOperator(UnOPOperator):
    op_name = 'abs'
    operator = operator.abs


class NotOperator(UnOPOperator):
    op_name = 'not'
    operator = operator.not_


class CallFunctionOperator(LVMOperator):
    op_name = "cfu"

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = lvm.pc + 1
        lvm.pc = self.op1


class EnterFunctionOperator(LVMOperator):
    op_name = "enf"

    def execute(self, lvm):
        lvm.sp += 1
        lvm.M[lvm.sp] = lvm.D[self.op1]
        lvm.D[self.op1] = lvm.sp + 1


class ReturnFromFunctionOperator(LVMOperator):
    op_name = "ret"

    def execute(self, lvm):
        lvm.D[self.op1] = lvm.M[lvm.sp]
        lvm.pc = lvm.M[lvm.sp - 1]
        lvm.sp -= self.op2 + 2


class IndexOperator(LVMOperator):
    op_name = "idx"

    def execute(self, lvm):
        lvm.M[lvm.sp - 1] += lvm.M[lvm.sp] * self.op1
        lvm.sp -= 1


class GetReferenceContentsOperator(LVMOperator):
    op_name = "grc"

    def execute(self, lvm):
        lvm.M[lvm.sp] = lvm.M[lvm.M[lvm.sp]]


class LoadMultipleValuesOperator(LVMOperator):
    op_name = "lmv"

    def execute(self, lvm):
        t = lvm.M[lvm.sp]
        k = self.op1
        lvm.M[lvm.sp: lvm.sp + k] = lvm.M[t: t + k]


class StoreMultipleValuesOperator(LVMOperator):
    op_name = "smv"

    def execute(self, lvm):
        k = self.op1
        t = lvm.M[lvm.sp - k]
        lvm.M[t: t + k] = lvm.M[lvm.sp - k + 1: lvm.sp + 1]
        lvm.sp -= k + 1


class StoreMultipleReferencesOperator(LVMOperator):
    op_name = "smr"

    def execute(self, lvm):
        t1 = lvm.M[lvm.sp - 1]
        t2 = lvm.M[lvm.sp]
        lvm.M[t1: t1 + self.op1] = lvm.M[t2: t2 + self.op1]
        lvm.sp -= 1


class StoreStringConstantOperator(LVMOperator):
    op_name = "sts"

    def execute(self, lvm):
        adr = lvm.M[lvm.sp]
        lvm.M[adr] = len(lvm.H[self.op1])
        for c in lvm.H[self.op1]:
            adr += 1
            lvm.M[adr] = c
        lvm.sp -= 1


class ReadValueOperator(LVMOperator):
    op_name = 'rdv'

    def execute(self, lvm):
        lvm.sp += 1
        val = input()
        if val == "TRUE" or val == "FALSE":
            val = int(val == "TRUE")
        try:
            val = int(val)
        except ValueError:
            pass
        lvm.M[lvm.sp] = val


class ReadStringOperator(LVMOperator):
    op_name = "rds"

    def execute(self, lvm):
        string = input()
        adr = lvm.M[lvm.sp]
        lvm.M[adr] = len(string)
        for k in string:
            adr += 1
            lvm.M[adr] = k
        lvm.sp -= 1


class PrintValueOperator(LVMOperator):
    op_name = "prv"

    def execute(self, lvm):
        if self.op1:
            print(chr(lvm.M[lvm.sp]))
        else:
            print(lvm.M[lvm.sp])
        lvm.sp -= 1


class PrintMultipleValuesOperator(LVMOperator):
    op_name = "prt"

    def execute(self, lvm):
        print(lvm.M[lvm.sp - self.op1 + 1:lvm.sp + 1])
        lvm.sp -= self.op1


class PrintStringConstantOperator(LVMOperator):
    op_name = "prc"

    def execute(self, lvm):
        print(lvm.H[self.op1], end="")


class PrintStringLocation(LVMOperator):
    op_name = "prs"

    def execute(self, lvm):
        adr = lvm.M[lvm.sp]
        length = lvm.M[adr]
        for i in range(length):
            adr += 1
            print(lvm.M[adr], end="")
            lvm.sp -= 1


class DefineLabelOperator(LVMOperator):
    op_name = "lbl"

    def first_pass(self, lvm):
        lvm.label_to_pc[self.op1] = lvm.pc


class NoOperationOperator(LVMOperator):
    op_name = "nop"


class StopProgramOperator(LVMOperator):
    op_name = "end"


class JumpOnFalseOperator(LVMOperator):
    op_name = 'jof'

    def execute(self, lvm):
        if not lvm.M[lvm.sp]:
            lvm.pc = lvm.label_to_pc[self.op1]
        lvm.sp -= 1


class JumpOperator(LVMOperator):
    op_name = 'jmp'

    def execute(self, lvm):
        lvm.pc = lvm.label_to_pc[self.op1]
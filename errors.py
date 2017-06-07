from enum import Enum
from environments import ExprType


class IssueType(Enum):
    WARNING = 1
    ERROR = 2


class SemanticIssue:
    def __init__(self, issue_type: IssueType):
        self.issue_type = issue_type

    def message(self):
        return ""


class SemanticError(SemanticIssue):
    def __init__(self):
        super().__init__(IssueType.ERROR)


class SemanticWarning(SemanticIssue):
    def __init__(self):
        super().__init__(IssueType.WARNING)


class TypeMismatch(SemanticError):
    def __init__(self, expected: ExprType, received: ExprType):
        super().__init__()
        self.expected = expected
        self.received = received

    def message(self):
        return "expected type {} but received {}".format(
            self.expected,
            self.received
        )


class InvalidType(SemanticError):
    def __init__(self, expr_type: ExprType):
        super().__init__()
        self.expr_type = expr_type

    def message(self):
        return "invalid type {}".format(self.expr_type)


class InvalidOperator(SemanticError):
    def __init__(self, operator_symbol: str, operand_type: ExprType):
        super().__init__()
        self.operator_symbol = operator_symbol
        self.operand_type = operand_type

    def message(self):
        return "invalid operator {} for {} operand".format(
            self.operator_symbol,
            self.operand_type
        )


class UndeclaredVariable(SemanticError):
    def __init__(self, var_name: str):
        super().__init__()
        self.var_name = var_name

    def message(self):
        return "identifier {} not declared".format(self.var_name)


class VariableRedeclaration(SemanticError):
    def __init__(self, var_name, prev_decl_line):
        super().__init__()
        self.var_name = var_name
        self.prev_decl_line = prev_decl_line

    def message(self):
        return "\"{}\" already declarated on line {}".format(
            self.var_name, self.prev_decl_line
        )


class CallingNonCallable(SemanticError):
    def __init__(self, var_name):
        super().__init__()
        self.var_name = var_name

    def message(self):
        return "Attempting to call {}, which is not a procedure".format(self.var_name)


class ArgCountError(SemanticError):
    def __init__(self, func_name, expected_num, received_num):
        super().__init__()
        self.func_name = func_name
        self.expected_num = expected_num
        self.received_num = received_num

    def message(self):
        return "Expected {} argument for procedure {}, but received {}".format(
            self.expected_num, self.func_name, self.received_num
        )
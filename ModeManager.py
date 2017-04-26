from case_ins_dict import CaseInsensitiveDict


class ExprType(object):
    def __init__(self, type: str, name: str=None):
        self.type = type
        self.name = name

    def __cmp__(self, other):
        return self.type == other.type and self.name == other.name

    def __str__(self):
        if self.name:
            return "{}-{}".format(self.type, self.name)
        return self.type

int_type = ExprType("int")
bool_type = ExprType("bool")
char_type = ExprType("char")
string_type = ExprType("string")
array_type = ExprType("array")

modes = CaseInsensitiveDict({'int': int_type,
         'bool': bool_type,
         'char': char_type,
         'string': string_type,
         'array': array_type})


def TypeGetter(mode_name: str, custom_name: str = None):
    if mode_name is None:
        return None
    if custom_name:
        mode_name = mode_name + "-" + custom_name
    if mode_name in modes:
        return modes.get(mode_name)
    modes[mode_name] = ExprType(mode_name)
    return modes[mode_name]
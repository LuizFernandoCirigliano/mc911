import ply.lex as lex

class LexerLuthor(object):
    # List of token names.   This is always required
    tokens = [
       'ICONST',
       'PLUS',
       'ARROW',
       'MINUS',
       'TIMES',
       'DIVIDE',
       'MODULO',
       'LPAREN',
       'RPAREN',
       'SEMI',
       'ASSIGN',
       'LBRACKET',
       'RBRACKET',
       'ID',
       'CCONST',
       'SCONST',
        'COMMA',
        'GT', 'LT', 'GTE', 'LTE', 'EQ', 'DIF', 'AND', 'OR',
        'COLON', 'CONCAT', 'EXCL'
    ]

    reserved = {'elsif': 'ELSIF', 'int': 'INT', 'fi': 'FI', 'false': 'FALSE', 'print': 'PRINT',
                'bool': 'BOOL', 'else': 'ELSE', 'end': 'END', 'od': 'OD', 'loc': 'LOC',
                'by': 'BY', 'true': 'TRUE', 'length': 'LENGTH', 'if': 'IF', 'return': 'RETURN',
                'in': 'IN', 'syn': 'SYN', 'returns': 'RETURNS', 'null': 'NULL', 'exit': 'EXIT',
                'upper': 'UPPER', 'do': 'DO', 'result': 'RESULT', 'abs': 'ABS', 'asc': 'ASC',
                'while': 'WHILE', 'array': 'ARRAY', 'chars': 'CHARS', 'for': 'FOR', 'down': 'DOWN',
                'proc': 'PROC', 'read': 'READ', 'char': 'CHAR', 'type': 'TYPE', 'then': 'THEN',
                'to': 'TO', 'ref': 'REF', 'lower': 'LOWER', 'num': 'NUM', 'dcl': 'DCL'}

    tokens += list(reserved.values())
    # Regular expression rules for simple tokens
    t_PLUS    = r'\+'
    t_ARROW = r'\-\>'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_MODULO = r'%'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_ASSIGN = r'='
    t_SEMI= r';'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_GT = r'>'
    t_LT = r'<'
    t_LTE = r'<='
    t_GTE = r'>='
    t_EQ = r'=='
    t_COLON = r':'
    t_DIF = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_CONCAT = r'&'
    t_EXCL = r'!'


    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'
    #t_CCONST = r'(?:\')(.)(?:\')'




    def t_ID(self, t):
      r'[a-zA-Z_][a-zA-Z_0-9]*'
      t.type = self.reserved.get(t.value,'ID')    # Check for reserved words
      return t

    # A regular expression rule with some action code
    def t_ICONST(self, t):
        r'\d+'
        t.value = int(t.value)
        return t



    def  t_CCONST(self, t):
      r'\'(?P<charval>.|\\.|\^\((?P<intval>\d+)\))?\''
      match = self.lexer.lexmatch
      t.value = match.group('intval')
      if t.value is None:
        value = match.group('charval')
        if value == "\\t":
            t.value = ord('\t')
        elif value == '\\n':
            t.value = ord('\n')
        elif value[0] == '\\':
            t.value = ord(value[1])
        else:
            t.value = ord(value)
      return t

    def  t_SCONST(self, t):
      r'\".*?\"'
      t.value =t.value[1:-1]
      return t

    def t_COMMENT(self, t):
      r'(//.*|\/\*(.|\n)*?\*/)'
      vector = t.value.splitlines()
      t.lexer.lineno += len(vector) - 1
      pass
      # No return value. Token discarded

    def t_COMMENT_ERROR(self, t):
      r'/\*(.|\n)*'
      print("%d: Unterminated comment" % t.lexer.lineno)
      t.lexer.skip(len(t.value))

    def  t_SCONST_ERROR(self, t):
      r'\".*'
      print("%d: Unterminated string" % t.lexer.lineno)
      pass

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


if __name__ == '__main__':
    from helpers import get_data
    lexer = LexerLuthor()
    data = get_data()
    lexer.lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.lexer.token()
        if not tok:
            break      # No more input
        print(tok)
import ply.lex as lex

# List of token names.   This is always required
tokens = [
   'ICONST',
   'PLUS',
   'ARROW',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'SEMI',
   'ASSIGN',
   'LBRACKET',
   'RBRACKET',
   'ID',
   'CCONST',
   'SCONST'
]

reserved = {
   'syn' : 'SYN',
   'dcl' : 'DCL',
   'print' : 'PRINT'
}

tokens += list(reserved.values())
# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_ARROW = r'\-\>'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_ASSIGN = r'\='
t_SEMI= r'\;'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'
#t_CCONST = r'(?:\')(.)(?:\')'




def t_ID(t):
  r'[a-zA-Z_][a-zA-Z_0-9]*'
  t.type = reserved.get(t.value,'ID')    # Check for reserved words
  return t

# A regular expression rule with some action code
def t_ICONST(t):
    r'\d+'
    t.value = int(t.value)
    return t



def  t_CCONST(t):
  r'\'(.|\n|\t)?\''
  #r'\'([^\\\n]|(\\.))*?\''
  if t.value == '\'\'':
    t.value = ''
  else:
    t.value =t.value[1]
  return t

def  t_SCONST(t):
  r'\".*\"'
  t.value =t.value[1:-1]
  return t


def t_COMMENT(t):
  r'(//.*|\/\*(.|\n)*?\*/)'
  pass
  # No return value. Token discarded
def t_COMMENT_ERROR(t):
  r'/\*(.|\n)*'
  print("%d: Unterminated comment" % t.lexer.lineno)
  t.lexer.skip(len(t.value))

def  t_SCONST_ERROR(t):
  r'\".*'
  print("%d: Unterminated string" % t.lexer.lineno)
  #t.lexer.skip(len(t.value))
  pass



# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def  t_BAD_ESCAPE_ERROR(t):
  r'\\.*'
  print("%d: Bad escape code %s" % (t.lexer.lineno, t.value))
  #t.lexer.skip(len(t.value))
  pass



# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


import sys

data = ""

# Build the lexer
lexer = lex.lex()

if len(sys.argv) == 1:
    # Test it out
    data = '''
    //3 + 4 * 10
      + -20 *2 ->
      ; [ ] =
      syn aba //oi
      // olarrrr
      oi
      /* linha ignorada
      "aaa"
      fim */
      a /* oooi */
      'x'
      "Hello world"
      /* oie \n */
      aa a
      \\aa
    '''
else:
    file_name = sys.argv[1]
    file = open(file_name)
    data = file.read()

lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)
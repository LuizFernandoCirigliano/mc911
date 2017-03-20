# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lyalex import LexerLuthor
from node import Node
from AST import make_html

class PeterParser(object):
    def p_expression_binop(self, p):
        '''expression : expression PLUS term
                      | expression MINUS term'''
        p[0] = Node('expression', [p[1], p[3]], p[2])

    def p_expression_term(self, p):
        'expression : term'
        p[0] = Node('expression', [p[1]], 'term')

    def p_expression_declaration(self, p):
        'expression : declaration'
        p[0] = Node('expression', [p[1]], 'declaration')

    def p_declaration(self, p):
        'declaration : DCL ID type SEMI'
        p[0] = Node('declaration', [p[3]], p[2])

    def p_term_binop(self, p):
        '''term : term TIMES factor
                | term DIVIDE factor'''
        p[0] =  Node("term", [p[1], p[3]], p[2])

    def p_term_factor(self, p):
        'term : factor'
        p[0] = Node('term', [p[1]], 'factor')

    def p_factor_num(self, p):
        'factor : ICONST'
        p[0] = Node('factor', None, p[1])

    def p_factor_expr(self, p):
        'factor : LPAREN expression RPAREN'
        p[0] = Node('factor', [p[2]], '( )')

    def p_type_int(self, p):
        'type : INT'
        p[0] = Node('type', None, p[1])

    def p_empty(self, p):
        'empty :'
        pass

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")

    def __init__(self, **kwargs):
        self.lexer = LexerLuthor()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)


    def parse(self, data):
        return self.parser.parse(data, self.lexer.lexer)

if __name__ == '__main__':
    from migue import get_data, bin_op_data
    pp = PeterParser()
    data = get_data()
    # Build the parser
    result = pp.parse(data)

    html = make_html(result)
    with open("ast.html", 'w') as html_file:
        html_file.write(html)
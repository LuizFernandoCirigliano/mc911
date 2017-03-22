# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lyalex import LexerLuthor
from node import Node
from AST import make_html

class PeterParser(object):
    start = 'program'
    def p_program(self, p):
        'program : statement_list'
        p[0] = Node('program', [p[1]], '')

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement
        '''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_statement(self, p):
        'statement : declaration_statement'
        p[0] = p[1]

    def p_declaration_statement(self, p):
        'declaration_statement : DCL declaration_list SEMI'
        p[0] = Node('declaration_statement', [p[2]], '')

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration COMMA declaration_list'''
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_declaration(self, p):
        '''declaration : identifier_list mode
                       | identifier_list mode initialization'''
        p[0] = Node('declaration', p[1:], '')

    def p_mode(self, p):
        '''mode : mode_name
                | discrete_mode
                | reference_mode
                | composite_mode'''
        p[0] = p[1]

    def p_mode_name(self, p):
        '''mode_name : identifier'''
        p[0] = p[1]

    def p_discrete_mode(self, p):
        '''discrete_mode : int_mode
                         | bool_mode
                         | char_mode
                         | discrete_range_mode'''
        p[0] = p[1]

    def p_reference_mode(self, p):
        'reference_mode : REF mode'
        p[0] = Node('reference_mode', [p[2]], '')

    def p_int_mode(self, p):
        'int_mode : INT'
        p[0] = Node('int', [], p[1])

    def p_char_mode(self, p):
        'char_mode : CHAR'
        p[0] = Node('char', [], p[1])

    def p_bool_mode(self, p):
        'bool_mode : BOOL'
        p[0] = Node('bool', [], p[1])

    def p_discrete_range_mode(self, p):
        '''discrete_range_mode : discrete_mode_name LPAREN literal_range RPAREN
                               | discrete_mode LPAREN literal_range RPAREN '''
        p[0] = Node('discrete_range_mode', [p[1], p[3]], '')

    def p_discrete_mode_name(self, p):
        'discrete_mode_name : identifier'
        p[0] = Node('discrete_mode_name', [p[1]], '')

    def p_literal_range(self, p):
        'literal_range : expression COLON expression'
        p[0] = Node('literal_range', [p[1], p[3]], '')

    def p_identifier_list(self, p):
        '''identifier_list : identifier
                           | identifier_list COMMA identifier '''

        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_identifier(self, p):
        '''identifier : ID'''
        p[0] = Node('identifier', [], p[1])

    def p_initialization(self, p):
        '''initialization : ASSIGN expression'''
        p[0] = Node('initialization', [p[2]], '')

    def p_expression_binop(self, p):
        '''expression : expression PLUS term
                      | expression MINUS term'''
        p[0] = Node('expression', [p[1], p[3]], p[2])

    def p_expression_term(self, p):
        'expression : term'
        p[0] = p[1]

    def p_term_binop(self, p):
        '''term : term TIMES factor
                | term DIVIDE factor'''
        p[0] =  Node("term", [p[1], p[3]], p[2])

    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]

    def p_factor_num(self, p):
        'factor : ICONST'
        p[0] = Node('factor', None, p[1])

    def p_factor_expr(self, p):
        'factor : LPAREN expression RPAREN'
        p[0] = Node('factor', [p[2]], '( )')

    def p_type_int(self, p):
        'type : INT'
        p[0] = Node('type', None, p[1])

    def p_composite_mode(self, p):
        '''composite_mode : string_mode
                          | array_mode'''
        p[0] = p[1]

    def p_string_mode(self, p):
        'string_mode : CHARS LBRACKET string_length RBRACKET'
        p[0] = Node('string_mode', [p[3]], '')

    def p_string_length(self, p):
        'string_length : ICONST'
        p[0] = Node('string_length', [], p[1])

    def p_array_mode(self, p):
        'array_mode : ARRAY LBRACKET index_mode_list RBRACKET mode'
        p[0] = Node('array_mode', [p[3], p[5]], '')

    def p_index_mode_list(self, p):
        '''index_mode_list : index_mode
                           | index_mode_list COMMA index_mode'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


    def p_index_mode(self, p):
        '''index_mode : discrete_mode
                      | literal_range'''
        p[0] = p[1]


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
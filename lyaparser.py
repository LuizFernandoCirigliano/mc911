# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lyalex import LexerLuthor
import node
from AST import make_html

class PeterParser(object):
    start = 'program'
    def p_program(self, p):
        'program : statement_list'
        p[0] = node.Program(p[1])

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement
        '''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_statement(self, p):
        '''statement : declaration_statement
                              | synonym_statement
                              | newmode_statement
                              | procedure_statement'''
        p[0] = p[1]

    def p_declaration_statement(self, p):
        'declaration_statement : DCL declaration_list SEMI'
        p[0] = p[1]

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration COMMA declaration_list'''
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_declaration(self, p):
        '''declaration : identifier_list mode
                       | identifier_list mode initialization'''
        p[0] = node.Declaration(*p[1:])

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
        '''discrete_mode : basic_mode
                         | discrete_range_mode'''
        p[0] = p[1]

    def p_reference_mode(self, p):
        'reference_mode : REF mode'
        p[0] = Node('reference_mode', [p[2]], '')

    def p_basic_mode(self, p):
        '''basic_mode : INT
                      | CHAR
                      | BOOL'''
        p[0] = node.Mode(p[1])

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

    def p_synonym_statement(self, p):
        'synonym_statement : SYN synonym_list SEMI'
        p[0] = Node('synonym_statement', [p[2]], '')

    def p_synonym_list(self, p):
        '''synonym_list : synonym_definition
                                  | synonym_list COMMA synonym_definition'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_synonym_definition(self, p):
        '''synonym_definition : identifier_list ASSIGN expression
                                              | identifier_list mode ASSIGN expression'''
        if len(p) == 4:
            p[0] = Node('synonym_definition', [p[1], p[3]], '')
        else:
            p[0] = Node('synonym_definition', [p[1], p[2], p[4]], '')

    def p_newmode_statement(self, p):
        'newmode_statement : TYPE newmode_list SEMI'
        p[0] = Node('newmode_statement', [p[2]], '')

    def p_newmode_list(self, p):
        '''newmode_list : mode_definition
                                    | newmode_list COMMA mode_definition'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_mode_definition(self, p):
        'mode_definition : identifier_list ASSIGN mode'
        p[0] = Node('mode_definition', [p[1], p[3]], '')

    def p_procedure_statement(self, p):
        'procedure_statement : label_id COLON procedure_definition SEMI'
        p[0] = Node('procedure_statement', [p[1], p[3]], '')

    def p_procedure_definition_empty(self, p):
        'procedure_definition : PROC LPAREN RPAREN SEMI END'
        p[0] = Node('procedure_definition', None, '')

    def p_procedure_definition_statement_only(self, p):
        'procedure_definition : PROC LPAREN RPAREN SEMI statement_list END'
        p[0] = Node('procedure_definition', [p[5]], '')

    def p_procedure_definition_result_only(self, p):
        'procedure_definition : PROC LPAREN RPAREN result_spec SEMI END'
        p[0] = Node('procedure_definition', [p[4]], '')

    def p_procedure_definition_parameter_only(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN SEMI END'
        p[0] = Node('procedure_definition', [p[3]], '')

    def p_procedure_definition_result_statement(self, p):
        'procedure_definition : PROC LPAREN RPAREN result_spec SEMI statement_list END'
        p[0] = Node('procedure_definition', [p[4], p[6]], '')

    def p_procedure_definition_parameter_statement(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN SEMI statement_list END'
        p[0] = Node('procedure_definition', [p[3], p[6]], '')

    def p_procedure_definition_parameter_result(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN result_spec SEMI END'
        p[0] = Node('procedure_definition', [p[3], p[5]], '')

    def p_procedure_definition_all(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN result_spec SEMI statement_list END'
        p[0] = Node('procedure_definition', [p[3], p[5], p[7]], '')

    def p_formal_parameter_list(self, p):
        '''formal_parameter_list : formal_parameter
                                                  | formal_parameter_list COMMA formal_parameter'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_formal_parameter(self, p):
        'formal_parameter : identifier_list parameter_spec'
        p[0] = Node('formal_parameter', [p[1], p[2]], '')

    def p_parameter_spec(self, p):
        '''parameter_spec : mode
                                        | mode parameter_attribute'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('parameter_spec', [p[1], p[2]], '')

    def p_parameter_attribute(self, p):
        'parameter_attribute : LOC'
        p[0] = Node('parameter_attribute', None, p[1])

    def p_result_spec(self, p):
        '''result_spec : RETURNS LPAREN mode RPAREN
                                | RETURNS LPAREN mode result_attribute RPAREN'''
        if len(p) == 5:
            p[0] = Node('result_spec', [p[3]], '')
        else:
            p[0] = Node('result_spec', [p[3], p[4]], '')

    def p_result_attribute(self, p):
        'result_attribute : LOC'
        p[0] = Node('result_attribute', None, p[1])

    def p_label_id(self, p):
        'label_id : identifier'
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
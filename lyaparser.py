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
        p[0] = node.Program(p.lexer.lineno, p[1])

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement
        '''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_statement(self, p):
        '''statement : declaration_statement
                              | synonym_statement
                              | newmode_statement
                              | procedure_statement
                              | action_statement'''
        p[0] = p[1]

    def p_declaration_statement(self, p):
        'declaration_statement : DCL declaration_list SEMI'
        p[0] = node.DeclarationStatement(p.lexer.lineno, p[2])

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration COMMA declaration_list'''
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_declaration(self, p):
        '''declaration : identifier_list mode
                       | identifier_list mode initialization'''
        p[0] = node.Declaration(p.lexer.lineno, *p[1:])

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
        p[0] = node.ReferenceMode(p.lexer.lineno, p[2])

    def p_basic_mode(self, p):
        '''basic_mode : INT
                      | CHAR
                      | BOOL'''
        p[0] = node.BasicMode(p.lexer.lineno, p[1])

    def p_discrete_range_mode(self, p):
        '''discrete_range_mode : discrete_mode_name LPAREN literal_range RPAREN
                               | discrete_mode LPAREN literal_range RPAREN '''
        p[0] = node.DiscreteRangeMode(p.lexer.lineno, p[1], p[3])

    def p_discrete_mode_name(self, p):
        'discrete_mode_name : identifier'
        p[0] = p[1]

    def p_literal_range(self, p):
        'literal_range : expression COLON expression'
        p[0] = node.LiteralRange(p.lexer.lineno, p[1], p[3])

    def p_identifier_list(self, p):
        '''identifier_list : identifier
                           | identifier_list COMMA identifier '''

        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_identifier(self, p):
        '''identifier : ID'''
        p[0] = node.Identifier(p.lexer.lineno, p[1])

    def p_initialization(self, p):
        '''initialization : ASSIGN expression'''
        p[0] = p[2]


    def p_location(self, p):
        '''location :    identifier
                         | dereferenced_reference
                         | string_element
                         | string_slice
                         | array_element
                         | array_slice
                         | call_action'''
        p[0] = p[1]

    def p_dereferenced_reference(self, p):
        'dereferenced_reference : location ARROW'
        p[0] = node.DereferenceLocation(p.lexer.lineno, p[1])

    def p_string_element(self, p):
        'string_element : identifier LBRACKET start_element RBRACKET'
        p[0] = node.StringElement(p.lexer.lineno, p[1], p[3])

    def p_start_element(self, p):
        'start_element : expression'
        p[0] = p[1]

    def p_string_slice(self, p):
        'string_slice : identifier LBRACKET expression COLON expression RBRACKET'
        p[0] = node.Slice(p.lexer.lineno, 'string', p[1], p[3], p[5])

    def p_array_element(self, p):
        'array_element : location LBRACKET expression_list RBRACKET'
        p[0] = node.ArrayElement(p.lexer.lineno, p[1], p[3])

    def p_expression_list(self, p):
        '''expression_list : expression
                          | expression_list COMMA expression'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_array_slice(self, p):
        'array_slice : location LBRACKET expression COLON expression RBRACKET'
        p[0] = node.Slice(p.lexer.lineno, 'array', p[1], p[3], p[5])

    def p_primitive_value(self, p):
        '''primitive_value : literal
                           | value_array_element
                           | value_array_slice
                           | parenthesized_expression'''
        p[0] = p[1]

    def p_literal_int(self, p):
        '''literal : ICONST'''
        p[0] = node.LiteralNode(p.lexer.lineno, p[1], 'int')

    def p_literal_bool(self, p):
        '''literal : TRUE
                   | FALSE'''
        p[0] = node.LiteralNode(p.lexer.lineno, p[1] == 'true', 'bool')

    def p_literal_char(self, p):
        'literal : CCONST'
        p[0] = node.LiteralNode(p.lexer.lineno, p[1], 'char')

    def p_literal_string(self, p):
        'literal : SCONST'
        p[0] = node.LiteralNode(p.lexer.lineno, p[1], 'string')

    def p_literal_null(self, p):
        'literal : NULL'
        p[0] = node.LiteralNode(p.lexer.lineno, p[1], 'null')

    def p_value_array_element(self, p):
        'value_array_element : primitive_value LBRACKET expression_list RBRACKET'
        p[0] = node.Element(p.lexer.lineno, 'value-array', p[1], p[3])

    def p_value_array_slice(self, p):
        'value_array_slice : primitive_value LBRACKET expression COLON expression RBRACKET'
        p[0] = node.Slice(p.lexer.lineno, 'value-array', p[1], p[3], p[5])

    def p_parenthesized_expression(self, p):
        'parenthesized_expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression(self, p):
        '''expression : operand0
                     | conditional_expression'''
        p[0] = p[1]

    def p_conditional_expression(self, p):
        '''conditional_expression : IF expression THEN expression ELSE expression FI
                                 | IF expression THEN expression elsif_list ELSE expression FI'''

        elsif_list = p[5] if len(p) == 9 else None
        else_exp = p[7] if len(p) == 9 else p[6]
        p[0] = node.ConditionalExpression(p.lexer.lineno, p[2], p[4], else_exp, elsif_list)

    def p_elsif_list(self, p):
        '''elsif_list : elsif_expression
                      | elsif_list elsif_expression'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_elsif_expression(self, p):
        '''elsif_expression : ELSIF expression THEN expression'''
        p[0] = node.ElsIf(p.lexer.lineno, p[2], p[4])

    def p_operand0(self, p):
        '''operand0 : operand1
                    | operand0 operator1 operand1'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = node.BinOp(p.lexer.lineno, p[1], p[2], p[3])

    def p_operator1(self, p):
        '''operator1 : relational_operator
                    | IN'''
        p[0] = p[1]

    def p_relational_operator(self, p):
        '''relational_operator : AND
                                | OR
                                | GT
                                | LT
                                | GTE
                                | LTE
                                | EQ
                                | DIF'''
        p[0] = node.OperatorNode(p.lexer.lineno, p[1])

    def p_operand1(self, p):
        '''operand1 : operand2
                    | operand1 operator2 operand2'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = node.BinOp(p.lexer.lineno, p[1], p[2], p[3])

    def p_operator2(self, p):
        '''operator2 : PLUS
                    | MINUS
                    | CONCAT'''
        p[0] = node.OperatorNode(p.lexer.lineno, p[1])

    def p_operand2(self, p):
        '''operand2 : operand3
                    | operand2 arithmetic_multiplicative_operator operand3'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = node.BinOp(p.lexer.lineno, p[1], p[2], p[3])

    def p_arithmetic_multiplicative_operator(self, p):
        '''arithmetic_multiplicative_operator : TIMES
                                                | DIVIDE
                                                | MODULO'''
        p[0] = node.OperatorNode(p.lexer.lineno, p[1])

    def p_operand3(self, p):
        '''operand3 : operand4
                    | monadic_operator operand4
                    '''
        if len(p) == 3:
            p[0] = node.UnOp(p.lexer.lineno, p[1], p[2])
        else:
            p[0] = node.BasicNode(p.lexer.lineno, p[1]) if type(p[1]) == str else p[1]

    def p_monadic_operator(self, p):
        '''monadic_operator : MINUS
                            | EXCL'''
        p[0] = node.OperatorNode(p.lexer.lineno, p[1])

    def p_operand4(self, p):
        '''operand4 : location
                    | referenced_location
                    | primitive_value'''
        p[0] = p[1]

    def p_referenced_location(self, p):
        'referenced_location : ARROW location'
        p[0] = node.ReferenceLocation(p.lexer.lineno, p[2])

    def p_composite_mode(self, p):
        '''composite_mode : string_mode
                          | array_mode'''
        p[0] = p[1]

    def p_string_mode(self, p):
        'string_mode : CHARS LBRACKET string_length RBRACKET'
        p[0] = node.StringMode(p.lexer.lineno, p[3])

    def p_string_length(self, p):
        'string_length : ICONST'
        p[0] = node.LiteralNode(p.lexer.lineno, p[1], 'int')

    def p_array_mode(self, p):
        'array_mode : ARRAY LBRACKET index_mode_list RBRACKET mode'
        p[0] = node.ArrayMode(p.lexer.lineno, p[3], p[5])

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
        p[0] = node.SynonymStatement(p.lexer.lineno, p[2])

    def p_synonym_list(self, p):
        '''synonym_list : synonym_definition
                        | synonym_list COMMA synonym_definition'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_synonym_definition(self, p):
        '''synonym_definition : identifier_list ASSIGN expression
                              | identifier_list mode ASSIGN expression'''
        mode = None
        exp = p[3]
        if len(p) == 5:
            mode = p[2]
            exp = p[4]
        p[0] = node.Synonym(p.lexer.lineno, p[1], exp, mode)

    def p_newmode_statement(self, p):
        'newmode_statement : TYPE newmode_list SEMI'
        p[0] = node.NewModeStatement(p.lexer.lineno, p[2])

    def p_newmode_list(self, p):
        '''newmode_list : mode_definition
                                    | newmode_list COMMA mode_definition'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_mode_definition(self, p):
        'mode_definition : identifier_list ASSIGN mode'
        p[0] = node.ModeDefinition(p.lexer.lineno, p[1], p[3])

    def p_procedure_statement(self, p):
        'procedure_statement : label_id COLON procedure_definition SEMI'
        p[0] = node.ProcedureStatement(p.lexer.lineno, p[1], p[3])

    def p_procedure_definition_empty(self, p):
        'procedure_definition : PROC LPAREN RPAREN SEMI END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno)

    def p_procedure_definition_statement_only(self, p):
        'procedure_definition : PROC LPAREN RPAREN SEMI statement_list END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, statement_list=p[5])

    def p_procedure_definition_result_only(self, p):
        'procedure_definition : PROC LPAREN RPAREN result_spec SEMI END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, result_spec=p[4])

    def p_procedure_definition_parameter_only(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN SEMI END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, formal_parameter_list=p[3])

    def p_procedure_definition_result_statement(self, p):
        'procedure_definition : PROC LPAREN RPAREN result_spec SEMI statement_list END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, result_spec=p[4], statement_list=p[6])

    def p_procedure_definition_parameter_statement(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN SEMI statement_list END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, formal_parameter_list=p[3], statement_list=p[6])

    def p_procedure_definition_parameter_result(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN result_spec SEMI END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, formal_parameter_list=p[3], result_spec=p[5])

    def p_procedure_definition_all(self, p):
        'procedure_definition : PROC LPAREN formal_parameter_list RPAREN result_spec SEMI statement_list END'
        p[0] = node.ProcedureDefintion(p.lexer.lineno, formal_parameter_list=p[3], result_spec=p[5], statement_list=p[7])

    def p_formal_parameter_list(self, p):
        '''formal_parameter_list : formal_parameter
                                                  | formal_parameter_list COMMA formal_parameter'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_formal_parameter(self, p):
        'formal_parameter : identifier_list parameter_spec'
        p[0] = node.FormalParameter(p.lexer.lineno, p[1], p[2])

    def p_attribute(self, p):
        'attribute : LOC'
        p[0] = node.BasicNode(p.lexer.lineno, p[1])

    def p_parameter_spec(self, p):
        '''parameter_spec : mode
                         | mode attribute'''
        parameter_attrib = None
        if len(p) == 3:
            parameter_attrib = p[2]
        p[0] = node.Spec(p.lexer.lineno, spec_type='parameter', mode=p[1], attribute=parameter_attrib)


    def p_result_spec(self, p):
        '''result_spec : RETURNS LPAREN mode RPAREN
                        | RETURNS LPAREN mode attribute RPAREN'''
        result_attrib = None
        if len(p) == 6:
            result_attrib = p[4]
        p[0] = node.Spec(p.lexer.lineno, spec_type='result', mode=p[3], attribute=result_attrib)

    def p_action_statement(self, p):
        '''action_statement : action SEMI
                            | label_id COLON action SEMI'''
        action, label_id = (p[1], None) if len(p) == 3 else (p[3], p[1])
        p[0] = node.ActionStatement(p.lexer.lineno, action, label_id)

    def p_action_statement_list(self, p):
        '''action_statement_list : action_statement
                                 | action_statement_list action_statement'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_action(self, p):
        '''action : bracketed_action
                      | assignment_action
                      | call_action
                      | exit_action
                      | return_action
                      | result_action'''
        p[0] = p[1]

    def p_bracketed_action(self, p):
        '''bracketed_action : if_action
                            | do_action'''
        p[0] = p[1]

    def p_assignment_action(self, p):
        'assignment_action : location assigning_operator expression'
        p[0] = node.AssignmentAction(p.lexer.lineno, p[1], p[2], p[3])

    def p_assigning_operator(self, p):
        '''assigning_operator : ASSIGN
                             | closed_dyadic_operator ASSIGN'''
        op = p[1] if len(p) > 2 else None
        p[0] = node.AssigningOperator(p.lexer.lineno, op)

    def p_closed_dyadic_operator(self, p):
        '''closed_dyadic_operator : PLUS
                                    | MINUS
                                    | TIMES
                                    | DIVIDE
                                    | MODULO
                                    | CONCAT'''
        p[0] = p[1]

    def p_if_action(self, p):
        '''if_action : IF expression then_clause FI
                     | IF expression then_clause else_clause FI
                     | IF expression then_clause elsif_clause else_clause FI'''
        p[0] = node.IfAction(p.lexer.lineno, *p[2:len(p)-1])

    def p_then_clause(self, p):
        '''then_clause : THEN
                       | THEN action_statement_list'''
        p[0] = node.ListNode(p[2], 'then') if len(p) > 2 else None

    def p_else_clause(self, p):
        '''else_clause : ELSE
                       | ELSE action_statement_list'''
        p[0] = node.ListNode(p[2], 'else') if len(p) > 2 else None

    def p_elsif_clause(self, p):
        '''elsif_clause : elsif_clause_list'''
        p[0] = node.ListNode(p[1], 'elsif')

    def p_elsif_clause_list(self, p):
        '''elsif_clause_list : elsif_clause_exp
                             | elsif_clause_list elsif_clause_exp'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_elsif_clause_exp(self, p):
        '''elsif_clause_exp : ELSIF expression then_clause'''
        p[0] = node.IfAction(p.lexer.lineno, *p[2:])

    def p_do_action(self, p):
        '''do_action : DO OD
                    | DO control_part SEMI OD
                    | DO action_statement_list OD
                    | DO control_part SEMI action_statement_list OD'''
        ctrl_part, action_list = None, None
        if len(p) == 5:
            ctrl_part = p[2]
        elif len(p) == 4:
            action_list = p[2]
        elif len(p) == 6:
            ctrl_part, action_list = p[2], p[4]
        p[0] = node.DoAction(p.lexer.lineno, ctrl_part, action_list)

    def p_control_part_for(self, p):
        '''control_part : for_control
                        | for_control while_control'''
        p[0] = node.ControlPart(p.lexer.lineno, *p[1:])

    def p_control_part_while(self, p):
        '''control_part      : while_control'''
        p[0] = node.ControlPart(p.lexer.lineno, while_ctrl=p[1])

    def p_for_control(self, p):
        'for_control : FOR iteration'
        p[0] = p[2]

    def p_iteration(self, p):
        '''iteration : step_enumeration
                    | range_enumeration'''
        p[0] = p[1]

    def p_step_enumeration_up(self, p):
        '''step_enumeration : identifier ASSIGN expression TO expression
                             | identifier ASSIGN expression step_value TO expression'''
        identifier = p[1]
        from_exp = p[3]
        to_exp = p[5] if len(p) == 6 else p[6]
        step_val = p[4] if len(p) > 6 else None
        p[0] = node.StepEnumeration(p.lexer.lineno, True, identifier, from_exp, to_exp, step_val)

    def p_step_enumeration_down(self, p):
        '''step_enumeration : identifier ASSIGN expression DOWN TO expression
                             | identifier ASSIGN expression step_value DOWN TO expression'''
        identifier = p[1]
        from_exp = p[3]
        to_exp = p[6] if len(p) == 7 else p[7]
        step_val = p[4] if len(p) == 7 else None
        p[0] = node.StepEnumeration(p.lexer.lineno, False, identifier, from_exp, to_exp, step_val)

    def p_step_value(self, p):
        'step_value : BY expression'
        p[0] = p[2]

    def p_range_enumeration(self, p):
        '''range_enumeration : identifier IN discrete_mode
                            | identifier DOWN IN discrete_mode'''
        up = len(p) == 4
        p[0] = node.RangeEnum(p.lexer.lineno, up, p[1], p[len(p) - 1])

    def p_while_control(self, p):
        'while_control : WHILE expression'
        p[0] = p[2]

    def p_call_action(self, p):
        '''call_action : procedure_call
                        | builtin_call'''
        p[0] = p[1]

    def p_procedure_call(self, p):
        '''procedure_call : identifier LPAREN RPAREN
                         | identifier LPAREN expression_list RPAREN'''
        exp_list = p[3] if len(p) > 4 else None
        p[0] = node.ProcedureCall(p.lexer.lineno, p[1], exp_list)

    def p_exit_action(self, p):
        'exit_action : EXIT identifier'
        p[0] = node.PassNode(p.lexer.lineno, 'EXIT', p[2])

    def p_return_action(self, p):
        '''return_action : RETURN
                        | RETURN expression'''
        exp = p[2] if len(p) > 2 else None
        p[0] = node.ReturnAction(p.lexer.lineno, exp)

    def p_result_action(self, p):
        'result_action : RESULT expression'
        p[0] = node.PassNode(p.lexer.lineno, 'RESULT', p[2])

    def p_builtin_call(self, p):
        '''builtin_call : builtin_name LPAREN RPAREN
                        | builtin_name LPAREN expression_list RPAREN'''
        exp_list =  p[3] if len(p) > 4 else None
        p[0] = node.BuiltinCall(p.lexer.lineno, p[1], exp_list)

    def p_builtin_name(self, p):
        '''builtin_name : ABS
                                  | ASC
                                  | NUM
                                  | UPPER
                                  | LOWER
                                  | LENGTH
                                  | READ
                                  | PRINT'''
        p[0] = node.BuiltinName(p.lexer.lineno, p[1])

    def p_label_id(self, p):
        'label_id : identifier'
        p[0] = p[1]

    # def p_empty(self, p):
    #     'empty :'
    #     pass

    # Error rule for syntax errors
    def p_error(self, p):
        if p is not None:
            print("ERROR (syntax) on line %s" % (p.lexer.lineno))
        else:
            print("Unexpected end of input")

    def __init__(self, **kwargs):
        self.lexer = LexerLuthor(debug=True)
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=True)


    def parse(self, data):
        return self.parser.parse(data, self.lexer.lexer)

if __name__ == '__main__':
    from helpers import get_data, bin_op_data
    pp = PeterParser()
    data = get_data()
    # Build the parser
    result = pp.parse(data)

    html = make_html(result)
    with open("ast.html", 'w') as html_file:
        html_file.write(html)
from lyaparser import PeterParser
from visualization import make_html
from visitors import semantic_visitor
import sys

if __name__ == '__main__':
    file_name = sys.argv[1]
    file = open(file_name)
    data = file.read()

    # Build the parser
    pp = PeterParser()
    AST = pp.parse(data)
    AST.validate_node()
    semantic_visitor.visit_tree(AST)

    html = make_html(AST)
    with open("{}.ast.html".format(file_name), 'w') as html_file:
        html_file.write(html)
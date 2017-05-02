from lyaparser import PeterParser
from visualization import make_html
from visitors import semantic_visitor

if __name__ == '__main__':
    from helpers import get_data
    pp = PeterParser()
    data = get_data()

    # Build the parser
    AST = pp.parse(data)
    AST.validate_node()
    semantic_visitor.visit_tree(AST)

    html = make_html(AST)
    with open("ast.html", 'w') as html_file:
        html_file.write(html)
from lyaparser import PeterParser
from visualization import make_html
from visitors import semantic_visitor, lvm_visitor
from LVM import LVM
import sys

if __name__ == '__main__':
    file_name = sys.argv[1]
    file = open(file_name)
    data = file.read()

    # Build the parser
    pp = PeterParser()
    AST = pp.parse(data)
    if AST:
        AST.validate_node()
        semantic_visitor.visit_tree(AST)

        if AST.is_valid:
            lvm_visitor.visit_tree(AST)
            print(lvm_visitor.result)

            lvm = LVM(lvm_visitor.result)
            lvm.run()
            print(lvm.stack())

        html = make_html(AST)
        with open("{}.ast.html".format(file_name), 'w') as html_file:
            html_file.write(html)
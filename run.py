from lyaparser import PeterParser
from visualization import make_html
from visitors import semantic_visitor
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
        AST.validation_visitor()
        semantic_visitor.visit_tree(AST)

        html = make_html(AST)
        with open("{}.ast.html".format(file_name), 'w') as html_file:
            html_file.write(html)

        if AST.is_valid:
            inst_list = AST.lvm_visitor()
            print(inst_list)
            print("STARTING PROGRAM")

            #lvm = LVM(lvm_visitor.result)
            lvm = LVM(inst_list)
            lvm.run()
            print("DONE---Printing Stack")
            print(lvm.stack())
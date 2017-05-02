from node import Node
from environments import cur_context

class GenericVisitor:
    @staticmethod
    def f(node: Node):
        pass

    def __init__(self, inner_visitor=None):
        self.result = []
        self.inner_visitor = inner_visitor

    def visit_tree(self, root: Node):
        if self.inner_visitor:
            self.inner_visitor.visit_tree(root)
        self.__visit__(root)

    def __visit__(self, root: Node):
        for c in root.children:
            self.__visit__(c)

        local_result = self.f(root)
        if local_result:
            self.result.append(local_result)


class ValidationVisitor(GenericVisitor):
    @staticmethod
    def f(node: Node):
        node.validate_node()

    def visit_tree(self, root: Node):
        cur_context.reset()
        super().visit_tree(root)


class PrintErrorVisitor(GenericVisitor):
    @staticmethod
    def f(node: Node):
        node.print_error()

class VisualizationVisitor(GenericVisitor):
    pass


semantic_visitor = PrintErrorVisitor(ValidationVisitor())

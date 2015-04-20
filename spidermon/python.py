import six
import ast

from .exceptions import InvalidExpression


class Interpreter(object):

    ast_allowed_nodes = (
        'expr', 'name', 'load', 'call', 'store',
        'str', 'unicode', 'num', 'list', 'dict', 'set', 'tuple',  # Data types
        'unaryop', 'usub',  # Unary arithmetic operators
        'binop', 'add', 'sub', 'div', 'mult', 'mod', 'pow', 'floordiv',  # Binary arithmetic operators
        'compare', 'eq', 'noteq', 'gt', 'lt', 'gte', 'lte',  # Comparison operators
        'bitand', 'bitor', 'bitxor', 'invert', 'lshift', 'rshift',  # Bitwise operators
        'boolop', 'and', 'or', 'not',  # Logical operators
        'in', 'notin',  # Membership operators
        'is', 'isnot',  # Identity operators
        'ifexp',  # Inline if statement
        'subscript', 'index', 'slice', 'extslice',  # Subscripting
        'listcomp', 'setcomp', 'dictcomp',  'generatorexp', 'comprehension',  # Comprehensions
        'attribute',  # Attribute access
    )

    allowed_objects = (
        str, unicode,  # strings
        int, float, long, complex,  # numbers
        list, dict, set, tuple,  # sequences
        type(None), bool  # others
    )

    def check(self, expression):
        if not isinstance(expression, six.string_types):
            raise InvalidExpression('Python expressions must be defined as strings')
        if not expression:
            raise InvalidExpression('Empty python expression')

        try:
            tree = ast.parse(expression)
        except SyntaxError as e:
            raise e

        if len(tree.body) is 0:
            raise InvalidExpression('Empty python expression')
        elif len(tree.body) > 1:
            raise InvalidExpression('Python expressions must be a single line expression')

        start_node = tree.body[0]
        if not isinstance(start_node, ast.Expr):
            raise InvalidExpression("Python string must be an expression: '%s' found" % start_node.__class__.__name__)

        self._check_node(start_node)

    def _check_node(self, node):
        if isinstance(node, list):
            for x in node:
                self._check_node(x)
        elif isinstance(node, ast.AST):
            if not node.__class__.__name__.lower() in self.ast_allowed_nodes:
                self._raise_not_allowed_node(node)
            for field in [f for _, f in ast.iter_fields(node)]:
                self._check_node(field)
        else:
            if not isinstance(node, self.allowed_objects):
                self._raise_not_allowed_node(node)

    def _raise_not_allowed_node(self, node):
        raise InvalidExpression("'%s' definition not allowed in python expressions" % node.__class__.__name__)
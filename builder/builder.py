from typing import Self, List, Literal


class SelectField:
    def __init__(self, expression: str, alias: str | None = None) -> None:
        self.expression = expression
        self.alias = alias

    def __str__(self) -> str:
        if self.alias:
            return f'{self.expression} AS {self.alias}'
        return self.expression


class WhereExpression:
    def __init__(
        self,
        left_expr: str | Self,
        right_expr : str | Self | None = None,
        op: Literal['AND', 'OR'] | None = None
    ) -> None:

        if op and op not in ('AND', 'OR'):
            raise Exception(
                "Attribute `op` of class `WhereExpression` must be either 'AND' or 'OR', "
                f"not '{op}'"
            )

        self.__lexpr = left_expr
        self.__rexpr = right_expr
        self.__op = op

    def bracket(self) -> str:
        return f'({self})'

    def __and__(self, other: Self | None) -> Self:
        if other is None:
            return self
        if self.__op is None and self.__rexpr is None:
            self.__rexpr = other
            self.__op = 'AND'
            return self
        return WhereExpression(self, other, 'AND')

    def __or__(self, other: Self | None) -> Self:
        if other is None:
            return self
        if self.__op is None and self.__rexpr is None:
            self.__rexpr = other
            self.__op = 'OR'
            return self
        return WhereExpression(self, other, 'OR')

    def __str__(self) -> str:
        if self.__op is None and self.__rexpr is None:
            return f'{self.__lexpr}'
        return f'{self.__lexpr} {self.__op} {self.__rexpr}'


class SQLQueryBuilder:
    __is_subquery: bool = False

    __select_fields: List[SelectField]
    __from: str
    __where: WhereExpression
    __group_by: str | None = None
    __order_by: str | None = None

    def add_select(self, *fields: SelectField) -> Self:
        self.__select_fields = fields
        return self

    def add_from(self, table: str | Self) -> Self:
        if isinstance(table, self.__class__):
            self.__from = f'({table.build()})'
        elif isinstance(table, str):
            self.__from = table
        else:
            raise Exception(
                'Argument `table` of method `add_from()` must be of type '
                f'`str` or `SQLBuilder`, not `{type(table)}`.'
            )
        return self

    def add_where(self, expr: WhereExpression) -> Self:
        self.__where = expr
        return self

    def add_group_by(self, group_by_expr: str) -> Self:
        self.__group_by = group_by_expr
        return self

    def add_order_by(self, order_by_expr: str) -> Self:
        self.__order_by = order_by_expr
        return self

    def build(self) -> str:
        parts = []
        parts.append(f"SELECT {', '.join(map(str, self.__select_fields))}")
        parts.append(f'FROM {self.__from}')
        parts.append(f'WHERE {self.__where}')

        if self.__group_by:
            parts.append(f'GROUP BY {self.__group_by}')

        if self.__order_by:
            parts.append(f'ORDER BY {self.__order_by}')

        if self.__is_subquery:
            query = '(' + ' '.join(parts) + ')'
        else:
            query = '\n'.join(parts)

        return query

    # helper methods
    @classmethod
    def subquery(cls) -> Self:
        new = cls()
        new._SQLQueryBuilder__is_subquery = True
        return new

    @staticmethod
    def select_field(expression: str, alias: str | None = None) -> SelectField:
        return SelectField(expression, alias)

    @staticmethod
    def where_expr(expression: str) -> WhereExpression:
        return WhereExpression(expression)

    @staticmethod
    def where_expr_if(cond: bool, exprt: str, exprf: str | None = None) -> WhereExpression:
        if cond:
            return WhereExpression(exprt)
        if exprf is None:
            return None
        return WhereExpression(exprf)

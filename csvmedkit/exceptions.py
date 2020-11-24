from csvkit.exceptions import (
    ColumnIdentifierError,
    CustomException,
    RequiredHeaderError,
)
from agate import DataTypeError


class ArgumentErrorTK(CustomException):
    """
    Exception raised when the user supplies an invalid column identifier.
    """

    pass


class InvalidAggregateName(CustomException):
    """
    this is used when a name for an aggregation isn't found in aggy.Aggregates
    """

    pass


class MissingAggregationArgument(CustomException):
    """
    this is used when user passed in an aggregation function name (e.g. sum, mean) but not the required
    column name argument. This is the case for every aggregate function other than `count`
    """

    pass


class InvalidRange(CustomException):
    pass


class IncorrectlyFormattedString(CustomException):
    pass


class ImplementationError(CustomException):
    pass


class ColumnNameError(CustomException):
    """ different than ColumnIdentifierError in that it only refers to column names"""

    pass

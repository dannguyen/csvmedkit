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


class InvalidAggregationArgument(CustomException):
    """
    this is used when there is a failure in an agate.Aggregation, e.g. a reference to
      a non-existent column in an agate.Table
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

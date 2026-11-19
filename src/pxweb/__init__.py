"""Python client for the PxWeb API v1."""

from .client import PxWebClient
from .errors import APIError, PxWebError, QueryError
from .jsonstat import to_records
from .models import ServerLimits, TableInfo, TableMetadata, Variable
from .query import Selection, fold

__all__ = [
    "APIError",
    "PxWebClient",
    "PxWebError",
    "QueryError",
    "Selection",
    "ServerLimits",
    "TableInfo",
    "TableMetadata",
    "Variable",
    "fold",
    "to_records",
]
__version__ = "0.1.0"

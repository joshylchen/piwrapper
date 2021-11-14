from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

class BufferOption(Enum):
    """
    Enumeration for buffer option type documented here:
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/buffer-option.html
    """

    DO_NO_BUFFER = "DoNotBuffer"
    BUFFER_IF_POSSIBLE = "BufferIdPossible"
    BUFFER = "Buffer"

class UpdateOption(Enum):
    """
    Enumeration for Update Option as documented here:
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/update-option.html
    """

    REPLACE = "Replace"
    INSERT = "Insert"
    NO_REPLACE = "NoReplace"
    REPLACE_ONLY = "ReplaceOnly"
    INSERT_NO_COMPRESSION = "InsertNoCompression"
    REMOVE = "Remove"

class SummaryType(Enum):
    """
    Enumeration for summary type documented here:
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/summary-type.html
    """

    TOTAL = "Total"
    AVERAGE = "Average"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    RANGE = "Range"
    STD_DEV = "StdDev"
    POPULATION_STD_DEV = "PopulationStdDev"
    COUNT = "Count"
    PERCENT_GOOD = "PercentGood"
    ALL = "All"
    ALL_FOR_NON_NUMERIC = "AllForNonNumeric"


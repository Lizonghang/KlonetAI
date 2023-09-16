from transformers import Tool
import datetime


class GetCurrentDateTimeTool(Tool):
    name = "get_current_datetime"
    description = ('''
    Get the current date and time.

    Args:
        None

    Returns:
        str: A string representing the current date and time in the 
            "YYYY-MM-DD HH:MM:SS" format.

    Example:
        >>> time = get_current_datetime()
        >>> print(time)
    ''')

    outputs = ["str"]

    def __call__(self):
        date_obj = datetime.datetime.now()
        date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        return date_str


class GetCurrentDayTool(Tool):
    name = "get_current_day"
    description = ('''
    Get the current day of week.

    Args:
        None

    Returns:
        str: A string representing the day of the week.

    Example:
        >>> day = get_current_day()
        >>> print(day)
    ''')

    outputs = ["str"]

    def __call__(self):
        date_obj = datetime.datetime.now()
        day_str = date_obj.strftime("%A")
        return day_str

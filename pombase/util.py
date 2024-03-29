from __future__ import annotations
import re
from typing import Callable, TypeVar, Any, Sequence, Mapping, MutableMapping, Iterable, Optional
from datetime import datetime, date as dt_date, time as dt_time
from time import time as t_time, sleep
from unicodedata import normalize
from string import Formatter
from dateutil.parser import parserinfo, parse
from seleniumbase.config.settings import LARGE_TIMEOUT

from . import types as pb_types

T = TypeVar('T')


def wait_until(f: Callable[..., T],
               args: list = None,
               kwargs: dict = None,
               timeout: Optional[pb_types.NumberType] = None,
               step: pb_types.NumberType = 0.5,
               expected: Any = True,
               equals: bool = True,
               raise_error: str = None, ) -> (bool, T):
    """
    Waits until Callable `f` returns the `expected` value
    (or something different from the expected value if `equals` is False).

    If you want to check an object property instead of a method, you can use a `lambda` function.

    :param f: The Callable object (usually function or method)
    :param args: List of positional arguments passed to f. Default: []
    :param kwargs: Dictionary of keyword arguments passed to f. Default: {}
    :param timeout: Timeout in seconds
    :param step: Wait time between each check
    :param expected: Expected value
    :param equals: If True, wait until f(*args, **kwargs) == expected.
                   If False, wait until f(*args, **kwargs) != expected.
    :param raise_error: If not None, raises an Error if timeout is reached
    :return: Tuple(success, value). success is True if the waiting succeeded,
             and value is the last value returned by f(*args, **kwargs)
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    if timeout is None:
        timeout = LARGE_TIMEOUT

    if timeout < 0:
        raise RuntimeError(f"timeout should be >= 0. timeout = {timeout}")
    if step <= 0:
        raise RuntimeError(f"step should be > 0. step = {step}")

    if equals is True:
        default_value = None if expected is not None else False
    else:
        default_value = expected

    current = t_time()
    start = current
    stop = start + timeout

    value = default_value
    # noinspection PyBroadException,TryExceptPass
    try:
        value = f(*args, **kwargs)
    except Exception:
        pass

    keep_looping = True
    while keep_looping:
        if (value == expected) is equals:
            return True, value
        after = t_time()
        if after < current + step:
            sleep(current + step - after)
        current = t_time()
        if current <= stop:
            # noinspection PyBroadException,TryExceptPass
            try:
                value = f(*args, **kwargs)
            except Exception:
                pass
        else:
            keep_looping = False
    else:
        if raise_error is not None:
            raise TimeoutError(
                f"{raise_error}. f='{f}', args='{args}', kwargs='{kwargs}', timeout='{timeout}', step='{step}', "
                f"expected='{expected}', equals='{equals}', last value={value}",
            )
        else:
            return False, value


class ParserInfoEs(parserinfo):
    HMS = [('h', 'hour', 'hours', 'hora', 'horas'),
           ('m', 'minute', 'minutes', 'minuto', 'minutos'),
           ('s', 'second', 'seconds', 'segundo', 'segundos')]

    JUMP = [' ', '.', ',', ';', '-', '/', "'", 'at', 'on', 'and', 'ad', 'm', 't', 'of', 'st', 'nd', 'rd', 'th',
            'a', 'en', 'y', 'de']

    MONTHS = [('Jan', 'January', 'Ene', 'Enero'),
              ('Feb', 'February', 'Febrero'),
              ('Mar', 'March', 'Marzo'),
              ('Apr', 'April', 'Abr', 'Abril'),
              ('May', 'May', 'Mayo'),
              ('Jun', 'June', 'Junio'),
              ('Jul', 'July', 'Julio'),
              ('Aug', 'August', 'Ago', 'Agosto'),
              ('Sep', 'Sept', 'September', 'Septiembre'),
              ('Oct', 'October', 'Octubre'),
              ('Nov', 'November', 'Noviembre'),
              ('Dec', 'December', 'Dic', 'Diciembre')]

    PERTAIN = ['of', 'de']

    WEEKDAYS = [('Mon', 'Monday', 'L', 'Lun', 'Lunes'),
                ('Tue', 'Tuesday', 'M', 'Mar', 'Martes'),
                ('Wed', 'Wednesday', 'X', 'Mie', 'Mié', 'Mier', 'Miér', 'Miercoles', 'Miércoles'),
                ('Thu', 'Thursday', 'J', 'Jue', 'Jueves'),
                ('Fri', 'Friday', 'V', 'Vie', 'Viernes'),
                ('Sat', 'Saturday', 'S', 'Sab', 'Sáb', 'Sabado', 'Sábado'),
                ('Sun', 'Sunday', 'D', 'Dom', 'Domingo')]

    def __init__(self, dayfirst=True, yearfirst=False):
        super().__init__(dayfirst=dayfirst, yearfirst=yearfirst)


class DateUtil:
    @staticmethod
    def parse_datetime_es(date_str: str) -> datetime:
        parser_info_es = ParserInfoEs()
        return parse(date_str, parser_info_es)

    @staticmethod
    def parse_date_es(date_str: str) -> dt_date:
        return DateUtil.parse_datetime_es(date_str).date()

    @staticmethod
    def parse_time_es(date_str: str) -> dt_time:
        return DateUtil.parse_datetime_es(date_str).time()

    @staticmethod
    def python_format_date(the_date: datetime, python_format_str: str = "{date.day}/{date:%m}/{date.year}") -> str:
        class CustomFormatter(Formatter):
            def get_field(self,
                          field_name: str,
                          args: Sequence[Any],
                          kwargs: Mapping[str, Any]) -> Any:
                if field_name.startswith("date") is False:
                    raise RuntimeError(f"Incorrect python_format_str: {python_format_str}")
                return super().get_field(field_name, args, kwargs)

        formatter = CustomFormatter()
        # noinspection StrFormat
        return formatter.format(python_format_str, date=the_date)


class CaseInsensitiveDict(MutableMapping):
    """A case-insensitive ``dict``-like object.
    Implements all methods and operations of
    ``MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.
    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive::
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True
    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.
    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """

    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for lowerkey, keyval in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


def clean(s: str) -> str:
    s = s.lower()
    s = re.sub('á', 'a', s)
    s = re.sub('é', 'e', s)
    s = re.sub('í', 'i', s)
    s = re.sub('ó', 'o', s)
    s = re.sub('ú', 'u', s)
    s = re.sub('ñ', 'n', s)

    # Invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '_', s)

    # Remove leading characters until we find a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '', s)

    return s


def normalize_caseless(text: str) -> str:
    return normalize("NFKD", text.casefold())


def caseless_equal(left, right) -> bool:
    return normalize_caseless(left) == normalize_caseless(right)


def caseless_text_in_texts(text: str, texts: Iterable[str]) -> bool:
    normalized_set = {normalize_caseless(t) for t in texts}
    normalized_text = normalize_caseless(text)
    return normalized_text in normalized_set


def expand_replacing_spaces_and_underscores(texts: Iterable[str]) -> set[str]:
    expanded = set(texts)
    expanded = expanded.union({t.replace("_", " ") for t in texts})
    expanded = expanded.union({t.replace(" ", "_") for t in texts})
    return expanded


def first_not_none(*args: T) -> Optional[T]:
    for i in args:
        if i is not None:
            return i
    else:
        return None

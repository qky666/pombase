import dateutil.parser
import datetime


class ParserInfoEs(dateutil.parser.parserinfo):
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
    def parse_datetime_es(datestr: str) -> datetime.datetime:
        parserinfo_es = ParserInfoEs()
        return dateutil.parser.parse(datestr, parserinfo_es)

    @staticmethod
    def parse_date_es(datestr: str) -> datetime.date:
        return DateUtil.parse_datetime_es(datestr).date()

    @staticmethod
    def parse_time_es(datestr: str) -> datetime.time:
        return DateUtil.parse_datetime_es(datestr).time()

    @staticmethod
    def python_format_date(date: datetime.datetime, python_format_str: str = "{date.day}/{date:%m}/{date.year}") -> str:
        return python_format_str.format(date=date)

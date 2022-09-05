# Ошибки

class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ParserFindStatusException(Exception):
    """Вызывается, когда парсер не может найти статус в общей таблице."""
    pass

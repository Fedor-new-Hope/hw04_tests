from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_dateTime = datetime.now()
    return {'year': current_dateTime.year}

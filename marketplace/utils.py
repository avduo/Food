from datetime import datetime, timedelta
from datetime import datetime

from vendor.models import OpeningHours

def get_current_opening_slots(vendor):
    now       = datetime.now()
    today     = now.isoweekday()
    yesterday = 7 if today == 1 else today - 1

    def parse_time(t_str):
        return datetime.strptime(t_str, "%I:%M %p").time()

    today_slots     = OpeningHours.objects.filter(vendor=vendor, day=today, is_closed=False)
    yesterday_slots = OpeningHours.objects.filter(vendor=vendor, day=yesterday, is_closed=False)

    current = []
    # today’s slots (with overnight)
    for slot in today_slots:
        o, c = parse_time(slot.opening_time), parse_time(slot.closing_time)
        open_dt  = datetime.combine(now.date(), o)
        close_dt = datetime.combine(now.date(), c)
        if close_dt <= open_dt:
            close_dt += timedelta(days=1)
        if open_dt <= now < close_dt:
            current.append(slot)

    # yesterday’s after-midnight piece
    for slot in yesterday_slots:
        o, c = parse_time(slot.opening_time), parse_time(slot.closing_time)
        if c <= o:
            open_dt  = datetime.combine(now.date() - timedelta(days=1), o)
            close_dt = datetime.combine(now.date(), c)
            if open_dt <= now < close_dt:
                current.append(slot)

    return current

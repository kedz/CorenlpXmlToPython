import re
from collections import defaultdict

def make_timex(tid, type, val):
    if type == 'DATE':
        date_props = parse_date_str(val)
        if not date_props:
            import sys
            sys.stderr.write('Warning: Could not parse date string ' \
                             '{} -- for tid:{} {}\n'.format(val, tid, type))
            sys.stderr.flush()

        else:
            return Date(tid,
                        date_props['year'],
                        date_props['month'],
                        date_props['day'],
                        date_props['interval'])
    elif type == 'TIME':
        time_props = parse_time_str(val)
        if not time_props:
            import sys
            sys.stderr.write('Warning: Could not parse time string ' \
                             '{} -- for tid:{} {}\n'.format(val, tid, type))
            sys.stderr.flush()

        else:
            return Time(tid,
                        year=time_props['year'],
                        month=time_props['month'],
                        day=time_props['day'],
                        hour=time_props['hour'],
                        minute=time_props['minute'],
                        second=time_props['second'],
                        interval=time_props['interval'])
   
    else:
        import sys
        sys.stderr.write('Warning: Could not parse timex string ' \
                         '{} -- for tid:{} {}\n'.format(val, tid, type))
        sys.stderr.flush()


def parse_date_str(date_str):
    m = re.match(r'(....)|(....)-(..)|(....)-(..)-(..)', str(date_str))
    if m:
        datum = defaultdict(lambda: None)
        datum['year'] = m.group(0) if m.group(0) != 'XXXX' else None
        datum['month'] = m.group(1) if m.group(1) != 'XX' else None
        datum['day'] = m.group(2) if m.group(2) != 'XX' else None
        datum['interval'] = m.group(3)
        return datum
    else:
        return None

def parse_time_str(time_str):
    m = re.match(r'T(\d\d):(\d\d)|()()()T(MO|AF|EV|NI)', time_str)
    if m:
        datum = defaultdict(lambda: None)
        datum['hour'] = m.group(0) if m.group(0) != 'XXXX' else None
        datum['minute'] = m.group(1) if m.group(1) != 'XX' else None
        datum['second'] = m.group(2) if m.group(2) != 'XX' else None
        datum['interval'] = m.group(3)
        return datum
    
    m = re.match(r'(....)-(..)-(..)T(MO|AF|EV|NI)', time_str)
    if m:
        datum = defaultdict(lambda: None)
        datum['year'] = m.group(0) if m.group(0) != 'XXXX' else None
        datum['month'] = m.group(1) if m.group(1) != 'XX' else None
        datum['day'] = m.group(2) if m.group(2) != 'XX' else None
        datum['interval'] = m.group(3)
        return datum

    m = re.match(r'(....)-(..)-(..)T(..):(..)', time_str)
    if m:
        datum = defaultdict(lambda: None)
        datum['year'] = m.group(0) if m.group(0) != 'XXXX' else None
        datum['month'] = m.group(1) if m.group(1) != 'XX' else None
        datum['day'] = m.group(2) if m.group(2) != 'XX' else None
        datum['hour'] = m.group(3)
        datum['minute'] = m.group(4)
        return datum
    
    return None

class Date:
    def __init__(self, tid, year, month, day, interval=None):
        self.tid = tid
        self.year = year
        self.month = month
        self.day = day
        self.interval = interval

class Time:
    def __init__(self, tid, year=None, month=None, day=None, hour=None, minute=None, second=None, interval=None):
        self.tid = tid
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        interval = interval


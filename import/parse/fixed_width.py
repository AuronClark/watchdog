"""
Library for processing fixed-width files.
"""

## Types used in definitions

def date(s):
    """where `s` is YYYYMMDD"""
    return s[0:4] + '-' + s[4:6] + '-' + s[6:8]

def year(s):
    return '20' + s

def string(s):
    return s.strip()

def boolean(s):
    return {'Y': True, 'N': False, ' ': None}[s]
    
filler = string

def enum(s=None, **db):
    if isinstance(s, basestring):
        return string(s)
    else:
        if ' ' not in db: db[' '] = None
        return lambda s: db[s]

def table_lookup(table, preProcess=None):
    def get_from_table(d):
        if preProcess:
            d=preProcess(d)
        if d in table:
            return table[d]
        else:
            return string(d)
    return get_from_table

def integer(s):
    s = s.strip()
    if s:
        try:
            return int(s)
        except ValueError:
            return s
    else: return None

## Format of the definitions

FIELD_KEY = 0
FIELD_LEN = 1
FIELD_TYP = 2

## The functions you might want to call

def parse_line(linedef, line):
    out = {}
    n = 0
    for (k, l, t) in linedef:
        if l < 0 : # go back
            out[k] = t(line[n+l:n])
        if k is not None:
            out[k] = t(line[n:n+l])
        if l > 0: n += l
    return out

def get_len(filedef):
    if isinstance(filedef, dict):
        linelen = set(sum(line[FIELD_LEN] for line in kind) for kind in filedef.itervalues())
        assert len(linelen) == 1, [(kind_name, sum(line[FIELD_LEN] for line in kind)) for kind_name, kind in filedef.iteritems()]
        linelen = list(linelen)[0]
        return linelen
    else:
        return sum(line[FIELD_LEN] for line in filedef)

def parse_file(filedef, fh, f_whichdef=None):
    linelen = get_len(filedef)
    if isinstance(filedef, dict):
        if not f_whichdef: f_whichdef = lambda x: x[0]
    else:
        f_whichdef = lambda x: slice(None, None)
    for line in iter(lambda: fh.read(linelen), ''):
        yield parse_line(filedef[f_whichdef(line)], line)
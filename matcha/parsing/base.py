import re
import logging
from functools import partial

log = logging.getLogger(__name__)

class ParsingException(Exception):
    def __init__(self, expected, parser, rest):
        self.expected = expected
        self.parser = parser
        self.rest = rest

def p_match(s, text):
    if text.startswith(s):
        return s, text[len(s):]
    return None

def p_regex(regex):
    def regex_parser(text):
        m = re.compile(regex).match(text)
        if m:
            g = m.group()
            return g, text[len(g):]

        return None

    return regex_parser

def match(s):
    return partial(p_match, s)

def then_parser(spec, match_all, text):
    names = spec[::2]
    parsers = spec[1::2]
    t = text
    out = {}
    for i in range(len(names)):
        p = parsers[i]
        n = names[i]
        r = p(t)
        if r == None:
            if match_all:
                raise ParsingException(n, p, t)

            return None

        if n == '<':
            out.update(r[0])
        elif n != '_':
            out[n] = r[0]

        t = r[1]

    return out, t

def then(*spec):
    return partial(then_parser, spec, False)

def then_all(*spec):
    return partial(then_parser, spec, True)

def many(p):
    def many_parser(text):
        out = []
        r = p(text)
        while r:
            out.append(r[0])
            text = r[1]
            r = p(text)

        if out:
            return out, text
        return None

    return many_parser

def either(*parsers):
    def either_parser(text):
        for p in parsers:
            r = p(text)
            if r:
                return r

        return None

    return either_parser

def oneof(options):
    return either(*map(match, options))

def wrapped(pre, p, post):
    spec = ['inner', p]
    if pre:
        spec = ['_', pre] + spec
    if post:
        spec = spec + ['_', post]

    t = then(*spec)

    def wrapped_parser(text):
        r = t(text)
        if r:
            return r[0]['inner'], r[1]
        return None

    return wrapped_parser

def rstrip(p):
    return wrapped(None, p, p_regex('\\s*'))

def strip(p):
    return wrapped(p_regex('\\s*'), p, p_regex('\\s*'))

def joined(by, part):
    def joined_parser(text):
        out = []
        r = part(text)
        expect = by
        while r:
            out.append(r[0])
            text = r[1]
            r = expect(text)
            if not r:
                break

            expect = part if expect == by else by

        if out:
            if expect == part:
                return out[:-1], text
            return out, text
        return None

    return joined_parser

def joined_skip(by, part, empty_valid=True):
    def joined_skip_parser(text):
        r = joined(by, part)(text)
        if r:
            return r[0][::2], r[1]

        if empty_valid:
            return [], text
        return None
    return joined_skip_parser

def flat(p):
    def flat_parser(text):
        r = p(text)
        if r:
            return ''.join(r[0]), r[1]
        return None

    return flat_parser




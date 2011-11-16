import re
import unicodedata



def force_unicode(value, encoding='utf-8', errors='strict'):
    """
    Force a value to be unicode.

    If the value is a bytestring, it will call decode using
    the given encoding and errors strategy.  If it has a
    __unicode__ method, it will call that, otherwise it will
    call str() on the value and then convert that to unicode.

    Inspired by Django's force_unicode.
    """
    if isinstance(value, unicode):
        u = value
    elif isinstance(value, basestring):
        u = value.decode(encoding, errors)
    else:
        if hasattr(value, '__unicode__'):
            u = unicode(value)
        else:
            u = unicode(str(value), encoding, errors)
    return u


SLUGIFY_STRIP_RE = re.compile(r'[^\w\s-]')
SLUGIFY_HYPHENATE_RE = re.compile(r'[-\s]+')


def slugify(value, limit=None):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Can be limited to a certain length.
    
    Inspired by Django's slugify function.
    """
    if not value:
        return u''

    if not isinstance(value, unicode):
        value = force_unicode(value)

    # remove all non-ascii characters, recoding as ascii
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')

    # remove all non-word, non-space characters, and strip and lowercase,
    # decoding back into unicode
    value = SLUGIFY_STRIP_RE.sub('', value)
    if limit:
        value = value[:limit]
    value = SLUGIFY_HYPHENATE_RE.sub('-', value.strip().lower())
    return unicode(value)

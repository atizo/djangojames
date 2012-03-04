# -*- coding: utf-8 -*-
#
# Atizo - The Open Innovation Platform
# http://www.atizo.com/
#
# Copyright (c) 2008-2010 Atizo AG. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from django.utils.translation import ugettext as _
import re
import sys
import unicodedata
from django.utils.encoding import force_unicode
   
def humanize_bool(a_bool):
    if a_bool:
        return _(u'Ja')
    else:
        return _(u'Nein')

def strip_empty_tags(value):
    return re.sub(r"""(?im)<(?!\s*/)\s*[^>]*?>\s*<s*/\s*[^>]*?>""", '', force_unicode(value))
    
def strip_tags(value, taglist):
    tags = '|'.join(taglist)
    return re.sub(r'<\s*(%(tags)s)\s*[^>]*?>|<\s*/\s*(%(tags)s)\s*[^>]*?>' % {'tags':tags}, '', force_unicode(value))

CHAR_REPLACEMENT = {
    # latin-1 characters that don't have a unicode decomposition
    0xc6: u"AE", # LATIN CAPITAL LETTER AE
    0xd0: u"D",  # LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # LATIN CAPITAL LETTER THORN
    0xdf: u"ss", # LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # LATIN SMALL LETTER AE
    0xf0: u"d",  # LATIN SMALL LETTER ETH
    0xf8: u"oe", # LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # LATIN SMALL LETTER THORN
}

class unaccented_map(dict):
    """
    Translation dictionary. Translation entries are added to this dictionary as needed
    """
    
    def mapchar(self, key):
        """
        Maps a unicode character code (the key) to a replacement code (either a character code or a unicode string).
        """
        ch = self.get(key)
        if ch is not None:
            return ch
        de = unicodedata.decomposition(unichr(key))
        if de:
            try:
                ch = int(de.split(None, 1)[0], 16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = CHAR_REPLACEMENT.get(key, key)
        self[key] = ch
        return ch

    if sys.version >= "2.5":
        # use __missing__ where available
        __missing__ = mapchar
    else:
        # otherwise, use standard __getitem__ hook (this is slower,
        # since it's called for each character)
        __getitem__ = mapchar
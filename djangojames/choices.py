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

from djangojames.string import unaccented_map
from copy import copy
from django.utils.translation import ugettext_lazy as _

SELECTION_NAME = _(u'- Bitte wählen -')
NO_SELECTION = _(u'- Keine Auswahl -')

def sort_choice(choice, head_tuple=None):
    c = list(copy(choice))
    m = unaccented_map()
    c.sort(key=lambda x: unicode(x[1]).translate(m))
    if head_tuple:
        l = []
        l.extend(c)
        for k in head_tuple:
            l.insert(1,k)
        return l
    return c

def get_display(choice, key):
    for c in choice:
        if c[0] == key:
            return unicode(c[1])
    return ''
    
COUNTRY_CHOICES_HEAD = (
    ('at', _(u'Österreich')),
    ('de', _(u'Deutschland')),
    ('ch', _(u'Schweiz')),
    ('fr', _(u'Frankreich')),
)

COUNTRY_CHOICES = (
    ('', SELECTION_NAME),
    ('ad', _(u'Andorra')),
    ('ae', _(u'Vereinigte Arabische Emirate')),
    ('af', _(u'Afghanistan')),
    ('ag', _(u'Antigua und Barbuda')),
    ('ai', _(u'Anguilla')),
    ('al', _(u'Albanien')),
    ('am', _(u'Armenien')),
    ('an', _(u'Niederländische Antillen')),
    ('ao', _(u'Angola')),
    ('aq', _(u'Antarktis')),
    ('ar', _(u'Argentinien')),
    ('as', _(u'Amerikanisch-Samoa')),
    ('at', _(u'Österreich')),
    ('au', _(u'Australien')),
    ('aw', _(u'Aruba')),
    ('ax', _(u'Ålandinseln')),
    ('az', _(u'Aserbaidschan')),
    ('ba', _(u'Bosnien-Herzegowina')),
    ('bb', _(u'Barbados')),
    ('bd', _(u'Bangladesch')),
    ('be', _(u'Belgien')),
    ('bf', _(u'Burkina Faso')),
    ('bg', _(u'Bulgarien')),
    ('bh', _(u'Bahrain')),
    ('bi', _(u'Burundi')),
    ('bj', _(u'Benin')),
    ('bm', _(u'Bermuda')),
    ('bn', _(u'Brunei')),
    ('bo', _(u'Bolivien')),
    ('br', _(u'Brasilien')),
    ('bs', _(u'Bahamas')),
    ('bt', _(u'Bhutan')),
    ('bv', _(u'Bouvetinsel')),
    ('bw', _(u'Botswana')),
    ('by', _(u'Weißrußland')),
    ('bz', _(u'Belize')),
    ('ca', _(u'Kanada')),
    ('cc', _(u'Kokosinseln')),
    ('cd', _(u'Die Demokratische Republik Kongo')),
    ('cf', _(u'Zentralafrikanische Republik')),
    ('cg', _(u'Kongo')),
    ('ch', _(u'Schweiz')),
    ('ci', _(u'Côte d\'Ivoire')),
    ('ck', _(u'Cook-Inseln')),
    ('cl', _(u'Chile')),
    ('cm', _(u'Kamerun')),
    ('cn', _(u'China')),
    ('co', _(u'Kolumbien')),
    ('cr', _(u'Costa Rica')),
    ('cu', _(u'Kuba')),
    ('cv', _(u'Kap Verde')),
    ('cx', _(u'Weihnachtsinsel')),
    ('cy', _(u'Zypern')),
    ('cz', _(u'Tschechische Republik')),
    ('de', _(u'Deutschland')),
    ('dj', _(u'Dschibuti')),
    ('dk', _(u'Dänemark')),
    ('dm', _(u'Dominika')),
    ('do', _(u'Dominikanische Republik')),
    ('dz', _(u'Algerien')),
    ('ec', _(u'Ecuador')),
    ('ee', _(u'Estland')),
    ('eg', _(u'Ägypten')),
    ('eh', _(u'Westsahara')),
    ('er', _(u'Eritrea')),
    ('es', _(u'Spanien')),
    ('et', _(u'Äthiopien')),
    ('fi', _(u'Finnland')),
    ('fj', _(u'Fidschi-Inseln')),
    ('fk', _(u'Falklandinseln (Malwinen)')),
    ('fm', _(u'Mikronesien')),
    ('fo', _(u'Faroer-Inseln')),
    ('ga', _(u'Gabun')),
    ('gb', _(u'Vereinigtes Königreich')),
    ('gd', _(u'Grenada')),
    ('ge', _(u'Georgien')),
    ('gf', _(u'Französisch Guyana')),
    ('gg', _(u'Guernsey')),
    ('gh', _(u'Ghana')),
    ('gi', _(u'Gibraltar')),
    ('gl', _(u'Grönland')),
    ('gm', _(u'Gambia')),
    ('gn', _(u'Guinea')),
    ('gp', _(u'Guadeloupe')),
    ('gq', _(u'Äquatorial-Guinea')),
    ('gr', _(u'Griechenland')),
    ('gs', _(u'Südgeorgien und Südliche Sandwichinseln')),
    ('gt', _(u'Guatemala')),
    ('gu', _(u'Guam')),
    ('gw', _(u'Guinea-Bissau')),
    ('gy', _(u'Guyana')),
    ('hk', _(u'Hongkong')),
    ('hm', _(u'Heard und McDonald-Inseln')),
    ('hn', _(u'Honduras')),
    ('hr', _(u'Kroatien')),
    ('ht', _(u'Haiti')),
    ('hu', _(u'Ungarn')),
    ('id', _(u'Indonesien')),
    ('ie', _(u'Irland')),
    ('il', _(u'Israel')),
    ('im', _(u'Isle of Man')),
    ('in', _(u'Indien')),
    ('io', _(u'Britisches Territorium im Indischen Ozean')),
    ('iq', _(u'Irak')),
    ('ir', _(u'Iran (Islamische Republik )')),
    ('is', _(u'Island')),
    ('it', _(u'Italien')),
    ('je', _(u'Jersey')),
    ('jm', _(u'Jamaika')),
    ('jo', _(u'Jordanien')),
    ('jp', _(u'Japan')),
    ('ke', _(u'Kenia')),
    ('kg', _(u'Kirgistan')),
    ('kh', _(u'Kambodscha')),
    ('ki', _(u'Kiribati')),
    ('km', _(u'Komoren')),
    ('kn', _(u'Saint Christopher/Kitts')),
    ('kp', _(u'Nordkorea')),
    ('kr', _(u'Südkorea')),
    ('kw', _(u'Kuwait')),
    ('ky', _(u'Cayman-Inseln')),
    ('kz', _(u'Kasachstan')),
    ('la', _(u'Laos')),
    ('lb', _(u'Libanon')),
    ('lc', _(u'Karibische Inseln - Saint Lucia')),
    ('li', _(u'Liechtenstein')),
    ('lk', _(u'Sri Lanka')),
    ('lr', _(u'Liberia')),
    ('ls', _(u'Lesotho')),
    ('lt', _(u'Litauen')),
    ('lu', _(u'Luxemburg')),
    ('lv', _(u'Lettland')),
    ('ly', _(u'Libyen')),
    ('ma', _(u'Marokko')),
    ('mc', _(u'Monaco')),
    ('md', _(u'Moldawien')),
    ('me', _(u'Montenegro')),
    ('mg', _(u'Madagaskar')),
    ('mh', _(u'Marschall-Inseln')),
    ('mk', _(u'Mazedonien')),
    ('ml', _(u'Mali')),
    ('mm', _(u'Burma')),
    ('mn', _(u'Mongolei')),
    ('mo', _(u'Macao')),
    ('mp', _(u'Nördliche Marianen-Inseln')),
    ('mq', _(u'Martinique')),
    ('mr', _(u'Mauretanien')),
    ('ms', _(u'Montserrat')),
    ('mt', _(u'Malta')),
    ('mu', _(u'Mauritius')),
    ('mv', _(u'Malediven')),
    ('mw', _(u'Malawi')),
    ('mx', _(u'Mexiko')),
    ('my', _(u'Malaysia')),
    ('mz', _(u'Mosambik')),
    ('na', _(u'Namibia')),
    ('nc', _(u'Neu-Kaledonien')),
    ('ne', _(u'Niger')),
    ('nf', _(u'Norfolk-Inseln')),
    ('ng', _(u'Nigeria')),
    ('ni', _(u'Nicaragua')),
    ('nl', _(u'Niederlande')),
    ('no', _(u'Norwegen')),
    ('np', _(u'Nepal')),
    ('nr', _(u'Nauru')),
    ('nu', _(u'Niue-Inseln')),
    ('nz', _(u'Neuseeland')),
    ('om', _(u'Oman')),
    ('pa', _(u'Panama')),
    ('pe', _(u'Peru')),
    ('pf', _(u'Französisch Polynesien')),
    ('pg', _(u'Papua-Neuguinea')),
    ('ph', _(u'Philippinen')),
    ('pk', _(u'Pakistan')),
    ('pl', _(u'Polen')),
    ('pm', _(u'Saint Pierre et Miquelon')),
    ('pn', _(u'Pitcairn')),
    ('pr', _(u'Puerto Rico')),
    ('ps', _(u'Palästinensisches Gebiet, Besetztes')),
    ('pt', _(u'Portugal')),
    ('pw', _(u'Palau-Inseln')),
    ('py', _(u'Paraguay')),
    ('qa', _(u'Katar')),
    ('re', _(u'Reunion')),
    ('ro', _(u'Rumänien')),
    ('rs', _(u'Serbien')),
    ('ru', _(u'Russische Föderation')),
    ('rw', _(u'Ruanda')),
    ('sa', _(u'Saudiarabien')),
    ('sb', _(u'Salomonen')),
    ('sc', _(u'Seychellen')),
    ('sd', _(u'Sudan')),
    ('se', _(u'Schweden')),
    ('sg', _(u'Singapur')),
    ('sh', _(u'Sankt Helena')),
    ('si', _(u'Slowenien')),
    ('sj', _(u'Svalbard und Jan Mayen-Inseln')),
    ('sk', _(u'Slowakei')),
    ('sl', _(u'Sierra Leone')),
    ('sm', _(u'San Marino')),
    ('sn', _(u'Senegal')),
    ('so', _(u'Somalia')),
    ('sr', _(u'Surinam')),
    ('st', _(u'Sao Tome & Principe')),
    ('sv', _(u'El Salvador')),
    ('sy', _(u'Syrien')),
    ('sz', _(u'Swasiland')),
    ('tc', _(u'Turks- und Caicos Inseln')),
    ('td', _(u'Tschad')),
    ('tf', _(u'Französische Gebiete im südlichen Indischen Ozean')),
    ('tg', _(u'Togo')),
    ('th', _(u'Thailand')),
    ('tj', _(u'Tadschikistan')),
    ('tk', _(u'Tokelau')),
    ('tl', _(u'Ost-Timor')),
    ('tm', _(u'Turkmenistan')),
    ('tn', _(u'Tunesien')),
    ('to', _(u'Tonga')),
    ('tr', _(u'Türkei')),
    ('tt', _(u'Trinidad und Tobago')),
    ('tv', _(u'Tuvalu')),
    ('tw', _(u'Taiwan')),
    ('tz', _(u'Tansania')),
    ('ua', _(u'Ukraine')),
    ('ug', _(u'Uganda')),
    ('um', _(u'United States Minor Outlying Islands')),
    ('us', _(u'Vereinigte Staaten')),
    ('uy', _(u'Uruguay')),
    ('uz', _(u'Usbekistan')),
    ('va', _(u'Vatikanstadt')),
    ('vc', _(u'Saint Vincent u. Grenadien')),
    ('ve', _(u'Venezuela')),
    ('vg', _(u'Jungfern-Inseln (UK)')),
    ('vi', _(u'Jungfern-Inseln (USA)')),
    ('vn', _(u'Vietnam')),
    ('vu', _(u'Vanuatu')),
    ('wf', _(u'Wallis und Futuna')),
    ('ws', _(u'Samoa-Inseln')),
    ('ye', _(u'Jemen')),
    ('yt', _(u'Mayotte')),
    ('za', _(u'Südafrika')),
    ('zm', _(u'Zambia')),
    ('zw', _(u'Zimbabwe')),
)

LANGUAGE_CHOICES_HEAD = (
    ('fr', _(u'Französisch')),
    ('en', _(u'Englisch')),
    ('de', _(u'Deutsch')),
)

LANGUAGE_CHOICES = (
    ('', SELECTION_NAME),
    ('ar', _(u'Arabisch')),
    ('cs', _(u'Tschechisch')),
    ('da', _(u'Dänisch')),
    ('de', _(u'Deutsch')),
    ('el', _(u'Griechisch')),
    ('en', _(u'Englisch')),
    ('es', _(u'Spanisch')),
    ('fi', _(u'Finnisch')),
    ('fr', _(u'Französisch')),
    ('he', _(u'Hebräisch')),
    ('hu', _(u'Ungarisch')),
    ('it', _(u'Italienisch')),
    ('ja', _(u'Japanisch')),
    ('ko', _(u'Koreanisch')),
    ('nl', _(u'Niederländisch')),
    ('no', _(u'Norwegisch')),
    ('pl', _(u'Polnisch')),
    ('pt', _(u'Portugiesisch')),
    ('ro', _(u'Rumänisch')),
    ('ru', _(u'Russisch')),
    ('sv', _(u'Schwedisch')),
    ('tr', _(u'Türkisch')),
    ('zh', _(u'Chinesisch')),
)
# -*- coding: utf-8 -*-
#
# Copyright 2008, 2011 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

# Original Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

"""A class to manage Mozilla .lang files.

See https://github.com/mozilla-l10n/langchecker/wiki/.lang-files-format for
specifications on the format.
"""

import six

from translate.storage import base, txt


@six.python_2_unicode_compatible
class LangUnit(base.TranslationUnit):
    """This is just a normal unit with a weird string output"""

    def __init__(self, source=None):
        self.locations = []
        base.TranslationUnit.__init__(self, source)

    def __str__(self):
        if self.source == self.target:
            unchanged = " {ok}"
        else:
            unchanged = ""
        if not self.istranslated():
            target = self.source
        else:
            target = self.target
        if self.getnotes():
            notes = ('\n').join(
                [("#%s" % note
                  if note.startswith("#")
                  else "# %s" % note)
                 for note
                 in self.getnotes('developer').split("\n")])
            return u"%s\n;%s\n%s%s" % (notes, self.source, target, unchanged)
        return u";%s\n%s%s" % (self.source, target, unchanged)

    def getlocations(self):
        return self.locations

    def addlocation(self, location):
        self.locations.append(location)


class LangStore(txt.TxtFile):
    """We extend TxtFile, since that has a lot of useful stuff for encoding"""

    UnitClass = LangUnit

    Name = "Mozilla .lang"
    Extensions = ['lang']

    def __init__(self, inputfile=None, mark_active=False, **kwargs):
        self.is_active = False
        self.mark_active = mark_active
        self._headers = []
        super(LangStore, self).__init__(inputfile, **kwargs)

    def parse(self, lines):
        source_unit = None
        comment = ""
        if not isinstance(lines, list):
            lines = lines.split(b"\n")

        for lineoffset, line in enumerate(lines):
            line = line.decode(self.encoding).rstrip("\n").rstrip("\r")

            if lineoffset == 0 and line == "## active ##":
                self.is_active = True
                continue

            if line.startswith("## ") and not line.startswith('## TAG'):
                self._headers.append(line)
                continue

            if len(line) == 0 and not source_unit:  # Skip blank lines
                continue

            if source_unit:
                # If we have a source_unit get the target
                if line != source_unit.source:
                    if line.rstrip().endswith("{ok}"):
                        source_unit.target = line.rstrip()[:-4].rstrip()
                    else:
                        source_unit.target = line
                else:
                    source_unit.target = ""
                source_unit = None
                continue

            is_comment = (
                line.startswith('#')
                and (not line.startswith("##")
                     or line.startswith('## TAG')))
            if is_comment:
                # Read comments, *including* meta tags (i.e. '## TAG')
                comment += line[1:].strip() + "\n"

            if line.startswith(';'):
                source_unit = self.addsourceunit(line[1:])
                source_unit.addlocation(
                    "%s:%d" % (self.filename, lineoffset + 1))
                if comment is not None:
                    source_unit.addnote(comment[:-1], 'developer')
                    comment = ""

    def serialize(self, out):
        if self.is_active or self.mark_active:
            out.write(b"## active ##\n")
        for header in self._headers:
            out.write(six.text_type("%s\n" % header).encode('utf-8'))
        if self._headers:
            out.write(b"\n\n")
        for unit in self.units:
            out.write(six.text_type(unit).encode('utf-8'))
            out.write(b"\n\n\n")

    def getlangheaders(self):
        return self._headers

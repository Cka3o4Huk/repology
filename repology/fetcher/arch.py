# Copyright (C) 2016 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import shutil

class ArchDBFetcher():
    def __init__(self, *sources):
        self.sources = sources

    def Fetch(self, statepath, update = True, verbose = False):
        if os.path.isdir(statepath) and not update:
            return

        if os.path.isdir(statepath):
            shutil.rmtree(statepath)

        os.mkdir(statepath)

        quietflag = 'q' if not verbose else ''

        for source in self.sources:
            subprocess.check_call("wget -%sO- %s | tar -xz -f- -C %s" % (quietflag, source, statepath), shell = True)

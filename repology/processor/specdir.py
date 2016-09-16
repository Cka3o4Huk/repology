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
from pkg_resources import parse_version

from .common import RepositoryProcessor
from ..util import VersionCompare
from ..package import Package

import sys

class GenericSpecDirectoryProcessor(RepositoryProcessor):
    def __init__(self, path, type):
        self.path = path
        self.type = type

    def GetRepoType(self):
        return self.type

    def IsUpToDate(self):
        return False

    def Download(self, update = True):
        pass

    def Parse(self):
        result = []

        for root, dirs, files in os.walk(self.path):
            for file in files:
                if not file.endswith(".spec"):
                    continue

                with open(os.path.join(root, file), encoding='utf-8', errors='ignore') as file:
                    pkg = Package()

                    for line in file:
                        line = line[:-1]

                        if line.find("%") != -1: # substitudes: ignore
                            continue

                        if line.startswith('Name: '):
                            pkg.name = line[6:].strip()
                        elif line.startswith('Version: '):
                            pkg.fullversion = line[9:].strip()
                            pkg.version = pkg.fullversion
                        elif line.startswith('Url: '):
                            pkg.homepage = line[5:].strip()
                        elif line.startswith('License: '):
                            pkg.license = line[9:].strip()
                        elif line.startswith('Group: '):
                            pkg.category = line[7:].strip().lower()
                        elif line.startswith('Summary: '):
                            pkg.comment = line[9:].strip()

                    if pkg.name is not None and pkg.version is not None:
                        result.append(pkg)

        return result

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
import re
from pkg_resources import parse_version

from .common import RepositoryProcessor
from ..util import VersionCompare
from ..package import Package

def SanitizeVersion(version):
    pos = version.find('-')
    if pos != -1:
        version = version[0:pos]

    pos = version.find(':')
    if pos != -1:
        version = version[pos+1:]

    return version

class ArchDBProcessor(RepositoryProcessor):
    def __init__(self, path, *sources):
        self.path = path
        self.sources = sources

    def GetRepoType(self):
        return 'arch'

    def IsUpToDate(self):
        return False

    def Download(self, update = True):
        if os.path.isdir(self.path) and update:
            shutil.rmtree(self.path)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
            for source in self.sources:
                subprocess.check_call("wget -qO- %s | tar -xz -f- -C %s" % (source, self.path), shell = True)

    def Parse(self):
        result = []

        for package in os.listdir(self.path):
            desc_path = os.path.join(self.path, package, "desc")
            if not os.path.isfile(desc_path):
                continue

            with open(desc_path, encoding='utf-8') as file:
                pkg = Package()

                tag = None
                for line in file:
                    line = line[:-1]

                    if line == '':
                        tag = None
                    elif tag == 'NAME':
                        pkg.name = line
                    elif tag == 'VERSION':
                        pkg.fullversion = line
                        pkg.version = SanitizeVersion(pkg.fullversion)
                    elif tag == 'DESC':
                        if pkg.comment is None:
                            pkg.comment = ''
                        if pkg.comment != '':
                            pkg.comment += "\n"
                        pkg.comment += line
                    elif tag == 'URL':
                        pkg.homepage = line
                    elif tag == 'LICENSE':
                        if pkg.license is None:
                            pkg.license = []
                        pkg.license.append(line)
                    elif tag == 'PACKAGER':
                        pkg.maintainer = line
                    elif line.startswith('%') and line.endswith('%'):
                        tag = line[1:-1]

                if pkg.name is not None and pkg.version is not None:
                    result.append(pkg)

        return result

class Aur3GitProcessor(RepositoryProcessor):
    def __init__(self, path, *sources):
        self.path = path
        self.sources = sources

    def GetRepoType(self):
        return 'arch'

    def IsUpToDate(self):
        return False

    def Download(self, update = True):
        if not os.path.isdir(self.path):
            subprocess.check_call("git clone -q --depth=1 %s %s" % (self.source, self.path), shell = True)
        # no updates, repo is frozen

    def Parse(self):
        result = []

        for package in os.listdir(self.path):
            if package.endswith("-git"):
                continue

            pkgbuild_path = os.path.join(self.path, package, "PKGBUILD")
            if not os.path.isfile(pkgbuild_path):
                continue

            with open(pkgbuild_path, encoding='utf-8', errors='ignore') as file:
                pkg = Package()

                for line in file:
                    line = line[:-1]

                    if re.search('[$(){}\'"]', line): # XXX: new more clever sh parser
                        continue

                    if line.startswith("pkgname="):
                        pkg.name = line[8:]
                    elif line.startswith("pkgver="):
                        pkg.fullversion = line[7:]
                        pkg.version = pkg.fullversion
                    elif line.startswith("pkgdesc="):
                        pkg.comment = line[8:]

                if pkg.name is not None and pkg.version is not None:
                    result.append(pkg)

        return result

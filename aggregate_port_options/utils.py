# Copyright (C) 2021 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of aggregate-port-options
#
# aggregate-port-options is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aggregate-port-options is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with aggregate-port-options.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import itertools
import os
import subprocess
from typing import Collection, Optional


class UtilityCallError(Exception):
    def __str__(self) -> str:
        assert(self.__cause__)
        assert(isinstance(self.__cause__, subprocess.CalledProcessError))

        command = ' '.join(self.__cause__.cmd)
        code = self.__cause__.returncode
        stderr = self.__cause__.stderr.strip().splitlines()

        if stderr and stderr[0]:
            return f'"{command}" returned {code}: "{stderr[0]}"'
        else:
            return f'"{command}" returned {code}'


class Pkg:
    _binary: str

    def __init__(self, binary: str = '/usr/sbin/pkg') -> None:
        self._binary = binary

    def __call__(self, *args: str) -> list[str]:
        try:
            res = subprocess.run((self._binary,) + args, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise UtilityCallError from e
        return res.stdout.strip().splitlines()


class Ports:
    _binary: str
    _ports_path: str

    def __init__(self, binary: str = '/usr/bin/make', ports_path: str = '/usr/ports') -> None:
        self._binary = binary
        self._ports_path = ports_path

    def _run_make(self, origin: str, *args: str, env: Optional[dict[str, str]]) -> subprocess.CompletedProcess[str]:
        cmd = [self._binary, '-C', os.path.join(self._ports_path, origin)] + list(args)

        try:
            return subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
        except subprocess.CalledProcessError as e:
            raise UtilityCallError from e

    def get_var(self, origin: str, varname: str, env: Optional[dict[str, str]] = None) -> str:
        res = self._run_make(origin, '-V', varname, env=env)
        return res.stdout.strip()

    def get_vars(self, origin: str, varnames: Collection[str], env: Optional[dict[str, str]] = None) -> dict[str, str]:
        res = self._run_make(origin, *itertools.chain.from_iterable(['-V', varname] for varname in varnames), env=env)
        return dict(zip(varnames, res.stdout.strip().splitlines()))

    def get_target(self, origin: str, targetname: str, env: Optional[dict[str, str]] = None) -> list[str]:
        res = self._run_make(origin, targetname, env=env)
        return res.stdout.strip().splitlines()

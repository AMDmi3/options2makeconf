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

from collections import defaultdict
from enum import Enum
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from aggregate_port_options.package_processing import PackageInfo


@dataclass
class _OptionInfoBase:
    packages_on: set[str] = field(default_factory=set)
    packages_off: set[str] = field(default_factory=set)
    packages_default: set[str] = field(default_factory=set)
    packages_default_bad: set[str] = field(default_factory=set)


class OptionStatus(Enum):
    UNCHANGED = 1
    ALWAYS_ENABLED = 2
    ALWAYS_DISABLED = 3
    MIXED = 4


@dataclass
class OptionInfo:
    name: str

    status: OptionStatus

    packages_on: set[str] = field(default_factory=set)
    packages_off: set[str] = field(default_factory=set)
    packages_default: set[str] = field(default_factory=set)
    packages_default_bad: set[str] = field(default_factory=set)

    packages_overridden_on: set[str] = field(default_factory=set)
    packages_overridden_off: set[str] = field(default_factory=set)
    packages_left_on: set[str] = field(default_factory=set)
    packages_left_off: set[str] = field(default_factory=set)


def iterate_options(packages: Iterable[PackageInfo]) -> Iterator[OptionInfo]:
    options: dict[str, _OptionInfoBase] = defaultdict(_OptionInfoBase)

    for package in packages:
        for option, on in package.options.items():
            if on:
                options[option].packages_on.add(package.name)
            else:
                options[option].packages_off.add(package.name)

        for option in package.default_options:
            if option in package.options:
                options[option].packages_default.add(package.name)
            else:
                options[option].packages_default_bad.add(package.name)

    for option, info in sorted(options.items()):
        if info.packages_on == info.packages_default:
            new_info = OptionInfo(option, OptionStatus.UNCHANGED, **info.__dict__)
        elif not info.packages_off:
            new_info = OptionInfo(option, OptionStatus.ALWAYS_ENABLED, **info.__dict__)
        elif not info.packages_on:
            new_info = OptionInfo(option, OptionStatus.ALWAYS_DISABLED, **info.__dict__)
        else:
            new_info = OptionInfo(option, OptionStatus.MIXED, **info.__dict__)
  
        new_info.packages_overridden_on = info.packages_on - info.packages_default
        new_info.packages_overridden_off = info.packages_default - info.packages_on

        new_info.packages_left_on = info.packages_default & info.packages_on
        new_info.packages_left_off = info.packages_off - info.packages_default

        yield new_info

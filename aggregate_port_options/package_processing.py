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

import logging
from dataclasses import dataclass
from typing import Iterator, Optional

from aggregate_port_options.utils import Pkg, Ports, UtilityCallError


@dataclass
class PackageInfo:
    name: str
    origin: str
    flavor: Optional[str]
    options: dict[str, bool]
    default_options: set[str]


def iterate_packages(pkg: Pkg, ports: Ports) -> Iterator[PackageInfo]:
    logging.debug('getting list of packages')

    for line in pkg('query', '%n %o'):
        package_name, origin = line.split(maxsplit=1)

        logging.debug(f'gathering package information for {package_name} ({origin})')

        options = {
            key: value == 'on'
            for key, value in (
                line.split(maxsplit=1)
                for line in pkg('query', '%Ok %Ov', package_name)
            )
        }

        # optionless packages are not interesting to us,
        # skip them early to avoid slow make invocation
        if not options:
            continue

        annotations = {
            key: value
            for key, value in (
                line.split(maxsplit=1)
                for line in pkg('query', '%At %Av', package_name)
            )
        }

        flavor_env = {'FLAVOR': annotations['flavor']} if 'flavor' in annotations else {}

        try:
            default_options = set(ports.get_var(origin, 'OPTIONS_DEFAULT', env=flavor_env).split())
        except UtilityCallError as e:
            logging.error(f'cannot get default options for {package_name} ({origin}) via ports: {e}')
            default_options = {key for key, value in options.items() if value}

        # always enabled by default options
        for option in ['DOCS', 'NLS', 'EXAMPLES', 'IPV6']:
            if option in options:
                default_options.add(option)

        yield PackageInfo(
            name=package_name,
            origin=origin,
            flavor=annotations.get('flavor'),
            options=options,
            default_options=default_options
        )

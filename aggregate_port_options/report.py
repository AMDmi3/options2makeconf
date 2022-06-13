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
from typing import Iterable

from aggregate_port_options.option_processing import OptionInfo, OptionStatus


def _format_package_list(names: Iterable[str]) -> str:
    return ', '.join(sorted(names))


def _format_package_lists(option: OptionInfo, want_enabled: bool = True, want_disabled: bool = True) -> str:
    parts = []
    if want_enabled:
        if (packages := _format_package_list(option.packages_overridden_on)):
            parts.append('enabled manually: ' + packages)
        if (default := _format_package_list(option.packages_left_on)):
            parts.append('enabled by default: ' + default)
    if want_disabled:
        if (packages := _format_package_list(option.packages_overridden_off)):
            parts.append('disabled manually: ' + packages)
        if (default := _format_package_list(option.packages_left_off)):
            parts.append('disabled by default: ' + default)
    return '; '.join(parts)


def print_options_report(options: Iterable[OptionInfo], verbose: int) -> None:
    logging.debug('generating report')

    for option in options:
        if option.packages_default_bad:
            print(f'{option.name}: exists in port, but not in package (bad port or package should be rebuilt)')
            print(f'  {_format_package_list(option.packages_default_bad)}')

        if option.status == OptionStatus.UNCHANGED:
            if verbose >= 2:
                print(f'{option.name}: unchanged')
        elif option.status == OptionStatus.ALWAYS_ENABLED:
            print(f'{option.name}: enabled in all packages')
            if verbose >= 1:
                print(f'  {_format_package_list(option.packages_on)}')
        elif option.status == OptionStatus.ALWAYS_DISABLED:
            print(f'{option.name}: disabled in all packages')
            if verbose >= 1:
                print(f'  {_format_package_list(option.packages_off)}')
        elif option.status == OptionStatus.MIXED:
            print(f'{option.name}: mixed status')
            if option.packages_overridden_on:
                print('  overridden to ON')
                print(f'    {_format_package_list(option.packages_overridden_on)}')

            if option.packages_overridden_off:
                print('  overridden to OFF')
                print(f'    {_format_package_list(option.packages_overridden_off)}')

            if option.packages_left_on:
                print('  left ON as default')
                print(f'    {_format_package_list(option.packages_left_on)}')

            if option.packages_left_off:
                print('  left OFF as default')
                print(f'    {_format_package_list(option.packages_left_off)}')


def print_make_conf(options: list[OptionInfo], package_to_origin: dict[str, str]) -> None:
    logging.debug('generating make.conf')

    print('# options list generated by aggregate_port_options')
    for option in options:
        if option.packages_default_bad:
            print(f'# {option.name}: exists in port, but not in package')

        if option.status == OptionStatus.UNCHANGED:
            print(f'# {option.name}: unchanged, {_format_package_lists(option)}')
        elif option.status == OptionStatus.ALWAYS_ENABLED:
            print(f'OPTIONS_SET+=\t{option.name}  # {_format_package_lists(option)}')
        elif option.status == OptionStatus.ALWAYS_DISABLED:
            print(f'OPTIONS_UNSET+=\t{option.name}  # {_format_package_lists(option)}')
        elif option.status == OptionStatus.MIXED:
            print(f'# {option.name}: mixed status, {_format_package_lists(option)}')

            if len(option.packages_on) == 1 and len(option.packages_off) > 1:
                package = next(iter(option.packages_on))
                print(f'.if "${{.CURDIR:H:T}}/${{.CURDIR:T}}" != "{package_to_origin[package]}"')
                print(f'OPTIONS_UNSET+=\t{option.name}')
                print('.endif')

            elif len(option.packages_off) == 1 and len(option.packages_on) > 1:
                package = next(iter(option.packages_off))
                print(f'.if "${{.CURDIR:H:T}}/${{.CURDIR:T}}" != "{package_to_origin[package]}"')
                print(f'OPTIONS_SET+=\t{option.name}')
                print('.endif')

            else:
                for package in option.packages_overridden_on:
                    print(f'.if "${{.CURDIR:H:T}}/${{.CURDIR:T}}" == "{package_to_origin[package]}"')
                    print(f'OPTIONS_SET+=\t{option.name}')
                    print('.endif')

                for package in option.packages_overridden_off:
                    print(f'.if "${{.CURDIR:H:T}}/${{.CURDIR:T}}" == "{package_to_origin[package]}"')
                    print(f'OPTIONS_UNSET+=\t{option.name}')
                    print('.endif')

    print('# end generated options list')
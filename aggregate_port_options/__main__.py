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

import argparse
import logging

from aggregate_port_options.option_processing import iterate_options
from aggregate_port_options.package_processing import iterate_packages
from aggregate_port_options.report import print_make_conf, print_options_report
from aggregate_port_options.utils import Pkg, Ports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--debug', action='store_true', help='enable debug logging')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='enable verbose output')
    parser.add_argument('-p', '--ports-path', type=str, default='/usr/ports', help='path to ports tree')

    parser.add_argument('-m', '--make-conf', action='store_true', help='generate make.conf')

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG if args.debug else logging.INFO,
    )

    pkg = Pkg()
    ports = Ports(ports_path=args.ports_path)

    packages = list(iterate_packages(pkg, ports))
    options = list(iterate_options(packages))

    if args.make_conf:
        package_to_origin = { package.name: package.origin for package in packages }
        print_make_conf(options, package_to_origin)
    else:
        print_options_report(options, args.verbose)


main()

FLAKE8?=	flake8
MYPY?=		mypy
ISORT?=		isort
PYTHON?=	python3
TWINE?=		twine

lint: flake8 mypy isort-check

flake8::
	${FLAKE8} --application-import-names=aggregate_port_options aggregate_port_options

mypy::
	${MYPY} aggregate_port_options

isort-check::
	${ISORT} --check aggregate_port_options/*.py

isort::
	${ISORT} aggregate_port_options/*.py

sdist::
	${PYTHON} setup.py sdist

release::
	rm -rf dist
	${PYTHON} setup.py sdist
	${TWINE} upload dist/*.tar.gz

# Makefile for globonetworkapi

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  docs       to create documentation files"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  compile    to compile .py files (just to check for syntax errors)"
	@echo "  test       to execute all tests"
	@echo "  build      to build without installing"
	@echo "  install    to install"
	@echo "  dist       to create egg for distribution"
	@echo "  publish    to publish the package to PyPI"
	@echo

default:
	@awk -F\: '/^[a-z_]+:/ && !/default/ {printf "- %-20s %s\n", $$1, $$2}' Makefile

pip: # install pip libraries
	@pip install -r requirements.txt
	@pip install -r requirements_test.txt

db_reset: # drop and create database
	@[ -z $NETWORKAPI_DATABASE_PASSWORD ] && [ -z $NETWORKAPI_DATABASE_USER ] && [ -z $NETWORKAPI_DATABASE_HOST ] && mysqladmin -hlocalhost -uroot -f drop networkapi; true
	@[ -z $NETWORKAPI_DATABASE_PASSWORD ] && [ -z $NETWORKAPI_DATABASE_USER ] && [ -z $NETWORKAPI_DATABASE_HOST ] && mysqladmin -hlocalhost -uroot -f create networkapi; true
	@[ -n $NETWORKAPI_DATABASE_PASSWORD ] && [ -n $NETWORKAPI_DATABASE_USER ] && [ -n $NETWORKAPI_DATABASE_HOST ] && mysqladmin -hNETWORKAPI_DATABASE_HOST -uNETWORKAPI_DATABASE_USER -pNETWORKAPI_DATABASE_PASSWORD -f drop networkapi; true
	@[ -n $NETWORKAPI_DATABASE_PASSWORD ] && [ -n $NETWORKAPI_DATABASE_USER ] && [ -n $NETWORKAPI_DATABASE_HOST ] && mysqladmin -hNETWORKAPI_DATABASE_HOST -uNETWORKAPI_DATABASE_USER -pNETWORKAPI_DATABASE_PASSWORD -f create networkapi; true

run: # run local server
	@python manage.py runserver 0.0.0.0:8000 $(filter-out $@,$(MAKECMDGOALS))

shell: # run django shell
	@python manage.py shell_plus

clean:
	@echo "Cleaning..."
	@rm -rf build dist *.egg-info
	@rm -rf docs/_build
	@find . \( -name '*.pyc' -o -name '**/*.pyc' -o -name '*~' \) -delete

docs: clean
	@(cd docs && make html)

compile: clean
	@echo "Compiling source code..."
	@python -tt -m compileall .
	#@pep8 --format=pylint --statistics networkapiclient setup.py

test: compile
	@[ ! -z $(NETWORKAPI_DATABASE_PASSWORD) ] && [ ! -z $(NETWORKAPI_DATABASE_USER) ] && [ ! -z $(NETWORKAPI_DATABASE_HOST) ] && mysqladmin -h $(NETWORKAPI_DATABASE_HOST) -u $(NETWORKAPI_DATABASE_USER) -p $(NETWORKAPI_DATABASE_PASSWORD) -f drop if exists test_networkapi; true
	@[ -z $(NETWORKAPI_DATABASE_PASSWORD) ] && [ -z $(NETWORKAPI_DATABASE_USER) ] && [ -z $(NETWORKAPI_DATABASE_HOST) ] && mysql -u root -e "DROP DATABASE IF EXISTS test_networkapi;"; true
	@python manage.py test --traceback $(filter-out $@,$(MAKECMDGOALS))

install:
	@python setup.py install

build:
	@python setup.py build

dist: clean
	@python setup.py sdist

publish: clean
	@python setup.py sdist upload


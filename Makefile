#
# Makefile for Network API project
#


# Docker image version
NETAPI_IMAGE_VERSION := 2.0.0


help:
	@echo
	@echo "Network API"
	@echo
	@echo "Available target rules"
	@echo
	@echo "Local:"
	@echo "  start      to run project through docker compose"
	@echo "  stop       to stop all containers from docker composition"
	@echo "  logs       to follow logs on application container"
	@echo "  tests      to execute tests using containers. Use app variable"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  fixture    to generate fixtures from a given model"
	@echo "  test       to execute all tests locally"
	@echo
	@echo "Build:"
	@echo "  build_img  to build docker images"
	@echo "  docs       to create documentation files"
	@echo "  compile    to compile .py files (just to check for syntax errors)"
	@echo "  build      to build without installing"
	@echo "  install    to install"
	@echo "  dist       to create egg for distribution"
	@echo
	@echo "Remote:"
	@echo "  publish    to publish the package to PyPI"
	@echo "  push_img   to push image to docker hub"
	@echo


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



#
# Containers based target rules
#

start: docker-compose.yml
	@docker-compose up --detach


stop: docker-compose.yml
	@docker-compose down --remove-orphans


logs:
	@docker logs --tail 100 --follow netapi_app


tests:
	@clear
	@echo "Running NetAPI tests.."
	time docker exec -it netapi_app ./fast_start_test_reusedb.sh ${app}


fixture:
ifeq (${model},)
	$(error Missing model. Usage: make fixture model=interface.PortChannel)
endif
	docker exec -it netapi_app django-admin.py dumpdata ${model}


build_img: scripts/docker/Dockerfile
	docker build -t networkapi:latest --file scripts/docker/Dockerfile .
	docker build -t networkapi:$(NETAPI_IMAGE_VERSION) --file scripts/docker/Dockerfile .


push_img: scripts/docker/push_image.sh
	./$^

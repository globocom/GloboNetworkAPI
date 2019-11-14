#
# Makefile for Network API project
#


# Docker image version
NETAPI_IMAGE_VERSION := 2.1.0

# Gets git current branch
curr_branch := $(shell git symbolic-ref --short -q HEAD)

# Gets git current branch
curr_version := $(shell cat version.txt);

# Sed binary depends on Operating system
ifeq ($(shell uname -s),Darwin)
	SED_TYPE := gsed
else
	SED_TYPE := sed
endif


help:
	@echo
	@echo "Network API"
	@echo
	@echo "Available target rules"
	@echo
	@echo "Local:"
	@echo "  api	    To get a shell of network_app container"
	@echo "  db	        To get a shell of network_db container"
	@echo "  start      to run project through docker compose"
	@echo "  stop       to stop all containers from docker composition"
	@echo "  logs       to follow logs on application container"
	@echo "  test       to execute tests using containers. Use app variable"
	@echo "  status     to show containers status"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  fixture    to generate fixtures from a given model"
	@echo "  tag        to create a new tag based on the current versioni"
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
	@echo "  test_ci    Used by Travis CI to run tests on django applications. The app name must be provided. Ex. ''make test_ci app=networkapi/api_environment'"
	@echo "  test_ci_travis    To locally run the same Travis CI tests"
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


install:
	@python setup.py install


api:
	@docker exec -it netapi_app sh


db: 
	@docker exec -it netapi_db bash


build:
	@docker-compose up --build -d


dist: clean
	@python setup.py sdist


publish: clean
	@python setup.py sdist upload



#
# Containers based target rules
#

start: docker-compose-sdn.yml docker-compose.yml
	docker-compose up --force-recreate --remove-orphans -d
	docker-compose --file $< up --force-recreate -d


stop: docker-compose-sdn.yml docker-compose.yml
	@docker-compose down --remove-orphans


logs:
	@docker logs --tail 100 --follow netapi_app


status:
	docker ps --all --format "{{.ID}}\t{{.Names}}\t{{.Status}}"


test:
	@clear
	@echo "Running NetAPI tests for app '${app}'"
	time docker exec -it netapi_app ./fast_start_test_reusedb.sh ${app}


test_ci:
	@echo "Running NetAPI tests for app '${app}'"
	time docker exec -it netapi_app ./fast_start_test.sh ${app}


test_ci_travis:
	@echo "Running the same NetAPI tests enabled on travis"
	time docker exec -it netapi_app ./thesame_tests_travis_does.sh

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
	
tag:
ifneq ($(curr_branch),master)
	$(error Branch must be master to generate a new tag)
endif
ifeq ($(shell which $(SED_TYPE)),)
	$(error Missing GNU sed. Install it with 'brew install gnu-sed')
endif
	@echo "Current version is: $(curr_version)"
	@read -p "Enter new tag/version: " tag; \
		echo "Bumping to tag: $$tag"; \
		echo $$tag > version.txt; \
		git diff; \
		git add version.txt ; \
		git commit --message "Update version to $$tag"; \
		git tag --annotate $$tag --message "Bump version to $$tag"; \
		git push origin master --tags;


COMPOSE_CMD=docker-compose -p gissues -f docker/docker-compose.yml

build:
	$(COMPOSE_CMD) build

up:
	$(COMPOSE_CMD) up -d

down:
	$(COMPOSE_CMD) down --remove-orphans --volumes

logs:
	$(COMPOSE_CMD) logs -f

restart:
	$(COMPOSE_CMD) restart

stop:
	$(COMPOSE_CMD) stop

start:
	$(COMPOSE_CMD) start

django:
	$(COMPOSE_CMD) exec web python3 manage.py $(filter-out $@,$(MAKECMDGOALS))

shell:
	$(COMPOSE_CMD) exec web python3 manage.py shell_plus

compile-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

test:
	$(COMPOSE_CMD) exec web pytest

mypy:
	$(COMPOSE_CMD) exec web mypy gissues/.

changelog:
	git cliff -o CHANGELOG.md

.PHONY: build up down logs restart stop start compile-requirements django shell test mypy changelog

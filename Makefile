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

clean:
	$(COMPOSE_CMD) down --remove-orphans --volumes
	$(COMPOSE_CMD) rm -f

django:
	$(COMPOSE_CMD) exec web python3 manage.py $(filter-out $@,$(MAKECMDGOALS))

compile-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

test:
	$(COMPOSE_CMD) exec web pytest

.PHONY: build up down logs restart stop start clean compile-requirements django test

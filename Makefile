.PHONY: build up down logs test shell db-shell clean

# Build and start services
build:
	docker-compose build

up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f api

# Run tests
test:
#	docker-compose --profile test run --rm test

# Shell into the API container
shell:
	docker-compose exec api bash

# Shell into the database
db-shell:
	docker-compose exec db psql -U hcs -d hcs

# Clean up containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Development setup
dev-setup:
	cp .env.example .env
	docker-compose up --build

# Run migration (if using Alembic)
migrate:
	docker-compose exec api alembic upgrade head
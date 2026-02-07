.PHONY: help build up down restart logs clean db-init db-reset

help:
	@echo "Available commands:"
	@echo "  make build      - Build all Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make clean      - Remove all containers and volumes"
	@echo "  make db-init    - Initialize database (create tables)"
	@echo "  make db-reset   - Reset database (WARNING: deletes all data)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

clean:
	docker compose down -v
	docker system prune -f

db-init:
	docker compose exec backend python scripts/init_db.py

db-reset:
	docker compose exec backend python -c "from app.database import reset_database; reset_database()"

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up


.PHONY: dev start stop stop-prod logs test migrate backup

dev:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build

start:
	cp -n .env.example .env 2>/dev/null || true
	docker compose -f docker-compose.prod.yml up --build -d

stop:
	docker compose down

stop-prod:
	docker compose -f docker-compose.prod.yml down

logs:
	docker compose logs -f

test:
	docker compose exec backend uv run pytest -v

migrate:
	docker compose exec backend uv run alembic upgrade head

backup:
	mkdir -p backups
	docker compose exec db pg_dump -U atoms atoms_dev > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup saved to backups/"

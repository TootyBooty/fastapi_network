up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

reload:
	docker compose -f docker-compose.yml up --build --detach


create_migrations:
	docker exec fastapi_network alembic revision --autogenerate

roll_migrations:
	docker exec fastapi_network alembic upgrade heads

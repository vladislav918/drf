
run:
	docker compose up

build:
	docker compose up --build

migrate:
	docker compose exec web ./manage.py migrate

makemigrations:
	docker compose exec web ./manage.py makemigrations
	make chown

test:
	docker compose exec web ./manage.py test --noinput
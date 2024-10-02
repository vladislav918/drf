
run:
	docker compose up

build:
	docker compose up --build

run -d:
	docker compose up -d

migrate:
	docker compose exec web ./manage.py migrate

migrations:
	docker compose exec web ./manage.py makemigrations
	make chown

test:
	docker compose exec web ./manage.py test --noinput

superuser:
	docker compose exec web ./manage.py createsuperuser

down:
	docker compose down

createsuperuser:
	docker compose exec web python manage.py createsuperuser
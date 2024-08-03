
run:
	docker-compose up

migrate:
	docker-compose exec web ./manage.py migrate

makemigrations:
	docker-compose exec web ./manage.py makemigrations
	make chown

test:
	docker-compose exec web ./manage.py test --noinput
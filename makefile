build:
	docker-compose up --build -d

start: 
	docker-compose start

stop:
	docker-compose stop

clean:
	docker-compose down --rmi all -v

install_uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

uv_init:
	cd backend && uv venv

uv_sync:
	cd backend && uv sync

uv_update:
<<<<<<< HEAD
	cd backend && uv lock --upgrade
=======
	cd backend && uv lock --upgrade
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953

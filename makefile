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
	cd backend && uv lock --upgrade

# Backend with A2A agents
backend_start:
	cd backend && ./start.sh

# Test A2A agent integration
test_agents:
	cd backend && uv run python test_integration.py
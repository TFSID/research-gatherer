.PHONY: up down build logs clean restart reset test

# Start all services
up:
	docker-compose up -d

# Build and start services
build:
	docker-compose up -d --build

# Stop all services
down:
	docker-compose down

# View real-time logs
logs:
	docker-compose logs -f

# Restart all services
restart:
	docker-compose restart

# Stop and remove volumes (WARNING: destroys data)
clean:
	docker-compose down -v

# Reset everything (clean + rebuild)
reset: clean build

# Check service status
status:
	docker-compose ps

# View MongoDB data (requires mongosh)
mongo:
	docker exec -it chatbot-mongodb mongosh

# Test backend health via frontend proxy
test:
	curl -s http://localhost:3000/health | python3 -m json.tool

# Open Mongo Express (via docker exec, not exposed)
mongo-ui:
	@echo "Mongo Express is internal. Use: docker exec -it chatbot-mongo-express sh"
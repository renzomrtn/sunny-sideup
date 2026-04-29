# YOUTH Project Setup and Manual

## Fresh Machine Setup

Use this flow when setting up the project on a different machine for the first time.

1. Create a `.env` file in every folder where a `.env.example` exists. Put the real values in each `.env` before building anything.

2. Restore the Authentik configuration:

```
.\authentik\restore-authentik.ps1
```

3. Start Authentik and verify the restored setup before starting the app:

```
docker compose up -d authentik-server authentik-worker
.\authentik\verify-authentik.ps1
```

4. Build the app images after the `.env` files and Authentik restore are correct:

```
docker compose build --no-cache youth-accmgmtsys identity-service
docker compose build
```

5. Start all services:

```
docker compose up -d
```

6. If it got messed up, just use; 

```
docker compose down -v
```

and repeat Steps 2 to 5 (given that all .env files are already created if not then return to Step 1)

## Docker Cheatsheet

### Start And Stop

1. Start all services:

```
docker compose up -d
```

2. Start all services and rebuild images:

```
docker compose up -d --build
```

3. Stop all services:

```
docker compose down
```

4. Stop all services and delete volumes/data:

```
docker compose down -v
```

Warning: `docker compose down -v` deletes database volumes, including Authentik and app data.

### Build

1. Build all services:

```
docker compose build
```

2. Build one service:

```
docker compose build <container-name>
```

### Logs

1. View logs for all services:

```
docker compose logs -f
```

2. View logs for one service:

```
docker compose logs -f <container-name>
```

### Containers

1. View running containers:

```
docker ps
```

2. View all containers:

```
docker ps -a
```

3. Restart one service:

```
docker compose restart <container-name>
```

4. Open a shell inside a container:

```
docker exec -it <container-name> sh
```
h
```
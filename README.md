# YOUTH - PROJECT MANAGEMENT AND MONITORING

Project Management and Monitoring Sub-module of the YOUTH System.

## About the System

The Project Management and Monitoring sub-module is designed to provide a centralized system for project management.

## Tech-Stack

* Vue Nuxt 3
* Postgresql
* FastAPI
* RabbitMQ
* Authentik
* Docker
* Git

## Installation Guide

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

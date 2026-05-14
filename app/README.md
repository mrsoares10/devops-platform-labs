# Tamagotchi App

A simple REST API that simulates a Tamagotchi. Stats decay over time and can be restored via the API endpoints.

## Endpoints

| Method | Path       | Description                            |
|--------|------------|----------------------------------------|
| GET    | `/healthz` | Health check                           |
| GET    | `/status`  | Get current stats                      |
| POST   | `/feed`    | Feed the Tamagotchi (increases hunger) |
| POST   | `/play`    | Play with it (increases happiness)     |
| POST   | `/sleep`   | Put it to sleep (increases energy)     |
| GET    | `/metrics` | Prometheus metrics                     |

## Running locally

``` bash
./run.sh
```

## Stats

Each stat ranges from 0 to 100 and decays by 5 every 300 seconds.

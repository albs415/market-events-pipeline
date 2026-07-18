# QQQ Reversal Engine

A deployable FastAPI dashboard for monitoring the probability, speed, and estimated magnitude of a potential intraday QQQ reversal.

## Current deployment mode

The public build runs in **simulation mode**. It demonstrates the state machine and dashboard without representing simulated values as live market predictions.

States:

`WATCHING → DEVELOPING → ARMED → TRIGGERED → CONFIRMED`

Endpoints:

* `/` dashboard
* `/api/signal` current simulated signal
* `/healthz` service health check

## Run locally

```bash
cd qqq-reversal-engine
python -m venv .venv
source .venv/bin/activate
pip install .
uvicorn app.main:app --reload
```

Open `http://localhost:8000`.

## Docker

```bash
docker build -t qqq-reversal-engine .
docker run --rm -p 8000:8000 qqq-reversal-engine
```

## Continuous deployment

The repository workflow compiles the application and builds its container. After changes reach `main`, it publishes the container to GitHub Container Registry:

```text
ghcr.io/albs415/qqq-reversal-engine:latest
```

The repository also includes a Render blueprint for creating a public web service.

## Production limitations

Live operation requires licensed market-data feeds and valid credentials. The uploaded full engine project includes adapter and model scaffolding, but a public deployment must remain in simulation mode until those credentials are configured and the predictive model has passed out-of-sample validation.

This application provides decision support only. It does not submit trades, and its displayed probabilities must not be used for position sizing until the model is calibrated and validated against historical and paper-trading data.

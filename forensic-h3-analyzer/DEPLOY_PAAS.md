ForenGeo - PaaS Deployment (Heroku / Railway)

This document summarizes steps to deploy ForenGeo to Heroku or Railway using the included `Procfile` and Docker image.

1) Heroku (Git-based or Container Registry)

- Using Git (Heroku will build the app using the Dockerfile if using container stack):
  - Create an app: `heroku create your-app-name`
  - Push: `git push heroku main`
  - Set config vars (optional):
    - `heroku config:set FORNEGO_DB_PATH=.fh3.db`
  - Scale web dyno: `heroku ps:scale web=1`

- Using Heroku Container Registry:
  - Login: `heroku container:login`
  - Build & push: `heroku container:push web -a your-app-name`
  - Release: `heroku container:release web -a your-app-name`

2) Railway

- Create a new project, connect a GitHub repo or deploy via Docker image.
- Add environment variables if needed (`FORNEGO_DB_PATH`, `FORNEGO_DEBUG`, etc.).

3) Docker Registry (Docker Hub / GHCR)

- Build locally:
  ```bash
  docker build -t forengeo .
  ```
- Test run locally:
  ```bash
  docker run --rm -p 5000:5000 forengeo
  ```
- Tag and push (example to Docker Hub):
  ```bash
  docker tag forengeo your_dockerhub_user/forengeo:latest
  docker push your_dockerhub_user/forengeo:latest
  ```

Notes & Security
- The container initializes `.fh3.db` on first run using `docker-entrypoint.sh`.
- For multi-tenant production, use external persistent storage for the database (bind mount or managed DB).
- Use strong API key management for OSINT services and do not store keys in the repo.
- Consider adding TLS termination via a reverse proxy (NGINX) or platform-managed TLS.

API Token

To secure the API, set the `FORNEGO_API_TOKEN` environment variable in your deployment. When set, the app requires this token (Bearer) for `/api/*` endpoints except `/api/status`. The web UI includes a "Set API Token" button which stores the token in `localStorage` and attaches it to requests.

Environment variables supported
- `FORNEGO_DB_PATH` - path to DB (default: .fh3.db)
- `FORNEGO_HOST` - host binding (default: 0.0.0.0)
- `FORNEGO_PORT` - port (default: 5000)
- `FORNEGO_DEBUG` - debug mode (true/false)

For help pushing to a specific registry, provide credentials or allow me to generate sample commands for your registry of choice.

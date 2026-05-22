# DevSecOps for ForenGeo

This repository now includes a secure development lifecycle for ForenGeo with automated quality, security, and deployment checks.

## What is included

- **Automated CI pipeline** in `.github/workflows/ci.yml`
- **Deterministic unit tests** in `test_devsecops.py`
- **Secure dependency management** via `requirements.txt` and `requirements-dev.txt`
- **Static code quality** with `flake8` and `black`
- **Security scanning** with `pip-audit` and `bandit`
- **Hardened Docker build** in `Dockerfile` using a non-root service user
- **Clean container context** via `.dockerignore`
- **Local and demo automation** with `demo_devsecops.py`

## DevSecOps workflow

1. Code is developed locally and dependencies are pinned.
2. Changes are pushed or opened as a pull request.
3. GitHub Actions runs `ci.yml`:
   - install application and development dependencies
   - perform linting and compile checks
   - run deterministic tests
   - audit Python dependencies for known vulnerabilities
   - scan code for common security issues
4. Approved changes are merged and deployed using the same reproducible environment.

## How to run locally

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q test_devsecops.py
python3 demo_devsecops.py
```

## Docker deployment

Build and run the hardened container:

```bash
docker build -t forengeo .
docker run --rm -p 5000:5000 forengeo
```

## Notes

- This workflow keeps generated artifacts out of Git with `.gitignore` and `.dockerignore`.
- Deterministic tests are designed to work without external network dependencies.
- Security scanning is automated so the project can be audited continuously.

Pushing ForenGeo Docker image to a registry

Docker Hub example:

```bash
# Log in
docker login
# Tag image
docker tag forengeo your_dockerhub_user/forengeo:latest
# Push
docker push your_dockerhub_user/forengeo:latest
```

GitHub Container Registry (GHCR) example:

```bash
# Build and tag
docker build -t ghcr.io/your-org/forengeo:latest .
# Login using GitHub CLI
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
# Push
docker push ghcr.io/your-org/forengeo:latest
```

Notes:
- Replace `your_dockerhub_user` and `your-org` with your account details.
- For CI/CD, store registry credentials in secrets and use automated workflows to push on release tags.

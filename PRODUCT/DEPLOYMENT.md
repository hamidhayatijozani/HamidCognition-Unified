# Production Deployment

## Architecture

Internet → Caddy/HTTPS → Customer Console + MCP → Action Gate → protected tool → PostgreSQL.

The production Compose stack is `action_gate/docker-compose.production.yml`.

## Deployment contract

The deployment host must already provide:
- Linux with Docker Engine;
- Docker Compose v2;
- public DNS pointing the selected domain to the host;
- inbound TCP 80/443;
- outbound access to GitHub and Docker registries;
- an SSH account used by the GitHub Actions deployment environment.

The deployment workflow is `.github/workflows/deploy-production.yml`.

Required GitHub Actions production secrets:
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`

No application secret is stored in GitHub. The remote deployment script creates the initial production secrets on the host with `openssl` and keeps them in `action_gate/.env.production` with mode 600. Existing production secrets are preserved on later deployments.

Run: GitHub → Actions → Deploy HamidCognition Production → Run workflow, supplying the already configured HTTPS domain.

## What the workflow verifies

1. The host receives the deployment script over SSH.
2. The host checks Docker and Compose.
3. The host checks out the current `main` revision.
4. Production Compose is rendered before startup.
5. Dashboard, Action Gate, PostgreSQL, MCP, enforcement and Caddy are built/started.
6. Caddy obtains/renews HTTPS certificates for the supplied domain.
7. The public dashboard and `/health` endpoint are checked from the GitHub runner.

## Security boundary

The workflow never accepts an application API token, signing secret, database password or MCP token as a GitHub workflow input. Those are generated on the deployment host if the production environment has not been initialized.

Do not expose PostgreSQL or internal Action Gate ports publicly. Only 80/443 should be reachable from the internet.

## Current truth

Creating this workflow does not mean a public deployment already exists. A real deployment requires an actual host, DNS and the three SSH secrets above. Until the workflow succeeds against that infrastructure, the product is not described as publicly deployed.

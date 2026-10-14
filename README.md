# Syllabus

A small web app that tracks how much of a syllabus a student has actually covered.

You add your subjects (Operating Systems, Discrete Maths, and so on) and split each one into topics. Every topic moves through **to study → in progress → done**. It also gets a difficulty rating from 1 to 5 and a rough estimate of the hours it needs. The dashboard then shows how much of each subject is done, how many hours of study are left, and how close each exam is. Subjects with an exam coming up soon and little progress get flagged in red.

The app itself is deliberately small. Most of this repo is about getting it from a laptop onto a monitored Kubernetes cluster on AWS. It has tests, containers, a CI/CD pipeline with image scanning, Terraform, Helm, autoscaling, Prometheus and Grafana.

```
 push to main
      │
      ▼
 GitHub Actions ── pytest ── vite build ── docker build ── trivy scan ── push to GHCR
                                                                            │
                                                                            ▼
                                     Terraform (VPC + EKS) ──────────► helm upgrade
                                                                            │
                                     ┌──────────── ingress-nginx ───────────┤
                                     │  /            /api                   │
                                     ▼               ▼                      │
                                 frontend ────►  backend (HPA) ───► postgres│
                                 (nginx)         (FastAPI)                  │
                                                     │ /metrics             │
                                                     ▼                      │
                                               Prometheus ──► Grafana       │
```

## Stack

| Layer | What's used |
|---|---|
| Frontend | React 18 + Vite, plain CSS, served by unprivileged nginx |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic |
| Database | PostgreSQL 16 |
| Tests | pytest + FastAPI TestClient on an in-memory SQLite database |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions, GHCR, Trivy |
| Infra | Terraform (`terraform-aws-modules` VPC + EKS), region `ap-south-1` |
| Platform | Kubernetes, Helm, ingress-nginx, HPA, metrics-server |
| Observability | kube-prometheus-stack (Prometheus Operator + Grafana) |

## Repository layout

```
backend/            FastAPI app, Alembic migrations, pytest suite
frontend/           React dashboard, nginx config, multi-stage Dockerfile
docker-compose.yml  postgres + backend + frontend for local use
.github/workflows/  CI/CD pipeline
terraform/          VPC, EKS cluster, node group, EBS CSI driver
k8s/                namespace and gp3 storage class
helm/syllabus/      Helm chart for the whole app
monitoring/         values for kube-prometheus-stack and metrics-server
troubleshooting/    deliberately broken manifests for debugging practice
scripts/            seed data and an HPA load generator
```

## API

| Method | Path | |
|---|---|---|
| GET | `/health` | liveness: the process is up |
| GET | `/ready` | readiness: the database is reachable |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/subjects` | list subjects with topic counts and % complete |
| GET | `/api/subjects/{id}` | one subject |
| POST | `/api/subjects` | create a subject |
| PUT | `/api/subjects/{id}` | update a subject |
| DELETE | `/api/subjects/{id}` | delete a subject and its topics |
| GET | `/api/topics?subject_id=&status=&search=` | list or filter topics |
| GET | `/api/topics/{id}` | one topic |
| POST | `/api/topics` | create a topic |
| PUT | `/api/topics/{id}` | update a topic (moving to `done` stamps `completed_at`) |
| DELETE | `/api/topics/{id}` | delete a topic |
| GET | `/api/stats` | overall progress, hours left, difficulty breakdown, per-subject progress |

Interactive docs are at `/docs` once the backend is running.

## Running locally

### Docker Compose

```bash
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

To load some sample subjects and topics:

```bash
python3 scripts/seed.py http://localhost:3000
```

`docker compose down -v` stops everything and also deletes the database volume.

### Without Docker

You'll need Python 3.12+, Node 20+ and a Postgres instance.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL='postgresql+psycopg://syllabus:syllabus@localhost:5432/syllabus'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Vite runs on http://localhost:5173 and forwards `/api` requests to port 8000.

## Tests

```bash
cd backend
pytest -v
```

The tests never touch Postgres. `tests/conftest.py` replaces the `get_db` dependency with a session on an in-memory SQLite database, and the tables are created fresh for each test. There are 17 tests covering subjects, topics, stats, validation, cascading deletes and the health, ready and metrics endpoints.

## CI/CD

`.github/workflows/ci.yml` runs on every push and pull request to `main`.

1. **test**: installs the backend dependencies, runs `pytest -v`, then runs `npm ci && npm run build` for the frontend. If any test fails, nothing after this point runs.
2. **build** (backend and frontend in parallel): builds each image, scans it with Trivy, and only pushes it to GHCR if the scan passes. Images are tagged with the full commit SHA, e.g. `ghcr.io/tripleyouuu/syllabus-backend:<sha>`, so any running pod can be traced back to the exact commit it came from. Pull requests build and scan but don't push.
3. **deploy**: runs `helm upgrade --install` against EKS with the new SHA tags. It only runs when the repository variable `DEPLOY_ENABLED` is `true`, so pushes don't fail while the cluster is torn down.

Settings the deploy job needs (Settings → Secrets and variables → Actions):

| Type | Name | Value |
|---|---|---|
| Secret | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | an IAM user that can call `eks:DescribeCluster` |
| Secret | `POSTGRES_PASSWORD` | database password used by the chart |
| Variable | `DEPLOY_ENABLED` | `true` once the cluster exists |
| Variable | `AWS_REGION` | optional, defaults to `ap-south-1` |
| Variable | `EKS_CLUSTER_NAME` | optional, defaults to `syllabus-dev-eks` |

After the first push, make both GHCR packages public (Package settings → Change visibility) so the cluster can pull them without credentials.

## Security scanning

Trivy scans each finished image before it is pushed. It checks the OS packages (Debian for the backend, Alpine for nginx) and the Python dependencies installed in the image against known CVE databases. The step uses `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`, so the build fails on any high or critical vulnerability that already has a fix available.

The first scan of this project failed for a real reason. Starlette 0.48, pulled in by FastAPI, had CVE-2025-62727: overlapping `Range` headers could be merged in a way that let a client tie up the server (a denial of service). The nginx 1.27 Alpine base also had unpatched `musl`, `zlib` and `libxml2` packages. Upgrading FastAPI and Starlette, moving to nginx 1.29, and running `apk upgrade` in the frontend image brought both scans to zero.

## Infrastructure (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

This creates:

- a VPC (`10.20.0.0/16`) with two public and two private subnets across two AZs, and a single NAT gateway to keep costs down
- an EKS cluster (`syllabus-dev-eks`) whose control plane runs in the private subnets
- a managed node group of 2–4 `c7i-flex.large` nodes (free-tier eligible)
- the CoreDNS, kube-proxy, VPC CNI, Pod Identity and EBS CSI add-ons (the EBS CSI driver gets its own IRSA role so Postgres and Prometheus can use persistent volumes)

Then point kubectl at the cluster:

```bash
aws eks update-kubeconfig --region ap-south-1 --name syllabus-dev-eks
```

Credentials come from your AWS CLI profile and are never written into the repo. `terraform.tfvars` and the state files are gitignored.

## Deploying to Kubernetes

The cluster add-ons need to be installed once, in this order:

```bash
kubectl apply -f k8s/

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx --create-namespace

helm upgrade --install metrics-server metrics-server/metrics-server \
  -n kube-system -f monitoring/metrics-server-values.yaml

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml \
  --set grafana.adminPassword='<pick-one>'
```

Then the app itself. The pipeline normally does this step, but it can also be run by hand:

```bash
helm upgrade --install syllabus ./helm/syllabus -n syllabus \
  -f helm/syllabus/values-eks.yaml \
  --set backend.image.tag=<sha> \
  --set frontend.image.tag=<sha> \
  --set postgres.password='<password>'
```

What the chart creates:

- **backend** Deployment (2+ replicas): liveness probe on `/health`, readiness probe on `/ready`, runs as UID 10001 with all capabilities dropped
- **frontend** Deployment (2 replicas): nginx on port 8080 as UID 101, proxies `/api` to the backend Service
- **postgres** StatefulSet with a PVC, plus a ClusterIP Service
- a **migration Job** that waits for Postgres and runs `alembic upgrade head` on every release, so the API pods never race each other on schema changes
- ClusterIP **Services** for all three
- an **Ingress** that sends `/api`, `/docs` and `/openapi.json` to the backend and everything else to the frontend
- an **HPA** that scales the backend between 2 and 6 pods at 60% CPU
- a **ServiceMonitor** and a **Grafana dashboard** ConfigMap

Find the public address with:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

### Local cluster (minikube)

```bash
minikube addons enable ingress
minikube addons enable metrics-server
kubectl apply -f k8s/namespace.yaml
helm upgrade --install syllabus ./helm/syllabus -n syllabus -f helm/syllabus/values-dev.yaml \
  --set backend.image.tag=<sha> --set frontend.image.tag=<sha>
echo "$(minikube ip) syllabus.local" | sudo tee -a /etc/hosts
```

Then open http://syllabus.local.

### Autoscaling

```bash
kubectl get hpa -n syllabus -w
./scripts/load-test.sh
```

The load script starts a busybox pod inside the cluster that hammers `/api/stats` with 20 parallel loops for three minutes. As backend CPU goes past 60% of its request, the HPA adds pods. Once the load stops, it scales back down after a two-minute stabilisation window.

## Monitoring

The backend uses `prometheus-fastapi-instrumentator` to expose request counts and latency histograms at `/metrics`. Because the chart's ServiceMonitor is labelled for the `monitoring` release, Prometheus discovers it automatically.

```bash
kubectl port-forward -n monitoring svc/monitoring-prometheus 9090:9090
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
```

- Prometheus targets: http://localhost:9090/targets. Look for `serviceMonitor/syllabus/syllabus-backend` showing as UP.
- Grafana: http://localhost:3001. The **Syllabus API** dashboard has request rate, p50/p95/p99 latency, 5xx error ratio, responses by status class, and CPU per backend pod.

## Troubleshooting lab

`troubleshooting/` has three broken manifests: an image tag that doesn't exist, a Service whose selector matches no pods, and a pod that runs but never becomes Ready because its DB password is wrong. [troubleshooting/README.md](troubleshooting/README.md) walks through diagnosing each one with `kubectl`.

## Tearing down

Delete the Kubernetes resources that created AWS objects **before** running `terraform destroy`. Otherwise the load balancer and EBS volumes they created will block the VPC from being deleted.

```bash
helm uninstall syllabus -n syllabus
helm uninstall monitoring -n monitoring
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete pvc --all -n syllabus
kubectl delete pvc --all -n monitoring

cd terraform
terraform destroy
```

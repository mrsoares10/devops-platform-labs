# DevOps Platform Labs

A personal learning and portfolio project covering platform engineering end-to-end across two tracks: a local Kubernetes platform and a cloud OpenShift environment.

---

##  Local Kubernetes Platform

A GitOps platform running on Minikube where GitHub Actions builds and publishes container images, ArgoCD automatically deploys them, Traefik handles ingress with TLS, Vault manages secrets, and the PLG stack provides full observability.

### Stack

| Category      | Tools                                                      |
|---------------|------------------------------------------------------------|
| Cluster       | Minikube                                                   |
| Ingress + TLS | Traefik, cert-manager                                      |
| GitOps        | ArgoCD                                                     |
| CI/CD         | GitHub Actions, GitHub Container Registry (GHCR)           |
| Security      | Vault, Trivy                                               |
| Observability | OpenTelemetry Collector, Prometheus, Loki, Grafana         |
| App           | Tamagotchi REST API (Python/Flask), packaged as Helm chart |

### Phases

**Phase 1 — Cluster Foundation**
- Minikube with sufficient resources (4 CPU, 8 GB RAM)
- Traefik as ingress controller with cert-manager for TLS
- ArgoCD exposed through Traefik

**Phase 2 — The App**
- Tamagotchi REST API in Python/Flask with `/healthz`, `/status`, `/feed`, `/play`, `/sleep`, `/metrics`
- Exposes Prometheus metrics (hunger, happiness, energy gauges)
- Packaged as a Helm chart, deployed via ArgoCD

**Phase 3 — GitOps with ArgoCD**
- ArgoCD watches `local-k8s/manifests/` for changes
- Syncs automatically on every commit to `main`

**Phase 4 — CI with GitHub Actions**
- On push: build Docker image → push to GHCR
- Trivy image scan — fails the build on critical vulnerabilities
- Update image tag in manifests → ArgoCD picks it up

**Phase 5 — Secrets**
- Vault for secret storage and dynamic credentials
- App manifests reference Vault paths — no secrets committed to git

**Phase 6 — Observability**
- OpenTelemetry Collector as the central signal hub
- Prometheus for metrics scraping and storage
- Loki for log aggregation
- Grafana dashboards wiring it all together

### Directory Layout

```
local-k8s/
├── charts/                 # Helm values overrides for bootstrap tools
│   ├── traefik/
│   └── argocd/
├── manifests/
│   ├── apps/               # ArgoCD Application CRDs (cert-manager, vault, loki, prometheus, grafana, tamagotchi)
│   └── infra/              # raw manifests applied with kubectl (IngressRoutes, Certificates, ClusterIssuer)
└── scripts/                # bootstrap (minikube start, helm installs)

app/
├── app.py                  # Tamagotchi Flask API
├── requirements.txt
├── Dockerfile
├── run.sh                  # local dev runner
└── chart/                  # Helm chart for Kubernetes deployment
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
```

---

## Track 2 — OpenShift + Terraform

Infrastructure-as-code for an OpenShift cluster on a cloud provider, using GitHub Actions as the GitOps engine for Terraform — `plan` on pull request, `apply` on merge to `main`.

### Stack

| Category | Tools                         |
|----------|-------------------------------|
| Platform | OpenShift (free 30-day trial) |
| IaC      | Terraform                     |
| CI/CD    | GitHub Actions                |

### Directory Layout

```
openshift/
├── modules/                # reusable Terraform modules
│   ├── cluster/
│   ├── networking/
│   └── operators/
├── environments/
│   └── dev/                # tfvars + backend config
└── .github/
    └── workflows/
        └── terraform.yaml  # plan on PR, apply on merge
```

---

## Repository Layout

```
devops-platform-labs/
├── local-k8s/
├── openshift/
└── README.md
```

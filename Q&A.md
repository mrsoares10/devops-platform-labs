## What if I dont use traefik?

Then you'd need to expose each service individually — a NodePort or port-forward for ArgoCD, another for Grafana, another for Vault, etc. No clean URLs, no single entry point, no TLS termination in one place.

For a portfolio project specifically, having Traefik is worth it — it shows you understand ingress architecture. Without it the setup looks incomplete.

## Is this the best approach to take, every time I want to do some infra from scratch?

Yes, this is the right order — it's called dependency-driven deployment:

1. Traefik first — ingress layer, everything else needs it to be accessible
2. ArgoCD — once you can access it, it takes over deploying everything else
3. Everything else via ArgoCD — Vault, LGTM stack, your app

The key insight is that once ArgoCD is running, you stop doing helm install manually. Instead you define Application CRDs and ArgoCD manages the deployments. That's the GitOps pattern — git is the source of truth, ArgoCD reconciles the cluster to match it.

So the bootstrap is just: Traefik + ArgoCD manually, then ArgoCD handles the rest.

## What are those IngressRoute files?

Without an IngressRoute, Traefik is running but has no rules — it doesn't know what to do with incoming requests. It's like a router with no routing table.

The IngressRoute tells Traefik:

When a request comes in matching Host(dashboard.localhost) on the web entrypoint
Send it to api@internal — which is Traefik's own internal dashboard service

## What is "terminating HTTPS"?

TLS termination means decrypting HTTPS traffic. The flow will be:

1. browser → HTTPS → Traefik (decrypts it) → HTTP → ArgoCD
2. Traefik handles the encryption/decryption at the edge. ArgoCD only ever sees plain HTTP internally — it doesn't need to know about TLS at all. That's why server.insecure: true is needed.

## In this local env, is traefik working as supposed?

Yes — Traefik is doing exactly what it should:

Single entry point for all traffic
Routing by hostname (argocd.localhost → ArgoCD, dashboard.localhost → Traefik dashboard)
All services are ClusterIP behind it

The only non-production part is how you reach Traefik itself (the minikube service tunnel instead of a real load balancer). Everything Traefik does internally is correct.

## If I grab this repo on another machine, I will be able to replicate the local env?

Yes, that's the goal. With a README explaining the setup and the bootstrap scripts we'll add, anyone can:

1. Install Minikube, Helm, kubectl
2. Run the bootstrap script
3. Get the same environment

The only machine-specific things are /etc/hosts entries and the Windows hosts file issue — those would need to be documented.

## Under manifests/apps there will be all my apps?

Yes — that's where all your ArgoCD Application manifests live. Each file tells ArgoCD to manage one thing.
The distinction is:

apps/ — ArgoCD Application CRDs (what ArgoCD manages)
infra/ — raw manifests applied directly with kubectl (IngressRoutes, etc.)

## How would I get the manifests info (cert-manager p.e.)?

From the cert-manager docs and the ArgoCD docs combined:

repoURL and chart name → from the cert-manager Helm installation docs (helm repo add jetstack https://charts.jetstack.io)
targetRevision → latest stable version from the cert-manager releases page or helm search repo cert-manager
installCRDs: true → cert-manager requires its CRDs to be installed, documented in their install guide
ArgoCD Application structure → from the ArgoCD docs on declarative setup

In general, for any tool you want ArgoCD to manage: find its Helm chart repo, check the install docs for required values, then wrap it in an ArgoCD Application.

## After kubectl apply cmd, ArgoCD pick it up and deploy cert-manager automatically. Why not use 'argocd app create' instead?

1. argocd app create → you type a command, ArgoCD creates the app, but nothing is stored in git
2. kubectl apply -f cert-manager.yaml → the app definition lives in your git repo, you apply it once, and from then on git is the record of what should exist

The second approach means if your cluster dies, you just kubectl apply all your manifests again and everything comes back — because git has the full definition. That's GitOps.

The argocd app create command itself isn't stored anywhere. If your cluster dies, you'd have to remember and retype all those commands. With the Application manifest in git, you just reapply the file.

If the cluster dies and you used kubectl apply -f cert-manager.yaml, you just run the same command again on the new cluster — the manifest is in git so you haven't lost anything.

If you used argocd app create, you'd need to remember all the flags and options you passed, or dig through ArgoCD's internal database (which is also gone if the cluster died).

So kubectl apply with manifests in git is always recoverable. argocd app create is not — unless you manually documented every command you ran.

## Applied the cluster issuer for the cert-manager. How should I know all these steps?

From the cert-manager docs — after installing cert-manager, the next step they always document is creating an Issuer or ClusterIssuer. That's the pattern:

1. Install the tool (Helm/ArgoCD)
2. Read its docs for post-install configuration
3. Apply the required resources

For cert-manager specifically: cert-manager.io/docs
As you do this more, you'll recognize the pattern. Most tools follow: install → configure → expose

## Is certificates.yaml the best approach?

Easier to manage when you have multiple services, and keeps the IngressRoute files focused on routing only.

## Why do I need to add argocd.localhost to /etc/hosts?

.localhost subdomains like argocd.localhost aren't automatically resolved to 127.0.0.1 by the OS — only the exact localhost is. The browser was handling the resolution differently (some browsers do resolve *.localhost to 127.0.0.1 automatically), but curl and the OS don't. So you need the /etc/hosts entry for curl and potentially for the browser too.

## What is the cert-manager workflow?

1. You create a Certificate resource (in certificates.yaml) — this is just a request saying "I need a TLS cert for argocd.localhost"
2. cert-manager sees that request and uses the ClusterIssuer to generate a certificate
3. cert-manager stores the result (certificate + private key) in a Kubernetes Secret (e.g. argocd-tls)
4. Traefik reads that Secret via the tls.secretName in the IngressRoute and uses it to serve HTTPS

So cert-manager is the middleman between "I want a cert" and "here's the cert in a Secret". Without it you'd have to manually generate certificates and create the Secrets yourself.

## What is that Loki multi tenancy?

Multi-tenancy means multiple organizations/tenants can use the same Loki instance with their data isolated from each other. Each tenant has an ID (the X-Scope-OrgID header).

For a single-user local lab you don't need it — auth_enabled: false disables it so Loki accepts requests without a tenant ID. That's the simpler approach for your setup.

## Do I need the Loki gateway?

No — you disabled it with gateway: enabled: false. Without the gateway, you access Loki directly via the singleBinary service. Keep it disabled.

## So now that I created the generic kubernetes secret for admin user in grafana, I need to create a grafana folder in charts with values?

No — Grafana is deployed by ArgoCD, not by manual helm install. The values go directly in the ArgoCD Application manifest (grafana.yaml) just like you did for Loki and Prometheus.

The charts/ folder is only for Traefik and ArgoCD which are bootstrapped manually.

## About promtail, is it the same as otel collector?

Similar purpose but different scope:

Promtail — specifically collects logs from Kubernetes pod stdout/stderr and ships them to Loki. Log-only.
OTel Collector — collects logs, metrics, and traces from multiple sources and can forward to multiple backends (Loki, Prometheus, Tempo, etc.)

OTel Collector is more powerful and flexible — it's the better choice for your stack since you already have it in the plan. With OTel Collector you can skip Promtail entirely and have one agent handling everything.
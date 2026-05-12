Without an IngressRoute, Traefik is running but has no rules — it doesn't know what to do with incoming requests. It's like a router with no routing table.

The IngressRoute tells Traefik:

When a request comes in matching Host(dashboard.localhost) on the web entrypoint
Send it to api@internal — which is Traefik's own internal dashboard service

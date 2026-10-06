# AnyGroupLLC Catalogue Microservice

Flask/Gunicorn service for a bounded Strangler Fig architecture prototype. It uses synthetic DynamoDB metadata and private S3 images; it does not migrate production Oracle data or implement checkout.

| Endpoint | Meaning |
|---|---|
| `GET /catalogue/health` | Process liveness and `APP_VERSION`; intentionally independent of data-service health |
| `GET /catalogue/ready` | DynamoDB read and S3 prefix-list access; 503 if a dependency is unavailable |
| `GET /catalogue/products` | Complete paginated table scan for the tiny pilot; sorted JSON-safe results |
| `GET /catalogue/products/<product_id>` | Product metadata; 404 if missing |
| `GET /catalogue/products/<product_id>/image-url` | Check the object, then return a 300-second HTTPS signed URL; 404 for missing data, 503 for storage access/service failures |

Environment: `CATALOGUE_TABLE`, `IMAGE_BUCKET`, `APP_VERSION` and the standard ECS region/credential environment. The task role supplies temporary AWS credentials. No keys belong in the source/image. Docker runs as user 10001 and builds for `linux/amd64`, matching X86_64 Fargate.

An empty but accessible table/bucket can pass readiness. The smoke test separately verifies seeded products and actual signed/unsigned image requests. ALB liveness remains separate to avoid restarting all containers during a shared data-service outage; functional failures surface through endpoint tests and ALB error monitoring.

Image tags are immutable; activation pins a verified digest. Build a new tag for changed source and retain a known-good image for reversal. An ECS circuit breaker is configured but its triggered rollback is unverified until tested after a successful baseline.

A full scan is acceptable only for this tiny prototype. Production requires bounded query/index/API pagination, validated data ownership/synchronisation, scoped roles, TLS, access/audit controls and measured sizing. Signed URLs grant temporary bearer access, not user authentication. Do not publish their query strings in evidence.

See `../IaC_Deployment_and_Usage_Instructions.md` for lab testing and `../tests/test_catalogue.py` for offline mocked regressions.

# AnyGroupLLC Catalogue Microservice

Small Flask/Gunicorn API used for the INFOSYS 735 Group Project 2 Strangler Fig pilot.

## Endpoints

- `GET /catalogue/health`
- `GET /catalogue/products`
- `GET /catalogue/products/<product_id>`
- `GET /catalogue/products/<product_id>/image-url`

The service reads catalogue metadata from DynamoDB and uses the `image_key` field to validate/generate a short-lived S3 presigned URL.

Environment variables are supplied by the ECS task definition:

- `CATALOGUE_TABLE`
- `IMAGE_BUCKET`

Do not place AWS access keys in the image. Fargate receives AWS credentials from the ECS task role.

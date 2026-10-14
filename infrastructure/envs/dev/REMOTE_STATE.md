# Terraform Remote State Bootstrap

## Current status

The S3 backend configuration is a template only. No remote state bucket
has been created, and no migration from local state has been performed.

## Prerequisites

Before enabling the backend:

1. Confirm an AWS region approved by the account owner.
2. Confirm the execution role has the required S3 permissions.
3. Provision a dedicated state bucket with S3 Block Public Access enabled.
4. Enable bucket versioning and server-side encryption.
5. Restrict bucket access to authorized Terraform operators and automation.
6. Permit Terraform S3 lockfile operations for the environment state key.
7. Confirm the bucket is not used for application data.

## Enablement

1. Copy `backend.hcl.example` to `backend.hcl`.
2. Replace the placeholder bucket and region with approved values.
3. Keep `backend.hcl` out of version control.
4. Add an S3 backend block to the dev root module.
5. Initialize the backend only after the bucket and permissions are verified.
6. If local state already contains resources, review and back it up before
   considering `terraform init -migrate-state`.

Never commit Terraform state, credentials, or the populated backend file.

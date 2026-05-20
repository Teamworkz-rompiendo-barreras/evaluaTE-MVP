# Deployment scripts

## Frontend deployment token

`deploy-frontend.sh` requires a Static Web Apps deployment token at runtime. The
secret **must not** be committed to the repository. Operators have two options:

1. Export the token before running the script (recommended for CI/CD):

   ```bash
   export DEPLOYMENT_TOKEN="$(az staticwebapp secrets list \
     --name evaluador-frontend-fzbhemgtetfeeme6 \
     --resource-group evaluador-frontend-fzbhemgtetfeeme6_group \
     --query properties.apiKey \
     -o tsv)"
   ./scripts/deploy/deploy-frontend.sh
   ```

   Store the token in a secure location such as Azure Key Vault or your CI
   secret store and inject it as the `DEPLOYMENT_TOKEN` environment variable
   during deployment jobs.

2. Allow the script to fetch the token automatically. If `DEPLOYMENT_TOKEN` is
   unset, the script attempts to call `az staticwebapp secrets list` using the
   logged-in Azure CLI session. Ensure your operator identity has permissions to
   read the deployment secret.

After rotating the token in Azure, update the external secret source (Key Vault,
GitHub Actions secret, etc.) and rerun the deployment. Removing the token from
this repository's history requires rewriting the Git history (for example with
`git filter-repo`); ensure this cleanup is performed outside of the deployment
process and force-push the sanitized history if you maintain a shared remote.

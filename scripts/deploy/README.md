# Deployment scripts

## Frontend deployment token

`deploy-frontend.sh` requires a Static Web Apps deployment token at runtime. The
secret **must not** be committed to the repository. Operators have two options:

1. Export the token before running the script (recommended for CI/CD):

   ```bash
   export DEPLOYMENT_TOKEN="$(az staticwebapp secrets list \
     --name evaluador-web \
     --resource-group evaluador-web_group \
     --query properties.apiKey \
     -o tsv)"
   ./scripts/deploy/deploy-frontend.sh
   ```

   Store the token in a secure location such as Azure Key Vault or your CI
   secret store and inject it as the `DEPLOYMENT_TOKEN` environment variable
   during deployment jobs. The script also recognises the standard
   `AZURE_STATIC_WEB_APPS_API_TOKEN` variable used by GitHub Actions—set either
   variable (but not both) and the deployment will proceed without invoking the
   Azure CLI secret lookup.

2. Allow the script to fetch the token automatically. If neither
   `DEPLOYMENT_TOKEN` nor `AZURE_STATIC_WEB_APPS_API_TOKEN` are present, the
   script attempts to call `az staticwebapp secrets list` using the logged-in
   Azure CLI session. Ensure your operator identity has permissions to read the
   deployment secret.

In both scenarios the deployment still requires the Azure CLI to obtain a
management access token and to resolve the Static Web App hostname. Run
`az login` (service principal or managed identity) before launching the script.

After rotating the token in Azure, update the external secret source (Key Vault,
GitHub Actions secret, etc.) and rerun the deployment. Removing the token from
this repository's history requires rewriting the Git history (for example with
`git filter-repo`); ensure this cleanup is performed outside of the deployment
process and force-push the sanitised history if you maintain a shared remote.

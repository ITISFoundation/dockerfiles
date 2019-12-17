# OpenAPI CLI toolkit

Node-based container with
- [Swagger/OpenAPI cli tool](https://www.npmjs.com/package/swagger-cli).
-

## Usage

```sh
docker pull itisfoundation/openapi-kit
docker run -v /local/path/to/folderWhereMyYamlFileExists:/spec itisfoundation/openapi-kit validate /api/spec/openapi.yaml
```


Based in https://github.com/kelvintaywl/swagger-cli-docker
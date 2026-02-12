# Authorisation Proxy Example
This example demonstrates Fine-Grained Authorisation (FGA) using a reverse proxy in front of a TAMS API instance, by matching user group membership to an `auth_classes` tag on Sources, Flows and Webhooks.
For a more complete discussion of FGA, see [AppNote 0016 Authorisation in TAMS Workflows](../../docs/appnotes/0016-authorisation-in-tams-workflows.md).

> [!IMPORTANT]
> This is intended as a proof-of-concept demo and a starting point.
See the [Limitations](#limitations) section for further details on security, feature, and performance compromises.

## How it works
The proxy receives requests from your client with the JSON Web Token (JWT) access token in the headers.
A JWT is a base64 encoded signed block of JSON containing claims about the user of the token (the "Bearer"), such as their identity or group membership.
Using the JSON Web Key Sets (JWKS) endpoint for the token, the proxy can check the authenticity of that token, using the provided public key to confirm the signature was constructed using the authorisation server's private key, however the token can be decoded and the claims read without any secret material.

Having read the token, the proxy extracts the user's groups, then makes a request to the upstream TAMS API to decide whether to allow the incoming request, by comparing the user's groups with the Resource(s) `auth_classes` tag.
Finally if the request is allowed, it makes the request and returns the response to the original client.
Requests to the upstream TAMS API use the the user's token.

## How to use it

### Pre-requisites
- A deployed copy of the TAMS API - this demo was tested against the [AWS implementation](https://github.com/awslabs/time-addressable-media-store).
- A user login method that issues a JWT access token containing the user's groups (such as AWS Cognito or Keycloak)
- A way to validate that JWT - e.g. a JWKS endpoint

> [!CAUTION]
> Making requests with the user's token instead of separate credentials means user can bypass the proxy and go directly to the upstream API with no authorisation rules, if that upstream Service is accessible on the user's network.
> This is a requirement of using their token, in order for the proxy to use it to get tags and make authorisation decisions.

### Usage as a Proxy

The proxy logic is implemented into a [Sanic](https://github.com/sanic-org/sanic) app.
To run the proxy, set the following environment variables and start the proxy:

```bash
export API_URL=<TAMS API URL>
export JWKS_URL=<JWKS Endpoint>
export GROUP_CLAIM=groups
make run
```

Note: `GROUP_CLAIM` does not need to be set when using Cognito. An appropriate default is set.

If you visit http://127.0.0.1:8000 with a valid access token (against the provided JWKS URL) you will be granted access based on your user groups.

When using the [AWS TAMS Tools UI](https://github.com/aws-samples/time-addressable-media-store-tools/tree/main/frontend), set up your `env.local` file with `VITE_APP_AWS_API_ENDPOINT=http://127.0.0.1:8000` for example.

## Resource Permissions

This example implements the fine-grained authorization logic described in [AppNote0016](../../docs/appnotes/0016-authorisation-in-tams-workflows.md#finer-grained-authorisation) using [tags](../../docs/appnotes/0016-authorisation-in-tams-workflows.md#implementation-using-tags) to manage base permissions.

In general this implementation reads the list of groups in the request, and only grants access to resources that have a corresponding `auth_classes` tag entry.
For demonstration purposes, basic logic has been provided that grants read, write, and delete permissions where matching classes end with `read`, `write`, and `delete` respectively.
i.e. a request that claims the `news_write` group will have write permissions against resources that have `news_write` in the `auth_classes` list.
A request that claims the `admin` group will be granted admin permissions.
This logic exists in the [`resources.py`](./resources.py) file and may be replaced with different/more complex logic as required.

## Limitations

> [!WARNING]
> This implementation is deliberately simple to serve as a starting point
> It comes with some notable, and potentially dangerous, limitations

- This example implementation re-uses the client's token for upstream requests to the Store service
    - If the user can make requests to the Store directly, they can bypass this auth proxy entirely
    - The correct approach would be for the proxy to possess its own client ID and secret, and make requests to the upstream API using the Client Credentials Grant
    - The auth proxy would separately authenticate users by whatever mechanism generates tokens, however their user tokens would not have access to the upstream API
    - Alternatively a network level solution could be applied, where the upstream API is not available to users other than the proxy itself
- This example implementation has not been fully security tested/hardened
    - It only exists to provide documentation as code for how fine-grained auth may be implemented
    - It WILL NOT be supported for production use cases
- Webhook permission are evaluated on registration/update of configuration only
    - Changes in permissions after registration/update will not be picked up
    - New resources created after registration/update of the webhook which match the configuration will not be picked up
    - Wildcard webhooks (i.e. those which consume all resources of a given type) are only available to admins
- This example implementation assumes API-wide read/write/delete permissions are implemented in the upstream Store implementation
    - The exception is admin permissions which result in a pass-through behaviour in this auth proxy
- This example implementation is reliant on the Groups OIDC claim
    - Many auth providers do not support Groups on machine users
- This example implementation may return empty lists in listings before the final page
    - This will happen where all items in a page are filtered out
    - A more complete implementation may recurse to the next page in this case
- This example implementation is designed to be readable, not performant
    - In many cases, it will make multiple requests to the Service where one would suffice

See [CONTRIBUTING.md](../../CONTRIBUTING.md) should you wish to improve on these!

## Tests

Tests can be run with the following command.

```bash
make lint typecheck
```

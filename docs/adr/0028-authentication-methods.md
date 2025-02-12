---
status: "proposed"
---
# Authentication Methods in TAMS

## Context and Problem Statement

Media workflows often contain sensitive or high-value content, and require a security model to restrict access; particularly important in a cloud-based environment, where approaches taken in the past (for example restricting physical access to facilities and sensitive areas) are restrictive and impractical.
Security is a complex topic, and general IT security (such as building secure cloud services and managing endpoints) is well covered in existing literature.
However, new cloud-based media workflows and the products and services that support them inevitably need to consider authentication and authorisation approaches.

Authentication in this context is the process of verifying the identity of a client of the TAMS API, and authorisation is the system by which rules (such as which users can access and modify content) are applied to those identities.
For clients and store implementations to interoperate, they must agree an authentication mechanism for the client to send suitable credentials with requests.
The authentication mechanism forms part of the specification, because clients and servers must both implement it correctly, and it should be possible to "mix-and-match" client and server implementations.
This ADR will propose changes to the specification to make that clear.

Conversely, authorisation is largely a consideration for the TAMS server implementation (and the wider system in which it exists), and implementers are more free to define how that works.
This could take the form of using some of the flexibility built into TAMS such as tags (with care taken to prevent tags being edited in a way that bypasses the rules).
Or it could be implemented using a separate API and interface to manage access to content, for example as part of a larger MAM system.
A future Application Note will discuss some options.

## Decision Drivers

* Clients should ideally implement all the authentication methods in the spec, to allow compatibility with the largest number of store implementations.
* Some clients will be browsers with a full user-interface operated by a human user.
  Some, however, will not.
  The approach should support both.
* Some server implementations will be in public cloud environments, however some may be in "edge" environments (such as inside a playout server), so an option that can be deployed in those environments is preferable.
* Secure management of credentials is challenging, and it should be possible to mitigate the risk of key loss or exfiltration where it cannot be secured effectively.
* Each additional option creates more implementation burden for clients, so fewer options would be better.

## Considered Options

* Option 1: Use Bearer tokens
* Option 2: Use tokens in URLs
* Option 3: HTTP Basic Auth
* Option 4: Mutual TLS (mTLS)
* Option 5: No auth

## Decision Outcome

Chosen option: Options 1, 2 and 3.

A broad ecosystem of tools exist to issue and validate cryptographically secure Bearer tokens, for example generating JSON Web Tokens (JWTs) as a result of an OAuth2 grant.
Clients could utilise this by acquiring the token using one of the OAuth2 grant types to interface with the TAMS instance owner's authorisation server, allowing existing systems, such as an existing Single Sign On (SSO) provider, to be used.
In addition Bearer tokens need not be JWTs: they are an opaque string understood by the server, with suitable protections against malicious modification by a client.
As a result, specifying the use of Bearer tokens enables significant flexibility for store implementations and the organisations that deploy them, while constraining complexity posed to clients.

A token can also be inserted into a URL directly for more lightweight integrations: effectively a TAMS [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).
This allows for very fine-grained access to a limited subset of resources, and for a simple integration model for clients that do not need the ability to issue and manage their own tokens.

In addition, Option 3 (HTTP Basic Auth) is selected to simplify the implementation in more constrained environments, such as in the field (e.g. an OB truck), proof-of-concept developments or where auth is being handled another way (e.g. a local proxy provides access to a cloud store only for users of that device).

### Implementation

Implemented by <https://github.com/bbc/tams/pull/113>.

## Pros and Cons of the Options

### Option 1: Use Bearer tokens

Bearer tokens are an HTTP authentication method in which a string token is included with requests that indicates the identity and/or access rights of the client, and that anyone in possession of the token (the "bearer") can claim to have that identity/those access rights.
They are formally defined in [RFC6750](https://datatracker.ietf.org/doc/html/rfc6750).

> [!NOTE]
> Intercepting the token in an HTTP request would provide access to an attacker, however in general TLS should be in use between the client and TAMS server to prevent that.

Generally the token is a [JSON Web Token (JWT)](https://www.rfc-editor.org/rfc/rfc7519.html#section-3) encoding the identity of the subject to which it is issued, the window of time for which it is valid, and a number of other "claims" such as their permissions.
JWTs are issued by an Authorisation Server, which will take steps to identify the user requesting the token (e.g. using a single sign-on system) and confirm they are permitted the access they have requested.
The Authorisation Server will then generate a token payload and cryptographically sign it using it's own private key.
As a result, the issuer's public key can be used to validate that the token has not been modified, a key property of Bearer tokens.

The token is supplied in an `Authorization` HTTP header when making a request, such as:

```http
GET /flows
Authorization: Bearer <encoded JWT>
```

The server (e.g. a TAMS instance) can decode that token, and either ask the Authorisation Server to validate it online, or use the Authorisation Server's public key to validate the signature offline.
It can then decide based on the claims in the token, whether to allow the request.

To acquire a token, one of the OAuth2 grants is used: either the Authorisation Code grant in which a client directs the user to an authorisation server (e.g. by opening a login page) and then passes back a code to acquire the JWT.
Alternatively the Client Credentials grant allows a client to request an access token using it's own credentials: for use cases such as machine to machine authentication.

* Good, because Bearer tokens are a standard approach used in HTTP-based APIs
* Good, because they pass transparently through reverse proxies and similar without additional config
* Good, because Bearer tokens can be validated offline, without necessitating per-request load on a central authorisation server
* Good, because Bearer tokens can also store the user's permissions (e.g. as Claims), again avoiding a central database lookup
* Neutral, because clients need to acquire tokens somehow and this can be complex
* Bad, because possession of the token confers access, so the possibility of leaked tokens must be managed through expiry times, least-privilege permissions and revocation

### Option 2: Use tokens in URLs

A token could be provided as a query string parameter in the URL for a request (this may also be called an "API key"), for example:

```http
GET /flows?access_token=<encoded token>
```

> [!NOTE]
> Intercepting the URL in an HTTP request would provide access to an attacker, however in general TLS should be in use between the client and TAMS server to prevent that.

This could be issued to the client as the URL of the TAMS interface (e.g. `https://media.example.com/tams?access_token=<encoded_token>`) and clients then have to attach that token to each subsequent request.
This token could be an encoded JWT, or another opaque token understood either by the TAMS server, or by an authorisation server which will validate requests.
If a JWT (or other suitable cryptographic token) is used, that verification can also be performed offline, or cached for a period of time.

For example a MAM might issue a short-lived token that grants access to only a limited selection of Flows in its TAMS interface: e.g. granting read access to Sources A and B, and write to Flow C for 8 hours (either by encoding those permissions into a JWT, or creating it's own opaque Bearer token).
This could be passed to a system such as a SaaS NLE operated by a third party.
The user is then able to run an edit session with access only to the material they selected in the MAM.

However care must be taken to balance the duration of the token, to account for the possibility of it expiring while the user is working, balanced against the risk of exposing a long-lived token.
Using an online verification approach (where the authorisation server checks the token every time) along with long-lived tokens which are revoked at the end of the session may help with this.

_Pros and Cons are broadly the same as Option 1, however "Neutral, because clients need to acquire tokens somehow and this can be complex" is partially mitigated.

* Good, because it creates a less prescriptive mechanism to integrate and acquire tokens for clients than Option 1
* Bad, because there's no obvious way to refresh the token after initial issue, so expiry must be carefully managed
* Bad, because tokens in URLs are more likely to be leaked since URLs are not generally held to be sensitive

### Option 3: HTTP Basic Auth

In HTTP Basic Authentication (as described by [RFC7617](https://datatracker.ietf.org/doc/html/rfc7617)) clients construct an `Authorization` header by combining a username and password and then encoding it, typically using base64 encoding.
The resulting request takes the form:

```http
GET /flows
Authorization: Basic <base64encode(username + ":" + password)>
```

The server compares the given password against their records (which may be hashed to avoid storing passwords in the clear) and if the credentials match, allows the request.

> [!NOTE]
> Intercepting the request would provide the user's password to an attacker, however in general TLS should be in use between the client and TAMS server to prevent that.

* Good, because HTTP Basic auth is well supported in HTTP client libraries, along with in server and edge proxy software
* Good, because a list of usernames and passwords for Basic auth is also easy to set up, even in constrained environments
* Bad, because central management of users and their access is very difficult
* Bad, because it passes the user's (long-lived) password around and exposes it to more risk than a dedicated auth server would

### Option 4: Mutual TLS (mTLS)

Mutual TLS (mTLS) extends the typical usage of Transport Layer Security (TLS) for verifying the identity of servers when establishing secure connections, to also verify the identity of the client.
When using mTLS, after verifying the server's certificate in the TLS handshake the client sends its own certificate, which the server verifies and uses to identify the client.
Typically the client's certificate is issued by a private Certificate Authority (CA), such as one managed by a company (unlike a server certificate, which is likely to be issued by a publicly-trusted CA).

TAMS could offer mTLS as an authentication option, in which clients are expected to provide a certificate with a suitable Common Name that a server can validate in order to grant access.

* Good, because mTLS can be verified offline using the CA's public key, without requiring per-request load on a central authorisation server
* Neutral, because mTLS support tends to be less common in client HTTP libraries, although this is improving
* Bad, because it restricts the insertion of HTTP middleware (caches, load balancers, reverse proxies etc.) because a direct TLS connection must be established with the server
* Bad, because revocation of certificates tends to be poorly supported in implementations

### Option 5: No auth

The existing TAMS API specification allows for requests to be unauthenticated, on the assumption that this is only used for development/testing scenarios, or in cases where the only parties with API access are intrinsically trusted (e.g. on localhost).

* Good, because it allows a very simple approach for development/testing
* Neutral, because removing it may be a breaking change
* Bad, because it encourages implementers to ignore auth entirely, creating a security risk down the line
* Bad, because it is relatively easy to accidentally expose an endpointer more widely than intended

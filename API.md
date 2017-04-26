
# Blenderfarm server-client API, v1

All communications are done via HTTP. Responses are sent as JSON.

## Response format

The JSON response will always contain a `status` key; if the action
was successful, the value will be `"ok"`; if there were errors, the
value will be `"error"`.

If `status` is `"error"`, a machine-readable error code will be
returned in `"code"`, and a user-facing error message will be returned
in `message`. Optionally, the context will be returned in `context`;
this will be, for example, the username during a failed authentication.

```json
{
  "status": "error",
  "code": "too-many-teapots",
  "message": "Too many concurrent teapots",
  "context": "42"
}
```

### Status codes

The status code for all valid requests must be `200`; invalid or
malformed requests must use `400`; and if the endpoint does not exist,
`404`. `500` will be sent in the case of a server error. Valid
requests, including those which generate errors (such as failed
authentication), must use code `200`.

#### Generic Errors

* `invalid-user` if the user does not exist
* `invalid-key` if the key does not match
* `expired-request` if the time window for the request has expired

## Authentication

Authentication is done via HMAC. Paths requiring authentication must
include three additional URL parameters; `user`, `digest`, and `time`.

* `user` is the name of the authenticating user.
* `digest` is the HMAC digest of the request data.
* `time` is the timestamp of the request. The value itself must be the
  fractional epoch time; if `time` is too far in the past, the server
  may reject the request to avoid replay attacks. The exact window
  will not be specified, but it should be greater than 10 seconds and
  less than 1-2 minutes.

The digest plaintext must start with the magic string
"BLENDERFARM". The keys are sorted alphabetically.

Data (keys and values) are stored in the format
`key:value\nkey:value\nkey:value...key:value`. Both `key` and `value`
are the values after stringification, to avoid floating-point
reproducibility issues.

Obviously, the `digest` is added to the URL parameters list after it's
been computed.

## Endpoints

All endpoints must be preceded by `v1`; for example, `/v1/info.json`.

### GET `info.json`

Returns server info:

```json
{
  "status": "ok",
  "server_version": "0.1.0",
  "server_uptime": 30
}

```

* `server_version` is the version of Blenderfarm running on the server.
* `server_uptime` is the number of fractional seconds the Blenderfarm server has been running.

This endpoint does _not_ require authentication.

### POST `session/verify.json`

Requests the creation of a new session token. The username and key
must be sent as `POST` parameters named `user` and `key`,
respectively.

```json
{
  "status": "ok",
  "token": "abcdefghijklmnopqrstuvwxyz0123456789",
  "expires-in": 86400
}

```

* `token` is the token, unique to this particular session.
* `expires-in` is the number of seconds in which the token will become
  invalid. The client must request a new token before this many
  seconds have passed, or any further requests requiring
  authentication will fail.

This endpoint does _not_ require authentication.

#### Errors

* `no-user` if there's no such `user` (`context` will be the relevant username)
* `bad-key` if there's no such `key` for the `user` (`context` will be the relevant username)

### POST `session/end.json`

Requests the destruction of a session token. The session token to be
ended must be sent as a `POST` parameter named `token`. Upon success,
any further transactions using that particular session token will
fail.

```json
{
  "status": "ok"
}

```

#### Errors

* `bad-token` if there's no such `token`


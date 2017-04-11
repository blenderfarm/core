
# Blenderfarm server-client API, v1

All communications are done via HTTP. Authentication is performed with
HTTP Basic Authentication; responses are sent as JSON.

All endpoints require a username/password (key) combination with HTTP
Basic Authentication unless otherwise specified.

## Response format

The JSON response will always contain a `status` key; if the action
was successful, the value will be `"ok"`; if there were errors, the
value will be `"error"`.

If `status` is `"error"`, a machine-readable error code will be
returned in `"code"`, and auser-facing error message will be returned
in `message`.

```json
{
  "status": "error",
  "code": "too-many-teapots",
  "message": "Too many concurrent teapots"
}
```

### Status codes

The status code for all valid requests must be `200`; invalid requests
must use `400`; and if the endpoint does not exist, `404`.

## Parameters



## Endpoints

### `/v1/info.json`

Returns server info:

```json
{
  "status": "ok",
  "server_version": "0.1.0",
  "server_uptime": 30
}

```

* `server_version` is the version of Blenderfarm running on the server.
* `server_uptime` is the number of seconds the Blenderfarm server has been running.

This endpoint does _not_ require authentication.

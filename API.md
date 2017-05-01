
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

### POST `auth/test.json`

Simply an endpoint that requires authentication, to verify the
user/key combination.

```json
{
  "status": "ok"
}

```

### GET `task/next.json`

Returns the next task to be performed.

```json
{
  "status": "ok",
  "task": {
    "task_id": "nrOn23gtBPlUGgRBXxnl6yCi5P7SIUx9",
    "job": {
      "job_id": "hzjtBPlUGgRBXxnrOn23gl6yCi5P7SWZ",
      "file_url"
    }
    "task_info_type": "render",
    "task_info": {
      "resolution": [1920, 1080],
      "frame": 0
    }
  }
}

```

* `task` is a `Task` JSON object, or `null` if all tasks are complete (yay!)

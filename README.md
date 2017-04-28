
# Blenderfarm

Distributed Blender renderfarm software. There are no "official"
servers; you must host your own server and render nodes.

# Important notes

This is alpha software, and backwards compatibility is *not* expected
at this point. Do not use this in any production system (obviously).

# Usage

Run `bf.py`. If you start a server, databases will be created in the
directory you're currently in.

To start a blenderfarm server, run `bf.py server`. If you're stuck,
use `bf.py help`.

# Terminology

#### Server

The Blenderfarm server. This does no real work other than accept new
`Job`s from clients and divvy them up into `Task`s to send to render
nodes.

#### Client

Something that connects to the `server`. It might upload new `job`s;
it might perform `task`s; or it might do both.

#### Node

Performs the actual work, one `task` at a time.

#### Job

A single "thing", such as a single still image or an animation. The
server will attempt to break a single `job` into multiple `task`s;
for example, an animation can be rendered by multiple clients, one for
each frame.

#### Task

A single, atomic operation. Clients are given one task at a time,
along with all the necessary data (such as `.blend` files); they
execute the task, then upload the finished data to the server.

## Example

A user uploads a new `.blend` file, a 30-frame animation, using
`blenderfarm-web-server`. The server sees that it's an animation and
creates 30 tasks. As soon as a client implementing `node` requests a
new task, the server sends a frame render task, along with all the
necessary data. Each render node then renders its own frame, then
uploads the resulting frame to the server. When all the tasks are
complete, the job is marked as complete and the client is notified.


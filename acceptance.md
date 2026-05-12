# Acceptance Criteria

## Task 1: Core web application with routing and request/response

### Acceptance Criteria
- [x] Users can create an app instance with a name: `app = Sanic("myapp")`
- [x] Users can register GET routes with `@app.get("/path")` decorator
- [x] Users can register POST routes with `@app.post("/path")` decorator
- [x] Users can register PUT routes with `@app.put("/path")` decorator
- [x] Users can register DELETE routes with `@app.delete("/path")` decorator
- [x] Users can register PATCH routes with `@app.patch("/path")` decorator
- [x] Users can register HEAD routes with `@app.head("/path")` decorator
- [x] Users can register OPTIONS routes with `@app.options("/path")` decorator
- [x] Users can register routes with multiple methods via `@app.route("/path", methods=["GET", "POST"])`
- [x] Path parameters are extracted: `@app.get("/users/<user_id>")` passes user_id to handler
- [x] Path parameters support type conversion: `<user_id:int>` converts to integer
- [x] Path parameters support float type: `<value:float>` converts to float
- [x] Path parameters default to string type
- [x] Handlers receive a Request object with method, path, headers, and body
- [x] Request object provides parsed query string via `request.args`
- [x] Request object provides parsed JSON body via `request.json`
- [x] `json({"key": "value"})` returns a JSON response with content-type application/json
- [x] `text("hello")` returns a text response with content-type text/plain
- [x] `html("<h1>Hi</h1>")` returns an HTML response with content-type text/html
- [x] `raw(b"bytes")` returns a raw bytes response
- [x] `redirect("/other")` returns a 302 redirect response
- [x] `empty()` returns a 204 no-content response
- [x] Custom status codes can be set on responses: `json(data, status=201)`
- [x] Custom headers can be set on responses: `json(data, headers={"X-Custom": "val"})`
- [x] A test client can make GET, POST, PUT, DELETE, PATCH requests against the app
- [x] The test client returns status code, headers, and body from responses
- [x] Requesting an unregistered route returns 404
- [x] Using wrong HTTP method on a route returns 405

## Task 2: Middleware support

### Acceptance Criteria
- [ ] Users can register request middleware using @app.middleware("request")
- [ ] Users can register response middleware using @app.middleware("response")
- [ ] @app.on_request is a shortcut for request middleware
- [ ] @app.on_response is a shortcut for response middleware
- [ ] Request middleware receives the request object
- [ ] Response middleware receives both request and response objects
- [ ] Request middleware can short-circuit by returning a response (skips handler)
- [ ] Response middleware can modify or replace the response
- [ ] Multiple middleware execute in registration order for request middleware
- [ ] Response middleware executes in reverse registration order
- [ ] Priority parameter controls middleware ordering (higher priority runs first for request)
- [ ] Middleware can be async functions
- [ ] Request middleware returning None continues to next middleware/handler

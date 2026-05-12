# Acceptance Criteria

## Task 1: Core web application with routing and request/response

### Acceptance Criteria
- [ ] Users can create an app instance with a name: `app = Sanic("myapp")`
- [ ] Users can register GET routes with `@app.get("/path")` decorator
- [ ] Users can register POST routes with `@app.post("/path")` decorator
- [ ] Users can register PUT routes with `@app.put("/path")` decorator
- [ ] Users can register DELETE routes with `@app.delete("/path")` decorator
- [ ] Users can register PATCH routes with `@app.patch("/path")` decorator
- [ ] Users can register HEAD routes with `@app.head("/path")` decorator
- [ ] Users can register OPTIONS routes with `@app.options("/path")` decorator
- [ ] Users can register routes with multiple methods via `@app.route("/path", methods=["GET", "POST"])`
- [ ] Path parameters are extracted: `@app.get("/users/<user_id>")` passes user_id to handler
- [ ] Path parameters support type conversion: `<user_id:int>` converts to integer
- [ ] Path parameters support float type: `<value:float>` converts to float
- [ ] Path parameters default to string type
- [ ] Handlers receive a Request object with method, path, headers, and body
- [ ] Request object provides parsed query string via `request.args`
- [ ] Request object provides parsed JSON body via `request.json`
- [ ] `json({"key": "value"})` returns a JSON response with content-type application/json
- [ ] `text("hello")` returns a text response with content-type text/plain
- [ ] `html("<h1>Hi</h1>")` returns an HTML response with content-type text/html
- [ ] `raw(b"bytes")` returns a raw bytes response
- [ ] `redirect("/other")` returns a 302 redirect response
- [ ] `empty()` returns a 204 no-content response
- [ ] Custom status codes can be set on responses: `json(data, status=201)`
- [ ] Custom headers can be set on responses: `json(data, headers={"X-Custom": "val"})`
- [ ] A test client can make GET, POST, PUT, DELETE, PATCH requests against the app
- [ ] The test client returns status code, headers, and body from responses
- [ ] Requesting an unregistered route returns 404
- [ ] Using wrong HTTP method on a route returns 405

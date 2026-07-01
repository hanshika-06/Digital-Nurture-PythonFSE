# ==============================================================================
# HANDS-ON 01 - Task 1: Understand the Request-Response Cycle
# ==============================================================================

"""
1. GET /api/courses/ Journey Through a Django Application:
   --------------------------------------------------------
   [Client Browser]
          │ (HTTP GET request)
          ▼
   [WSGI / ASGI Web Server]
          │ (translates HTTP to python request object)
          ▼
   [URL Router (urls.py)]
          │ (matches '/api/courses/' to the target view function/class)
          ▼
   [Middlewares (Request phase)]
          │ (performs preprocessing e.g., security, sessions)
          ▼
   [View (views.py)]
          │ (executes business logic; calls ORM if data is needed)
          ▼
   [Model / Database (models.py / DB)]
          │ (executes SQL query to fetch course details and returns objects)
          ▼
   [View (views.py)]
          │ (serializes objects and constructs an HTTP Response)
          ▼
   [Middlewares (Response phase)]
          │ (post-processes response e.g., adding headers, cookies)
          ▼
   [WSGI / ASGI Web Server]
          │ (converts python response to raw HTTP response string)
          ▼
   [Client Browser] (renders the JSON response payload)


2. Middlewares in the Request-Response Cycle:
   ------------------------------------------
   - Middlewares sit between the web server's request handling and the views. They act as hooks
     executing before the view starts running (request phase) and after the view returns (response phase).
   
   Two built-in Django middlewares:
   a) 'django.middleware.security.SecurityMiddleware':
      Adds several security-enhancing HTTP response headers (e.g. X-Content-Type-Options, X-Frame-Options,
      SSL redirect checks) to protect against clickjacking, content sniffing, and enforce HTTPS.
   b) 'django.middleware.csrf.CsrfViewMiddleware':
      Protects the application against Cross-Site Request Forgeries (CSRF) by injecting and verifying
      cryptographic tokens in POST, PUT, and DELETE forms/requests.


3. WSGI vs ASGI:
   -------------
   - WSGI (Web Server Gateway Interface):
     * The traditional Python standard for synchronous web application servers.
     * Handles requests synchronously; one thread/process handles one request at a time.
     * Standard for traditional Django, but inefficient for long-lived connections (WebSockets, SSE).
   - ASGI (Asynchronous Server Gateway Interface):
     * The modern successor designed to support asynchronous capability.
     * Supports async call signatures, multi-request concurrency, WebSockets, and long polling.
     * By default, Django uses WSGI. You would switch to ASGI when integrating real-time communication 
       (e.g., Django Channels) or handling asynchronous requests directly in views.


4. MVC vs MVT Mapping:
   -------------------
   - MVC (Model-View-Controller) is mapped to Django's MVT (Model-View-Template) as follows:
     * Model (MVC) -> Model (MVT): Maps directly. Defines schema, fields, and DB logic.
     * View (MVC) -> Template (MVT): Defines the presentation layer (what the user sees, e.g. HTML/CSS).
     * Controller (MVC) -> View (MVT): Maps the business logic, URL routing, and handles request inputs 
       to produce responses.
"""

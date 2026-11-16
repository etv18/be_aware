Be Aware is a personal project which helps me to track my financial records on a monthly basis, keeping me post on my incomes and expenses and how my bank accounts's money fluctuate day to day depending on my cash flow.

Folder layout

backend/   the Flask app: JSON API under /api (app/, tests/, migrations/, requirements/, scripts/, run.py). Run flask, pytest and pip from here. Every path such as app/... or tests/... below is inside backend/.
frontend/  the React + TypeScript app (Vite, Tailwind). Run npm from here.

Installation

1. clone the repo
2. create a venv and activate it
3. go to /backend/requirements and run "pip install -r requirements.txt"
4. create a .env file (in /backend or in the project root). With the default APP_ENV (development) the app uses the MySQL settings of app/utils/db.py (DB_DRIVER, HOST, PORT, DATABASE, ...). For a quick local try-out without MySQL put these two lines in it: APP_ENV=testing and TEST_DATABASE_URL=sqlite:///be_aware_local.db
5. go to /backend and run "flask db upgrade" to create the tables (if the migrations folder is empty run "flask db init" and "flask db migrate" first)
6. run "flask seed-db" to create a login user (admin) and some demo records
7. go to /frontend, run "npm install" and then "npm run build"
8. go to /backend and run "flask run", then open http://127.0.0.1:5000

Working on the frontend

The frontend is React + TypeScript + Tailwind in /frontend. "npm run build" writes it into backend/app/static/app (not committed: build it after pulling), and Flask serves it at "/" (every URL that is not /api answers with its index.html).

1. development: run "flask run" (in /backend) in one terminal and "npm run dev" (in /frontend) in another, then open http://localhost:5173 (Vite sends /api to Flask, so login and CSRF work)
2. "npm test" runs the unit tests and "npm run typecheck" checks the types
3. the code is organised as src/pages (one file per page), src/components (layout, tables, forms, charts), src/lib (api, queries, formatting) and src/types (generated). See MAINTENANCE_GUIDE.md, section 4

How the code is organised (backend)

Request -> route -> controller -> service -> model, the same in every module:

- app/routes/<module>_routes.py says which URL goes to which controller function (the JSON of the module under /api).
- app/controllers/<module>_controller.py reads the request, validates the JSON body (app/controllers/schemas.py), calls the service and turns the result into JSON (app/controllers/serializers.py, checked against app/controllers/out.py). It holds no business rules.
- app/services/<module>_service.py holds the business rules. It takes plain arguments, returns model objects and knows nothing about Flask. Every operation that moves money runs inside one transaction (atomic()).

The API description (OpenAPI)

The API is described by an OpenAPI document that is generated from the code (the Pydantic models in app/controllers/schemas.py for requests and app/controllers/out.py for responses). In development and tests it is served at /api/openapi.json, with a page to try the endpoints at /api/docs.

- After changing an endpoint or a response model, run "npm run gen:api" in /frontend. It rewrites frontend/openapi.json and the TypeScript types in frontend/src/types/api.ts (never edit that file by hand). A test fails when the exported file is out of date.
- Endpoints that are not described yet are listed in NOT_TYPED_YET in backend/tests/test_openapi.py. Describe one (a model in out.py, "out=" in its route) and remove it from the list.

Environments

The APP_ENV variable picks the settings (see app/config.py):

- development (default): DEBUG on, MySQL using the DB_DRIVER, USERNAME, PASSWORD, HOST, PORT and DATABASE values from the .env file (app/utils/db.py).
- testing: used by pytest, in-memory SQLite. Set TEST_DATABASE_URL to a file (sqlite:///be_aware_local.db) to keep the data between commands.
- production: DEBUG off, the same MySQL settings. Set APP_ENV=production on the server.

Tests

1. run "pip install -r requirements/requirements-dev.txt"
2. from /backend run "pytest" (the React tests run with "npm test" in /frontend)

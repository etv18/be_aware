Be Aware is a personal project which helps me to track my financial records on a monthly basis, keeping me post on my incomes and expenses and how my bank accounts's money fluctuate day to day depending on my cash flow.

Installation

1. clone the repo
2. create a venv
3. activate the venv
4. go to /project/requirements
5. run "pip install -r requirements.txt"
6. go to /project
7. run "flask init-db" to create the local SQLite database (instance/be_aware_dev.db)
8. run "flask seed-db" to create a login user and some demo records
9. run this command "flask run"

Frontend (only needed when you change styles or icons)

The pages are plain ES modules in app/static/js, with no build step. The CSS (Tailwind) and the icon sprite are built from /frontend and the result is committed in app/static, so the app runs without Node.

1. go to /frontend and run "npm install"
2. "npm run build" rebuilds app/static/css/app.css and app/static/img/icons.svg ("npm run watch:css" while styling)
3. add an icon: put its Lucide name in ICONS in frontend/scripts/build-icons.mjs, then "npm run build:icons"

How the code is organised

Request -> route -> controller -> service -> model, the same in every module:

- app/routes/<module>_routes.py says which URL goes to which controller function (and serves the page of the module).
- app/controllers/<module>_controller.py reads the request, validates the JSON body (app/controllers/schemas.py), calls the service and turns the result into JSON (app/controllers/serializers.py). It holds no business rules.
- app/services/<module>_service.py holds the business rules. It takes plain arguments, returns model objects and knows nothing about Flask. Every operation that moves money runs inside one transaction (atomic()).

Every page is an empty shell (templates/page.html). Its script in app/static/js/pages calls the same controllers with JSON and draws the answer, so a new frontend (React, etc.) only needs to call the same endpoints. There is no separate API package.

- GET: simple values go in the URL (/expenses/12, /expenses?q=pizza&start=2026-10-01&end=2026-10-31, /stats/cash-flow?year=2026).
- POST and PUT: a JSON body that goes to the service (the fields are in app/controllers/schemas.py; created_at is optional and defaults to now).
- DELETE: the id in the URL.
- Each module has the same five endpoints: GET /expenses, POST /expenses, GET /expenses/<id>, PUT /expenses/<id>, DELETE /expenses/<id>. Modules: expenses, incomes, withdrawals, deposits, loans, debts, loan_payments, debt_payments, banktransfer, credit_card_payments, banks, bank_accounts, credit_cards, expense_categories. The ledgers (cashledger, bank_transaction_ledger, credit_card_ledger) are read only, except that POST /cashledger makes a manual cash adjustment and DELETE /cashledger/<id> removes one.
- Also: /loans/<id>/payments, /debts/<id>/payments, /bank_accounts/<id>/records, /credit_cards/<id>/records, /expense_categories/<id>/records, the reports (/stats/..., /bank_accounts/<id>/reports/..., ?year=), /dashboard and /options.
- Success: {"data": ...} (lists also have "meta"). Errors: {"error": {"code", "message", "fields"?}} with 400 (rejected by a business rule), 401, 404, 422 (invalid body) or 500.
- Login: POST /login with {"username", "password"}; GET /session returns the user and a CSRF token that has to come back in an X-CSRFToken header on POST, PUT and DELETE.

Environments

The APP_ENV variable picks the settings (see app/config.py):

- development (default): DEBUG on, SQLite file at instance/be_aware_dev.db. Set DEV_DATABASE_URL to use another database.
- testing: used by pytest, in-memory SQLite.
- production: DEBUG off, MySQL using the DB_DRIVER, USERNAME, PASSWORD, HOST, PORT and DATABASE values from the .env file. Set APP_ENV=production on the server.

Tests

1. run "pip install -r requirements/requirements-dev.txt"
2. from /project run "pytest"

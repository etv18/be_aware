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

The pages are plain HTML templates and ES modules in app/static/js, with no build step. The CSS (Tailwind) and the icon sprite are built from /frontend and the result is committed in app/static, so the app runs without Node. Run "npm run build:css" after adding a Tailwind class to a template or script.

1. go to /frontend and run "npm install"
2. "npm run build" rebuilds app/static/css/app.css and app/static/img/icons.svg ("npm run watch:css" while styling)
3. add an icon: put its Lucide name in ICONS in frontend/scripts/build-icons.mjs, then "npm run build:icons"

How the code is organised

Request -> route -> controller -> service -> model, the same in every module:

- app/routes/<module>_routes.py says which URL goes to which controller function (the page of the module at a plain URL, and its JSON under /api).
- app/controllers/<module>_controller.py reads the request, validates the JSON body (app/controllers/schemas.py), calls the service and turns the result into JSON (app/controllers/serializers.py). It holds no business rules.
- app/services/<module>_service.py holds the business rules. It takes plain arguments, returns model objects and knows nothing about Flask. Every operation that moves money runs inside one transaction (atomic()).

The frontend (every page is a real HTML file with its own script, and a few shared files):

- app/templates/<page>.html is the page: its real markup (table, form, figures). It extends layout.html (navbar, head, scripts) and reuses app/templates/partials/ui.html (macros: page_header, stat_row, table_card, row_actions, chart_card, form_dialog and the form fields) and partials/dialogs.html (forms used by more than one page).
- app/static/js/<page>.js is the only script of that page: it asks the controllers for JSON, fills the rows with textContent (so nothing a person typed can run as HTML) and reacts to clicks.
- app/static/js/common.js is the shared file: api() with CSRF, formatting, toasts, dialogs, form helpers, renderRows, and the two helpers that remove most of the repetition, bindList() (load, search, rows, edit/delete buttons) and recordForm() (a form in a dialog: new and edit). chart.js draws charts, forms.js has the forms several pages share (transfer, card payment, loan/debt payment) and records.js is the "one tab per kind of record" table of the detail pages.
- To change a column: edit the <thead> and the <template data-row-template> in the page's template and the cells() function in its script. To add a form field: add it in the template and in fromRecord() / toBody() of its script.
- A new frontend (React, etc.) only needs to call the same endpoints. There is no separate API package.

URLs. Pages live at plain URLs and the JSON lives under /api, always snake_case and plural:

- Pages: /expenses, /loans, /loans/12 (the page of one loan), /bank_accounts/3, /cash_ledger ... one list page per module and one page per record for bank_accounts, credit_cards, expense_categories, loans and debts. /login is the login form and / is home.
- GET: simple values go in the URL (/api/expenses/12, /api/expenses?q=pizza&start=2026-10-01&end=2026-10-31, /api/reports/cash_flow?year=2026).
- POST and PUT: a JSON body that goes to the service (the fields are in app/controllers/schemas.py; created_at is optional and defaults to now).
- DELETE: the id in the URL.
- Each module has the same five endpoints: GET /api/expenses, POST /api/expenses, GET /api/expenses/<id>, PUT /api/expenses/<id>, DELETE /api/expenses/<id>. Modules: expenses, incomes, withdrawals, deposits, loans, debts, loan_payments, debt_payments, bank_transfers, credit_card_payments, banks, bank_accounts, credit_cards, expense_categories. The ledgers (cash_ledger, bank_ledger, card_ledger) are read only, except that POST /api/cash_ledger makes a manual cash adjustment and DELETE /api/cash_ledger/<id> removes one.
- Also: /api/loans/<id>/payments, /api/debts/<id>/payments, /api/bank_accounts/<id>/records, /api/credit_cards/<id>/records, /api/expense_categories/<id>/records, the reports (/api/reports/... for the whole app, /api/bank_accounts/<id>/reports/..., /api/expense_categories/reports/monthly, ?year=), /api/dashboard and /api/options.
- Success: {"data": ...} (lists also have "meta"). Errors: {"error": {"code", "message", "fields"?}} with 400 (rejected by a business rule), 401, 404, 422 (invalid body) or 500.
- Login: POST /api/login with {"username", "password"}, POST /api/logout; GET /api/session returns the user and a CSRF token that has to come back in an X-CSRFToken header on POST, PUT and DELETE.
- Errors under /api are always JSON, even for a GET opened in the browser.

Environments

The APP_ENV variable picks the settings (see app/config.py):

- development (default): DEBUG on, SQLite file at instance/be_aware_dev.db. Set DEV_DATABASE_URL to use another database.
- testing: used by pytest, in-memory SQLite.
- production: DEBUG off, MySQL using the DB_DRIVER, USERNAME, PASSWORD, HOST, PORT and DATABASE values from the .env file. Set APP_ENV=production on the server.

Tests

1. run "pip install -r requirements/requirements-dev.txt"
2. from /project run "pytest"

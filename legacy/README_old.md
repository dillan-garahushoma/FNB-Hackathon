# Path2Work

Path2Work helps young people build credible skills profiles, discover relevant opportunities, and improve their work readiness.

## Run locally

1. Create and activate a virtual environment:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the application dependency:

   ```powershell
   py -3 -m pip install -r requirements.txt
   ```

3. Set a persistent secret key and start Flask:

   ```powershell
   $env:PATH2WORK_SECRET_KEY = py -3 -c "import secrets; print(secrets.token_hex(32))"
   py -3 app.py
   ```

   Open <http://127.0.0.1:5000>. The SQLite database is created in `instance\path2work.sqlite3`.

4. Run the tests:

   ```powershell
   py -3 -m unittest discover -s tests -v
   ```

Set `PATH2WORK_COOKIE_SECURE=1` when serving over HTTPS. Do not use the ephemeral development secret in a deployed environment.

## Routes

- `/` — public Path2Work landing page
- `/opportunities` — public directory (currently no listings are available)
- `/register` — local account creation
- `/signin` — sign in to an existing account

Passwords are validated on the server and stored only as Werkzeug password hashes. No external identity providers or opportunity feed are configured.

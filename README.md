# Employee Form → MySQL (Python / Flask)

A small web app: fill in Employee Name, ID, Salary, Designation and City, click **Save employee**, and the record is inserted into a MySQL table. Recently added employees are listed beside the form.

## Project layout

```
employee-form/
├── app.py            # Flask routes + server-side validation
├── db.py             # MySQL connection pool, insert/list queries
├── templates/form.html
├── schema.sql        # database, table, least-privilege app user
├── requirements.txt
└── .env.example      # DB credentials template
```

## Setup

1. **Create the database and table** (as a MySQL admin):

   ```bash
   mysql -u root -p < schema.sql
   ```

   Edit the `emp_app` password in `schema.sql` first.
2. **Install dependencies**:

   ```bash
   python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure credentials**:

   ```bash
   cp .env.example .env    # then edit DB_PASSWORD etc.
   ```

4. **Run**:

   ```bash
   python app.py
   ```

   Open <http://127.0.0.1:5000>

## Verify the data landed

```sql
SELECT * FROM employee_db.employees ORDER BY created_at DESC;
```

## Design notes

- **Parameterised queries** (`%s` placeholders) — no SQL injection.
- **Validation on the server**, not just the browser; bad input re-renders the form with messages.
- **Duplicate IDs** are caught via the `UNIQUE` constraint (MySQL error 1062) and shown on the ID field.
- **Salary** stored as `DECIMAL(12,2)` — never `FLOAT` for money.
- **Connection pool** instead of opening a connection per request.
- **Post/Redirect/Get** — refreshing after a save doesn't insert twice.
- Credentials come from `.env`; the app user only has `SELECT, INSERT`.

## Deploying on EC2

### 1. Launch the EC2 instance

- Launch an EC2 instance with an **Ubuntu** AMI.

- Security group inbound rules:

  | Type       | Port | Source                  | Purpose            |
  |------------|------|-------------------------|--------------------|
  | SSH        | 22   | My IP                   | Terminal access    |
  | Custom TCP | 5000 | My IP (or 0.0.0.0/0)    | Flask application  |

  > Do **not** open port 3306. MySQL is only reachable by the app over the private Docker network.

### 2. Install Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo systemctl status docker        # should show "active (running)"
```

Allow your user to run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker                       # apply the group change in the current session
docker ps                           # should work without sudo
```

### 3. Clone the repository

```bash
git clone https://github.com/SDET-Engineer19/flask-python-mysql-app.git
cd flask-python-mysql-app
```

All remaining commands must be run from this folder.

### 4. Create a Docker network

Both containers join this bridge network so the app can reach MySQL by its container name.

```bash
docker network create empnet
```

### 5. Start the MySQL container

```bash
docker run -d --name mysql --network empnet \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=employee_db \
  -e MYSQL_USER=emp_app \
  -e MYSQL_PASSWORD=change_me \
  -v mysql_data:/var/lib/mysql \
  -v "$(pwd)/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro" \
  mysql:8.0
```

- `mysql_data` is a named volume, so the data survives container restarts.
- `schema.sql` creates the `employees` table automatically on the **first** start only.
- No `-p` flag is used, so MySQL is not exposed outside the instance.

Wait until MySQL is ready:

```bash
docker logs -f mysql                # wait for "ready for connections", then press Ctrl+C
```

### 6. Build the application image

```bash
docker build -t flask-app .
```

### 7. Run the application container

```bash
docker run -d --name web-app --network empnet -p 5000:5000 \
  -e DB_HOST=mysql \
  -e DB_USER=emp_app \
  -e DB_PASSWORD=change_me \
  -e DB_NAME=employee_db \
  -e FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  flask-app

- `DB_HOST` is the **MySQL container name** (`mysql`), not `localhost`.
- `DB_PASSWORD` must match `MYSQL_PASSWORD` from step 5.
- `FLASK_SECRET_KEY` signs session cookies; a random value is generated here.

### 8. Verify

```bash
docker ps                           # both containers should be "Up"
docker logs web-app                 # should show "Running on all addresses (0.0.0.0)"
curl -I http://<EC2_PUBLIC_IP>:5000       # should return HTTP/1.1 200 OK
```

Open `http://<EC2_PUBLIC_IP>:5000` in the browser, submit the form, then confirm the record was saved:

```bash
docker exec -it mysql mysql -u emp_app -p employee_db -e "SELECT * FROM employees;"
```

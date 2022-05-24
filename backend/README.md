# Instalation

Clone repository and ``cd backend`` into backend folder.

### Setup
-------------------------------------------------------
Setup your db credentials in ``piccolo_conf.py``

```python
DB = PostgresEngine(
    config={
        "database": "your db name",
        "user": "your db username",
        "password": "your db password",
        "host": "localhost",
        "port": 5432,
    }
)
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Migrations

```bash
piccolo migrations forwards session_auth
piccolo migrations forwards user
piccolo migrations new home --auto
piccolo migrations forwards home
```

### Create admin user

```bash
piccolo user create
```

### Getting started 

```bash
python main.py
```
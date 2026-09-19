# Sofpia

## Frontend

```bash
cd frontend
npm install
ng serve
```

Angular aplikacija je dostupna na <http://localhost:4200>.

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Flask API je dostupan na <http://localhost:5000>, a provera rada na <http://localhost:5000/api/health>.

## SQLite

Nije potrebna instalacija ili ručno kreiranje baze. Flask pri prvom pokretanju automatski pravi `backend/instance/library.db`, admin nalog i 5 knjiga.

Admin nalog za testiranje:

```text
username: admin
password: admin123
```

SQL struktura i seed primer nalaze se u `backend/schema.sql` i `backend/seed.sql`.

## Docker

Potrebni su samo Docker i Docker Compose. Iz root foldera projekta pokreni:

```bash
docker compose up --build
```

Aplikacija je dostupna na <http://localhost:4200>, a backend na <http://localhost:5000/api/health>.
SQLite baza i uploadovane slike čuvaju se u Docker volume-ima.

Za zaustavljanje:

```bash
docker compose down
```

Za potpuno čist novi start, uključujući brisanje baze i slika:

```bash
docker compose down -v
```
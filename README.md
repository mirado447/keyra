# Keyra — Auth-as-a-Service

Plateforme d'authentification multi-tenant (mini Auth0/Clerk) : des développeurs tiers créent un compte, déclarent une application, et obtiennent des endpoints d'authentification (register/login/refresh) prêts à l'emploi pour leurs propres utilisateurs finaux, avec isolation stricte entre applications.

**Stack** : Backend Python/FastAPI · Base de données PostgreSQL · ORM SQLAlchemy · Migrations Alembic · Frontend React (à venir) · Déploiement Docker (à venir)

---

## 1. Modélisation (MCD / MLD)

### Entités et cardinalités (MCD)

```
DEVELOPER (0,N) ---- CRÉE ---- (1,1) APPLICATION
APPLICATION (0,N) ---- POSSÈDE ---- (1,1) ENDUSER
ENDUSER (0,N) ---- POSSÈDE ---- (1,1) REFRESHTOKEN
```

### Schéma des tables (MLD)

**developers**
| Colonne | Type | Contrainte |
|---|---|---|
| id | INTEGER | PK |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | |

**applications**
| Colonne | Type | Contrainte |
|---|---|---|
| id | INTEGER | PK |
| name | VARCHAR(100) | NOT NULL |
| public_key | VARCHAR(255) | UNIQUE, NOT NULL |
| private_key_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | |
| developer_id | INTEGER | FK → developers.id |

**endusers**
| Colonne | Type | Contrainte |
|---|---|---|
| id | INTEGER | PK |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL *(unique par application, pas globalement)* |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | |
| application_id | INTEGER | FK → applications.id |

**refresh_tokens**
| Colonne | Type | Contrainte |
|---|---|---|
| id | INTEGER | PK |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL |
| expires_at | TIMESTAMP | NOT NULL |
| revoked | BOOLEAN | défaut FALSE |
| created_at | TIMESTAMP | |
| end_user_id | INTEGER | FK → endusers.id |

**Point de sécurité important** : `private_key_hash` (l'équivalent de `app_secret`) est stocké **hashé**, jamais en clair — comme un mot de passe. Il n'est affiché en clair au développeur qu'**une seule fois**, à la création de l'application.

---

## 2. Setup du projet

### Créer le projet et l'environnement virtuel

```bash
mkdir Keyra
cd Keyra
python -m venv venv
```

Activer l'environnement virtuel (à refaire à chaque nouvelle session de travail, dans un nouveau terminal) :
```bash
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### Installer les dépendances

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-jose passlib bcrypt python-dotenv
pip freeze > requirements.txt
```

| Paquet | Rôle |
|---|---|
| fastapi | Framework backend |
| uvicorn | Serveur qui fait tourner FastAPI |
| sqlalchemy | ORM (modèles ↔ tables) |
| psycopg2-binary | Driver PostgreSQL |
| alembic | Migrations de base de données |
| python-jose | Génération/validation JWT |
| passlib + bcrypt | Hashing des mots de passe |
| python-dotenv | Lecture du fichier `.env` |

### Structure de dossiers

```
Keyra/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   └── models/
│       ├── __init__.py
│       ├── developer.py
│       ├── application.py
│       ├── enduser.py
│       └── refresh_token.py
├── alembic/
│   ├── versions/
│   └── env.py
├── venv/
├── .env
├── .gitignore
├── alembic.ini
└── requirements.txt
```

### Vérifier que FastAPI tourne

`app/main.py` (contenu minimal de test) :
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

Lancer le serveur **depuis la racine du projet** (jamais depuis un sous-dossier) :
```bash
uvicorn app.main:app --reload
```
Vérifier sur `http://localhost:8000/health` et la doc auto-générée sur `http://localhost:8000/docs`.

---

## 3. PostgreSQL

### Installation (Windows)

1. Télécharger l'installeur officiel sur `https://www.postgresql.org/download/windows/`
2. Installer avec PostgreSQL Server + pgAdmin 4 + Command Line Tools
3. Port par défaut : `5432`
4. Noter le mot de passe du superutilisateur `postgres`

Vérifier :
```bash
psql --version
```

### Créer la base et un utilisateur dédié (bonne pratique : ne jamais utiliser `postgres` directement)

```bash
psql -U postgres
```
Puis en SQL :
```sql
CREATE USER keyra WITH PASSWORD 'mdp';
CREATE DATABASE keyra_db OWNER keyra;
GRANT ALL PRIVILEGES ON DATABASE keyra_db TO keyra;
\l
\q
```

Tester la connexion avec le nouvel utilisateur :
```bash
psql -U keyra -d keyra_db
```

---

## 4. Configuration `.env` et `.gitignore`

**`.env`** (racine du projet — ne JAMAIS commiter ce fichier) :
```
DATABASE_URL=postgresql://keyra:mdpt@localhost:5432/keyra_db
```

**`.gitignore`** (racine du projet) :
```
venv/
.env
__pycache__/
```

---

## 5. `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Point de vigilance** : `load_dotenv()` doit recevoir le **chemin explicite** vers `.env` (via `os.path.dirname(__file__)`), sinon le fichier n'est pas retrouvé de façon fiable selon l'endroit d'où une commande est lancée (cause fréquente d'erreur `DATABASE_URL = None`).

---

## 6. Modèles SQLAlchemy (`app/models/`)

Chaque fichier définit une classe héritant de `Base`, avec `__tablename__` au pluriel.

**Règle générale à respecter** :
- Toujours importer `ForeignKey` quand une colonne l'utilise
- Toujours importer `Boolean` quand une colonne l'utilise
- `DateTime` (pas `Datetime`) pour les types date
- `from datetime import datetime` (module standard) — ne pas confondre avec `database.py`

*(Voir les 4 fichiers dans `app/models/` pour le détail exact des colonnes — cf. schéma MLD en section 1)*

**`app/models/__init__.py`** — centralise les imports, indispensable pour qu'Alembic détecte toutes les tables :
```python
from app.models.developer import Developer
from app.models.application import Application
from app.models.enduser import Enduser
from app.models.refresh_token import RefreshToken
```

---

## 7. Alembic (migrations)

### Initialisation

```bash
alembic init alembic
```

### Configuration `alembic/env.py`

En haut du fichier :
```python
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base
from app.models import Developer, Application, Enduser, RefreshToken

load_dotenv()
```

Remplacer :
```python
target_metadata = None
```
par :
```python
target_metadata = Base.metadata
```

Dans **les deux fonctions** `run_migrations_offline()` et `run_migrations_online()`, injecter l'URL depuis `.env` en première ligne :
```python
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
```

### Générer une migration

```bash
alembic revision --autogenerate -m "create initial tables"
```
→ Toujours **relire** le fichier généré dans `alembic/versions/` avant de l'appliquer (Alembic devine, mais peut se tromper).

### Appliquer la migration

```bash
alembic upgrade head
```

### Vérifier

```bash
psql -U keyra -d keyra_db
```
```sql
\dt
```
→ Doit lister `developers`, `applications`, `endusers`, `refresh_tokens`, `alembic_version`.

---

## 8. Prochaines étapes (roadmap)

- [x] Modélisation MCD/MLD
- [x] Setup FastAPI + PostgreSQL
- [x] Modèles SQLAlchemy + première migration
- [ ] Endpoints d'authentification développeur (register/login)
- [ ] Gestion des applications (création, `public_key`/`private_key_hash`)
- [ ] Endpoints d'authentification end-user, scopés par application (le cœur du projet — isolation multi-tenant)
- [ ] Sécurité renforcée (rate limiting, validation stricte, rotation des tokens)
- [ ] Dashboard frontend React
- [ ] Dockerisation + déploiement

---

## Principe directeur du projet

Ce projet ne vise pas à rivaliser avec Auth0 en production. L'objectif est de démontrer, à échelle réduite mais fonctionnelle et correcte, une compréhension réelle des mécanismes d'authentification multi-tenant (JWT, refresh tokens, hashing, isolation des données) — un projet de démonstration technique, pas un produit commercial.
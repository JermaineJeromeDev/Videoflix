# Videoflix Backend

### Language / Sprache

- 🇬🇧 [English Version](#english-version)
- 🇩🇪 [Deutsche Version](#deutsche-version)

---

<a id="english-version"></a>

## 🇬🇧 English Version

REST API backend for the Videoflix video streaming platform, built with Django and Django REST Framework. It supports secure asynchronous video processing, HLS streaming, and HttpOnly cookie-based JWT authentication.

### Product Pitch

Videoflix is a Netflix-inspired learning platform backend for users who want secure account management and adaptive video playback while keeping media processing asynchronous and scalable.

### Core Features

- User registration with activation email flow
- Account activation via secure uid/token validation
- Login and logout with HttpOnly JWT cookies (access + refresh)
- Refresh token blacklisting on logout
- Password reset flow with tokenized confirmation
- Adaptive HLS streaming with 480p, 720p, and 1080p variants

### Repository Role

This repository contains the backend API only. The frontend client is maintained separately and consumes the endpoints documented below.

### Project Status & Scope

- Type: Final backend project from the Developer Akademie training
- Scope: MVP focused on backend architecture and API workflows
- Production readiness: Educational project, not positioned as production-grade SaaS

### Table of Contents

1. [Tech Stack](#tech-stack-en)
2. [Prerequisites](#prerequisites-en)
3. [Setup & Installation](#setup--installation-en)
4. [API Endpoints](#api-endpoints-en)
5. [Video Processing Workflows](#video-processing-workflows-en)

<a id="tech-stack-en"></a>

### 1. Tech Stack

- **Django 5+ & Django REST Framework** – Core API Framework
- **PostgreSQL** – Primary production database
- **Redis** – In-memory caching and message broker layer
- **Django RQ** – Asynchronous background processing (FFMPEG conversion)
- **JWT via HttpOnly Cookies** – Secure authentication
- **Docker & Docker Compose** – Containerization and environment orchestration

<a id="prerequisites-en"></a>

### 2. Prerequisites

- Docker Desktop installed and running
- Git

<a id="setup--installation-en"></a>

### 3. Setup & Installation

**1. Clone the repository:**

```bash
git clone https://github.com
cd Videoflix
```

**2. Create and configure the environment variables:**
Create a `.env` file in the root directory:

```bash
cp .env.template .env
```

Adjust the following values in your `.env` file:

| Variable               | Description                           | Default / Example                             |
| :--------------------- | :------------------------------------ | :-------------------------------------------- |
| `SECRET_KEY`           | Django cryptographic signing key      | _Your secure key_                             |
| `DEBUG`                | Django debug toggle                   | `True`                                        |
| `ALLOWED_HOSTS`        | Allowed backend hostnames             | `localhost,127.0.0.1`                         |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for secure requests   | `http://localhost:5500,http://127.0.0.1:5500` |
| `DB_NAME`, `DB_USER`   | PostgreSQL target database & owner    | `videoflix_db`, `videoflix_admin`             |
| `DB_PASSWORD`          | PostgreSQL user password              | `passwort123`                                 |
| `DB_HOST`, `DB_PORT`   | PostgreSQL host and port              | `db`, `5432`                                  |
| `REDIS_LOCATION`       | Full connection URI for Redis cache   | `redis://redis:6379/1`                        |
| `EMAIL_HOST`           | SMTP Server Host                      | `://gmail.com`                                |
| `EMAIL_PORT`           | SMTP Server Port                      | `587`                                         |
| `EMAIL_HOST_USER`      | Outbound email authentication account | `your.email@gmail.com`                        |
| `EMAIL_HOST_PASSWORD`  | 16-character Google App Password      | `abcdefghijklmnop`                            |

**3. Build and launch the Docker containers:**

```bash
docker compose up -d --build
```

_The API is now available locally at `http://localhost:8000/`._

**4. Run the automated test suite:**
Verify that all 27 unit tests pass successfully inside the runtime container:

```bash
docker compose exec web python -m pytest
```

<a id="api-endpoints-en"></a>

### 4. API Endpoints

#### Authentication (`auth_app`)

| Method   | Endpoint                                  | Description                                                         |
| :------- | :---------------------------------------- | :------------------------------------------------------------------ |
| **POST** | `/api/register/`                          | Register a new inactive user account. Sends activation email.       |
| **GET**  | `/api/activate/<uidb64>/<token>/`         | Activate account via query-parameter mapping.                       |
| **POST** | `/api/login/`                             | Validate data and issue secure HttpOnly JWT cookies.                |
| **POST** | `/api/logout/`                            | Blacklist refresh token and clear client cookies.                   |
| **POST** | `/api/refresh/`                           | Re-issue a fresh access token cookie using the refresh cookie.      |
| **POST** | `/api/password_reset/`                    | Request an asynchronous password reset email (anonymized response). |
| **POST** | `/api/password_confirm/<uidb64>/<token>/` | Set a brand new account password.                                   |

#### Video Catalog (`video_app`)

| Method  | Endpoint                                          | Description                                                |
| :------ | :------------------------------------------------ | :--------------------------------------------------------- |
| **GET** | `/api/video/`                                     | List all available videos ordered by `created_at` DESC.    |
| **GET** | `/api/video/<movie_id>/<resolution>/index.m3u8`   | Stream the target HLS master playlist (480p, 720p, 1080p). |
| **GET** | `/api/video/<movie_id>/<resolution>/<segment>.ts` | Fetch specific secure binary HLS video fragments.          |

<a id="video-processing-workflows-en"></a>

### 5. Video Processing Workflows

Videos are uploaded exclusively via the Django Admin interface (`http://localhost:8000/admin/`). Upon successfully saving a video record with an raw `.mp4` file, a database signal intercepts the request and offloads three parallel encoding tasks to the Redis queue. An asynchronous `rqworker` spins up FFMPEG to segment the media files into HLS-compliant streams for **480p, 720p, and 1080p** adaptive bit-rate playback alongside saving the dedicated custom thumbnail.

---

<a id="deutsche-version"></a>

## 🇩🇪 Deutsche Version

REST-API-Backend für die Videoflix-Videostreaming-Plattform, entwickelt mit Django und dem Django REST Framework. Unterstützt asynchrone Videoverarbeitung im Hintergrund, HLS-Streaming und HttpOnly-cookiebasierte JWT-Authentifizierung.

### Produkt-Pitch

Videoflix ist ein Netflix-inspiriertes Backend für eine Lernplattform. Ziel ist es, sichere Benutzerverwaltung und adaptives Video-Streaming bereitzustellen und die Medienverarbeitung asynchron sowie skalierbar umzusetzen.

### Kernfunktionen

- Benutzerregistrierung mit Aktivierungs-E-Mail-Workflow
- Kontoaktivierung über sichere uid/token-Prüfung
- Login und Logout über HttpOnly-JWT-Cookies (Access + Refresh)
- Blacklisting des Refresh-Tokens beim Logout
- Passwort-Reset mit tokenbasierter Bestätigung
- Adaptives HLS-Streaming in 480p, 720p und 1080p

### Rolle Dieses Repositories

Dieses Repository enthält ausschließlich das Backend (API). Das Frontend wird separat verwaltet und nutzt die unten dokumentierten Endpunkte.

### Status & Scope

- Typ: Backend-Endprojekt aus der Weiterbildung bei der Developer Akademie
- Umfang: MVP mit Fokus auf Backend-Architektur und API-Workflows
- Produktionsreife: Lernprojekt, nicht als produktionsreifes SaaS positioniert

### Inhaltsverzeichnis

1. [Tech Stack](#tech-stack-de)
2. [Voraussetzungen](#voraussetzungen-de)
3. [Setup & Installation](#setup--installation-de)
4. [API-Endpunkte](#api-endpunkte-de)
5. [Videoverarbeitungs-Workflow](#videoverarbeitungs-workflow-de)

<a id="tech-stack-de"></a>

### 1. Tech Stack

- **Django 5+ & Django REST Framework** – Kern-API-Framework
- **PostgreSQL** – Primäre relationale Produktionsdatenbank
- **Redis** – In-Memory-Caching-Layer und Message-Broker für Hintergrund-Tasks
- **Django RQ** – Asynchroner Background-Task-Runner (FFMPEG-Videokonvertierung)
- **JWT via HttpOnly Cookies** – Hochsicheres Authentifizierungsverfahren
- **Docker & Docker Compose** – Containerisierung und Infrastruktur-Orchestrierung

<a id="voraussetzungen-de"></a>

### 2. Voraussetzungen

- Docker Desktop installiert und aktiv
- Git

<a id="setup--installation-de"></a>

### 3. Setup & Installation

**1. Repository klonen:**

```bash
git clone https://github.com
cd Videoflix
```

**2. Umgebungsvariablen anlegen und konfigurieren:**
Erstelle eine `.env`-Datei auf oberster Ebene deines Projekts:

```bash
cp .env.template .env
```

Passe die folgenden Werte in deiner `.env`-Datei an:

| Variable               | Beschreibung                                     | Standard / Beispiel                           |
| :--------------------- | :----------------------------------------------- | :-------------------------------------------- |
| `SECRET_KEY`           | Kryptografischer Sicherheitsschlüssel für Django | _Dein sicherer Key_                           |
| `DEBUG`                | Aktiviert/Deaktiviert den Django-Debug-Modus     | `True`                                        |
| `ALLOWED_HOSTS`        | Erlaubte Hostnamen für das Backend               | `localhost,127.0.0.1`                         |
| `CSRF_TRUSTED_ORIGINS` | Vertrauenswürdige Herkunfts-URLs für Formulare   | `http://localhost:5500,http://127.0.0.1:5500` |
| `DB_NAME`, `DB_USER`   | PostgreSQL Datenbankname & Besitzer              | `videoflix_db`, `videoflix_admin`             |
| `DB_PASSWORD`          | Passwort des Datenbank-Benutzers                 | `passwort123`                                 |
| `DB_HOST`, `DB_PORT`   | Hostname und Port für PostgreSQL                 | `db`, `5432`                                  |
| `REDIS_LOCATION`       | Verbindungs-URI für den Redis-Cache              | `redis://redis:6379/1`                        |
| `EMAIL_HOST`           | SMTP-Server-Adresse                              | `://gmail.com`                                |
| `EMAIL_PORT`           | SMTP-Server-Port                                 | `587`                                         |
| `EMAIL_HOST_USER`      | E-Mail-Konto für den Postausgang                 | `deine.email@gmail.com`                       |
| `EMAIL_HOST_PASSWORD`  | 16-stelliges Google App-Passwort                 | `abcdefghijklmnop`                            |

**3. Docker-Container bauen und starten:**

```bash
docker compose up -d --build
```

_Die API ist nun lokal unter `http://localhost:8000/` erreichbar._

**4. Automatisierte Test-Suite ausführen:**
Überprüfe, ob alle 27 Unit-Tests innerhalb der Container-Umgebung erfolgreich durchlaufen:

```bash
docker compose exec web python -m pytest
```

<a id="api-endpunkte-de"></a>

### 4. API-Endpunkte

#### Benutzerverwaltung & Authentifizierung (`auth_app`)

| Methode  | Endpunkt                                  | Beschreibung                                                                  |
| :------- | :---------------------------------------- | :---------------------------------------------------------------------------- |
| **POST** | `/api/register/`                          | Registriert einen neuen, inaktiven Benutzer und sendet die Aktivierungs-Mail. |
| **GET**  | `/api/activate/<uidb64>/<token>/`         | Aktiviert den Benutzer-Account über die Frontend-Parameter.                   |
| **POST** | `/api/login/`                             | Prüft die Daten und setzt die sicheren HttpOnly-JWT-Cookies.                  |
| **POST** | `/api/logout/`                            | Setzt den Refresh-Token auf die Blacklist und löscht die Cookies.             |
| **POST** | `/api/refresh/`                           | Erneuert das Access-Token-Cookie mithilfe des Refresh-Cookies.                |
| **POST** | `/api/password_reset/`                    | Stößt den asynchronen Passwort-Reset an (anonymisierte Server-Antwort).       |
| **POST** | `/api/password_confirm/<uidb64>/<token>/` | Speichert ein neues, geändertes Passwort in der Datenbank.                    |

#### Videokatalog & Streaming (`video_app`)

| Methode | Endpunkt                                          | Beschreibung                                                             |
| :------ | :------------------------------------------------ | :----------------------------------------------------------------------- |
| **GET** | `/api/video/`                                     | Gibt alle Videos sortiert nach Erstellungsdatum (`created_at` DESC) aus. |
| **GET** | `/api/video/<movie_id>/<resolution>/index.m3u8`   | Liefert die HLS-Master-Playlist für den Player (480p, 720p, 1080p).      |
| **GET** | `/api/video/<movie_id>/<resolution>/<segment>.ts` | Liefert die verschlüsselten, binären HLS-Videosegmente aus.              |

<a id="videoverarbeitungs-workflow-de"></a>

### 5. Videoverarbeitungs-Workflow

Videos werden ausschließlich über das Django-Admin-Interface (`http://localhost:8000/admin/`) hochgeladen. Sobald ein Video-Datensatz mit einer rohen `.mp4`-Datei abgespeichert wird, fängt ein Django-Datenbank-Signal den Request ab und übergibt drei parallele Encodierungs-Jobs an die Redis-Warteschlange. Ein asynchroner `rqworker` startet im Hintergrund FFMPEG, um das Video vollautomatisch in HLS-konforme Streams für **480p, 720p und 1080p** zu segmentieren, während zeitgleich das zugewiesene Custom-Thumbnail registriert wird.

# Bibliotheks-Ausleih-API

Eine in Python mit FastAPI, Pydantic v2 und SQLAlchemy 2.0 gebaute REST-API für die Ausleihe einer kleinen Stadtbibliothek. Sie verwaltet Bücher, Mitglieder und Ausleihen in einer SQLite-Datenbank, setzt die Leihregeln serverseitig durch (maximal drei offene Ausleihen pro Mitglied, nur freie Exemplare, 14 Tage Leihfrist, Rückgabe schließt die Ausleihe) und schützt schreibende Endpunkte per API-Key. Eine Buchsuche mit Paginierung sowie einheitliche Fehlerantworten runden den Sprint ab.

## Tech-Stack

- **Sprache**: Python
- **Framework**: FastAPI
- **Validierung**: Pydantic v2
- **ORM**: SQLAlchemy 2.0
- **Datenbank**: SQLite
- **Tests**: pytest + FastAPI TestClient
- **Konfiguration**: pydantic-settings / Umgebungsvariablen

## Installation

```bash
python -m pip install -e ".[dev]"
```

## Start (Entwicklung)

```bash
uvicorn app.main:app --port 8000
```

Die Anwendung legt beim Start automatisch die Tabellen in der SQLite-Datenbank an (`sqlite:///./library.db`).

## Konfiguration

| Variable          | Zweck                        | Dev-Default   |
| ----------------- | ---------------------------- | ------------- |
| `LIBRARY_API_KEY` | API-Key für schreibende Endpunkte | `dev-key` |
| `DATABASE_URL`    | SQLAlchemy-Datenbank-URL     | `sqlite:///./library.db` |

Schreibende Endpunkte (`POST`/`PUT`/`PATCH`/`DELETE`) verlangen den Header `X-API-Key` mit dem Wert aus `LIBRARY_API_KEY`. Lesende Endpunkte bleiben ohne Key erreichbar.

## Endpunkte

| Methode | Pfad                 | Beschreibung                                  |
| ------- | -------------------- | --------------------------------------------- |
| GET     | `/health`            | Health-Check (`{"status": "ok"}`)             |
| GET     | `/books`             | Bücher auflisten / suchen (Pagination)        |
| POST    | `/books`             | Buch anlegen                                   |
| GET     | `/books/{id}`        | Buch einzeln lesen                             |
| PUT     | `/books/{id}`        | Buch vollständig aktualisieren                 |
| PATCH   | `/books/{id}`        | Buch teilweise aktualisieren                   |
| DELETE  | `/books/{id}`        | Buch löschen                                   |
| GET     | `/members`           | Mitglieder auflisten                           |
| POST    | `/members`           | Mitglied anlegen                               |
| GET     | `/members/{id}`      | Mitglied einzeln lesen                         |
| PUT     | `/members/{id}`      | Mitglied vollständig aktualisieren             |
| PATCH   | `/members/{id}`      | Mitglied teilweise aktualisieren               |
| DELETE  | `/members/{id}`      | Mitglied löschen                               |
| POST    | `/loans`             | Ausleihe anlegen                               |
| POST    | `/loans/{id}/return` | Ausleihe zurückgeben                           |
| GET     | `/loans/overdue`     | Überfällige offene Ausleihen auflisten         |

### Fehlerantworten

Alle Fehlerantworten folgen demselben Schema:

```json
{ "detail": { "code": "not_found", "message": "..." } }
```

Mögliche Codes: `not_found` (404), `conflict` (409), `unauthorized` (401), `validation` (422).

## Tests

```bash
PYTHONPATH=. pytest
```

Die Test-Suite läuft gegen eine separate In-Memory-SQLite-Datenbank.

## Features

- Vollständiges CRUD für Bücher und Mitglieder
- Leihregeln: max. 3 offene Ausleihen pro Mitglied, nur freie Exemplare, 14 Tage Leihfrist
- Rückgabe schließt eine Ausleihe; doppelte Rückgabe wird abgelehnt
- Buchsuche über Titel/Autor (case-insensitiv) mit Paginierung
- Überfällige Ausleihen abrufbar
- API-Key-Schutz für schreibende Endpunkte
- Einheitliche Fehlerantworten

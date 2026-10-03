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

`LIBRARY_API_KEY` ist **erforderlich** und hat keinen festen Default — setzen Sie ihn, bevor Sie starten:

```bash
# Linux/macOS
export LIBRARY_API_KEY=<ein-beliebiger-Key>

# Windows (PowerShell)
$env:LIBRARY_API_KEY = "<ein-beliebiger-Key>"
```

Danach:

```bash
uvicorn app.main:app --port 8000
```

Die `RUN.json` erzeugt den Key bei Tessa/CI automatisch pro Lauf. Die Anwendung legt beim Start automatisch die Tabellen in der SQLite-Datenbank an (`sqlite:///./library.db`). Fehlt `LIBRARY_API_KEY`, verweigert die Anwendung den Start mit einer klaren Fehlermeldung.

## Konfiguration

| Variable          | Zweck                          | Default                        |
| ----------------- | ------------------------------ | ------------------------------ |
| `LIBRARY_API_KEY` | API-Key für schreibende Endpunkte | **erforderlich**, kein Default |
| `DATABASE_URL`    | SQLAlchemy-Datenbank-URL       | `sqlite:///./library.db`       |

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

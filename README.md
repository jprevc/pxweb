# pxweb-client

A small Python client for the **v1 API** of [PxWeb](https://www.scb.se/en/services/statistical-programs-for-px-files/px-web/),
the publishing platform that many national statistics offices use for their databases. Use it to list
tables, inspect their variables, and download data as plain records, ready for pandas, polars or
anything else.

PxWeb **API v2** is not supported yet.

## Install

```bash
pip install pxweb-client
```

The import name is `pxweb`. Its only dependency is `httpx`.

## Usage

Point the client at a server's API root (the URL up to `/api/v1`), a database and a language.
The examples use [SiStat](https://pxweb.stat.si/SiStat), the database of the Statistical Office
of Slovenia; for SiStat specifically, see [`sistat`](https://github.com/jprevc/sistat).

```python
from pxweb import PxWebClient

with PxWebClient("https://pxweb.stat.si/SiStatData/api/v1", "Data", "en", user_agent="my-app/1.0") as px:
    px.tables()                       # tables and folders at the database root
    # [TableInfo(id='0156101S.px', text='Average annual and monthly air temperatures [°C] by ...', ...), ...]

    meta = px.metadata("0156101S.px")
    for v in meta.variables:
        print(v.code, "|", v.text, "|", v.value_texts[:3])
    # METEOROLOŠKA POSTAJA | METEOROLOGICAL STATION | ('SLOVENIA', 'Bilje', 'Bovec')
    # OBDOBJE, LETO | PERIOD, YEAR | ('1981-1990', '1991-2000', '2001-2010')
    # MERITVE | MEASURE | ('Average temperature - ANNUAL', 'January', 'February')

    records = px.get_records(
        "0156101S.px",
        {
            "METEOROLOGICAL STATION": ["Ljubljana, Bežigrad", "Maribor, Tabor"],
            "PERIOD, YEAR": "201*",
        },
    )
    # [{'METEOROLOGICAL STATION': 'Ljubljana, Bežigrad', 'PERIOD, YEAR': '2010',
    #   'MEASURE': 'Average temperature - ANNUAL', 'value': 10.7}, ...]
```

Pass your own `user_agent` so server operators can tell your application apart; the default is
`pxweb-python/<version>`.

### Selections

Keys are variables, given as their code or their label, case-insensitively. Values can be:

| Selection                         | Meaning                                    |
|-----------------------------------|--------------------------------------------|
| `"Ljubljana, Bežigrad"` or `"10"` | one value, by label or code                |
| `["10", "Maribor, Tabor"]`        | several values                             |
| `"2020*"`, `"*"`                  | glob pattern over codes and labels         |
| `"top:5"`                         | the first 5 values in the table's order    |

Matching ignores case and accents (`"cas"` matches `"čas"`); `pxweb.fold` exposes the same rule.
Every variable you leave out is sent with all its values selected. PxWeb would otherwise drop it
from the result without telling you.

Pass `codes=True` to also get a `<variable>_code` key with the raw value codes. Queries that
exceed the server's cell limit are split into several requests and merged. Requests are kept
under the server's rate limit (read from its `?config` endpoint) automatically.

### Errors and logging

Every error is a `pxweb.PxWebError`: `APIError` for error responses (with `status_code`) and
failed requests, `QueryError` (also a `ValueError`) for selections that don't match the table.
If the server's limits can't be read, a warning is logged to the `pxweb` logger and defaults are used.

### Testing your code

`pxweb.testing.FakePxWeb` is an in-memory PxWeb v1 server for `httpx.MockTransport`. Give it a
table listing and recorded metadata and json-stat2 responses; it answers queries by slicing them.

```python
import httpx
from pxweb import PxWebClient
from pxweb.testing import FakePxWeb

fake = FakePxWeb("Data", tables=[...], metadata={"T.px": meta}, data={"T.px": dataset})
px = PxWebClient("https://example.test/api/v1", "Data", "en", transport=httpx.MockTransport(fake))
```

## Development

```bash
uv sync
uv run pytest            # offline tests against recorded fixtures
uv run ruff check .
uv run mypy
```

The test fixtures are responses recorded from SiStat. Data © SURS, see their
[terms of use](https://www.stat.si/StatWeb/en/StaticPages/Index/Copyright).

# Bet Intelligence AI

FastAPI + PostgreSQL + скенер на мачове, деплойнат на Render.

## Какво прави

- **Скенер** — тегли предстоящи мачове от топ футболните лиги (Premier League,
  La Liga, Serie A, Bundesliga, Ligue 1, Шампионска лига) от **API-Football**,
  коефициенти от **The Odds API** и статистики от **FootyStats**, изчислява
  AI Score / Value % и ги пази в базата.
- **Дневник** — прогнозите (ръчни или от скенера) се пазят трайно в
  PostgreSQL, не в браузъра. ROI/Win Rate/Net Profit се смятат на сървъра.

## Локално стартиране

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Без `DATABASE_URL` приложението пада обратно на локален SQLite файл
(`backend/local.db`), за да можеш да го тестваш без база на Render.

## Deploy в Render

Blueprint deploy с `render.yaml` — той вече дефинира и безплатна Postgres
база (`bet-intelligence-db`), автоматично свързана към web service чрез
`DATABASE_URL`.

Environment variables за въвеждане ръчно в Render (Secret, `sync: false`):
- `FOOTYSTATS_API_KEY`
- `ODDS_API_KEY`
- `API_FOOTBALL_KEY`

⚠️ **Важно:** безплатната Render Postgres база **изтича 30 дни след
създаване** (14 дни грейс период след това), след което данните се трият,
ако не се ъпгрейдне до платен план. За постоянна употреба обмисли платен
инстанс (~$6-7/мес) навреме.

## Endpoints

- `GET /api/health` — статус на ключовете и връзката с базата
- `POST /api/scanner/refresh` — тегли реални данни и обновява селекциите
- `GET /api/scanner/picks?sport=&min_score=&min_value=&sort=` — списък селекции
- `GET /api/bets` / `POST /api/bets` / `PATCH /api/bets/{id}` / `DELETE /api/bets/{id}`
- `POST /api/bets/from-pick` — добавя селекция от скенера в дневника
- `GET /api/stats/summary` — обобщена статистика (ROI, win rate, ...)

## Известни ограничения (за следваща итерация)

- Засега скенерът генерира само пазарите **"Над/Под 2.5 гола"** и **BTTS**
  (корнери/картони изискват по-скъп FootyStats/API-Football план).
- Съвпадението на мачове между трите източника е по имена на отборите
  (нормализирани) — работи добре за големите клубове, но не е перфектно.
- "Forebet %" полето реално се захранва от FootyStats потенциали (Forebet
  няма публично API), запазено е само като име на колоната за съвместимост.
- Точните имена на полетата от FootyStats/Odds API markets може да се
  различават леко от очакваното в кода — при първия реален `refresh` провери
  `/api/footystats/todays-matches` (бутон "FootyStats – суров отговор" в таб
  API Status) и коригирай при нужда в `backend/services/`.
- Тенис/баскетбол/волейбол все още не са включени в скенера — само футбол.

# Known Limitations

## 1. Quota sensitivity

Система чувствительна к:
- 429
- RATE_LIMIT_EXCEEDED
- quota exceeded
- временным внешним сбоям Google APIs

Особенно это касается:
- repeated MASTER_INDEX lookup
- deep diagnostics
- smoke/regression flows

## 2. MASTER_INDEX dependency

Большая часть полезной логики опирается на:
- доступность MASTER_INDEX
- корректность его структуры
- доступность Google Sheets API

Это создает единый чувствительный operational dependency.

## 3. Deep path instability

doctor и smoke-проверки:
- полезны;
- explainable;
- но могут быть нестабильны при quota pressure.

Их нельзя интерпретировать изолированно без контекста и без reconciliation logic.

## 4. Cache not yet implemented

Пока отсутствует полноценный:
- MASTER_INDEX cache
- in-process memoization
- one-fetch local filtering

Из-за этого система делает больше внешних обращений, чем хотелось бы.

## 5. docs_agent_v2 status

docs_agent_v2.py пока следует считать:
- draft / alternative variant
- не полностью canonical baseline

Нужна отдельная нормализация решения:
- либо canonical,
- либо experimental branch artifact.

## 6. audits growth

Папка audits полезна, но со временем может:
- стать шумной
- ухудшить читаемость baseline
- затруднить onboarding

Нужна дальнейшая курируемая политика хранения артефактов.

## 7. Secrets handling

Хотя config/ уже исключен из git, локальная работа все равно требует дисциплины:
- не показывать токены
- не публиковать client secrets
- при утечке ротировать credentials

## 8. Practical workaround policy

Пока cache не внедрен, разумная практика такая:
1. routine checks через doctor-lite
2. deep checks только по необходимости
3. не запускать deep path сериями
4. при спорном результате делать cooldown и reconciliation

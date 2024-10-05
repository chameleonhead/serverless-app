# Contacts

## DB スキーママイグレーションツール (alembic) の使い方

DB を最新化する

```bash
alembic upgrade head
```

マイグレーションを追加する

```bash
alembic revision -m "create account table"
```

一つ戻す

```bash
alembic downgrade -1
```

一つ進める

```bash
alembic upgrade +1
```

最初の状態（何もない状態）に戻す

```bash
alembic downgrade base
```

https://alembic.sqlalchemy.org/en/latest/tutorial.html

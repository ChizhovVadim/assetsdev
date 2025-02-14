# assets

## assets
Пакет assets позволяет скачивать и смотреть котировки акций и строить отчеты по брокерскому счету.

- Отчет об изменении котировок за период. Учитывает дивиденды и сплиты.
```
$python3 -m assets.quotes.cmd_view --start 2024-12-17 --dividend
```

- Скачивает исторические котировки (для отладки).
```
$python3 -m assets.quotes.cmd_testdownload --provider finam --timeframe daily --security SBER
```

- Скачивает и обновляет исторические котировки.
```
$python3 -m assets.quotes.cmd_update --provider mfd,finam
```

- Балансовый отчет по брокерскому счету.
```
$python3 -m assets.portfolio.cmd_balance
```

- Отчет о прибылях и убытках по брокерскому счету.
```
$python3 -m assets.portfolio.cmd_pnl
```

- Отчет о дивидендах по брокерскому счету.
```
$python3 -m assets.portfolio.cmd_dividend
```

- Импорт сделок из брокерского отчета сбербанка.
```
$python3 -m assets.portfolio.cmd_import_sber
```

## trading
Пакет trading позволяет скачивать котировки фьючерсов и тестировать на истории торговые стратегии.

- Скачивает исторические котировки (для отладки).
```
$python3 -m trading.history.cmd_testdownload --provider finam --timeframe minutes5 --security Si-3.25
```

- Скачивает и обновляет исторические котировки.
```
$python3 -m trading.history.cmd_update --provider finam,mfd --timeframe minutes5 --security CNY-3.25,Si-3.25
```

- Показывает несколько последних позиций торгового советника (для отладки).
```
$python3 -m trading.history.cmd_status --security Si-3.25 --advisor main
```

- Тестирует на истории торгового советника.
```
$python3 -m trading.history.cmd_history --security Si --startyear 2009 --advisor main
```

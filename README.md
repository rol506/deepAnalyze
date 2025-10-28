# Deep analyze - детальный анализатор карт градостроительства

## Установка
Для установки потребуется python версии 3 и выше, git, pip и подключение к Интернету.

Для Windows:
```bash
git clone https://github.com/ro506/deepAnalyze.git
python -m venv deepAnalyze
cd deepAnalyze
Scripts\activate
pip install -r requirements.txt
```

Для Linux/Mac:
```bash
git clone https://github.com/ro506/deepAnalyze.git
python3 -m venv deepAnalyze
cd deepAnalyze
source bin/activate
pip install -r requirements.txt
```

## Использование
Приложение работает в веб-интерфейсе. Для его запуска выполните следующую команду:
```bash
python src/main.py
```
Веб интерфейс будет доступен по адресу устройства на порте 4221.

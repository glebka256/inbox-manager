# Gmail AI Manager (inbox-manager)

Система керування поштовою скринькою Gmail на Python: підключається до скриньки за IMAP, класифікує листи (правила + модель машинного навчання), веде аналітику, перевіряє безпеку листів, виконує автоматичні дії та надає REST API для зовнішніх клієнтів.

Проєкт створено як навчальний для дисципліни «Інженерія та верифікація інформаційних систем».

> **Статус: навчальний прототип.** Система не готова до використання на реальній скриньці без перевірки результатів. Докладніше — у розділі [Відомі обмеження](#відомі-обмеження) та у файлі [SECURITY.md](SECURITY.md).

## Можливості

| Модуль | Файл | Призначення |
|---|---|---|
| Класифікація за правилами | `core/email_classifier.py` | Мітка, дія (label / archive / trash / star), важливість |
| Самонавчальний класифікатор | `smart_learning_classifier.py` | TF-IDF + Naive Bayes, відгуки користувача, власні категорії |
| Аналітика | `email_analytics.py` | Звіти та графіки (matplotlib, seaborn) |
| Бізнес-дані | `business_intelligence.py` | Вилучення ставок, рахунків, DOT-порушень |
| Безпека листів | `security_compliance.py` | Фішинг, PII, оцінка ризику 0–100 |
| Автоматизація | `email_automation.py` | Правила та сценарії, планувальник |
| REST API | `mobile_api.py` | 15 ендпоінтів під `/api` (Flask) |
| Головний конвеєр | `master_gmail_ai.py` | Об’єднує всі модулі, демонстраційний запуск |
| Графічний інтерфейс | `visual_advanced_gui.py` | Tkinter-панель з аналітикою |

## Вимоги

- **Python 3.12 або новіший.** `requirements.txt` закріплює `numpy==2.5.1`, якому потрібен Python ≥ 3.12.
- Tkinter (для GUI). У Windows і macOS входить до інсталяції Python; у Ubuntu/Debian: `sudo apt install python3-tk`.
- Для роботи з реальною скринькою: обліковий запис Gmail із двоетапною перевіркою та **пароль додатка** (звичайний пароль не підійде).

## Встановлення

```bash
git clone https://github.com/glebka256/inbox-manager.git
cd inbox-manager

# віртуальне середовище
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Налаштування облікових даних

Потрібно лише для роботи з реальною скринькою. Демонстраційний режим і запуск без скриньки облікових даних не потребують.

1. Увімкніть двоетапну перевірку в обліковому записі Google.
2. Створіть пароль додатка: <https://myaccount.google.com/apppasswords>.
3. Створіть файл з обліковими даними на основі шаблону:

   ```bash
   cp credentials/gmail_credentials_template.env credentials/gmail_credentials.env
   ```

4. Відредагуйте `credentials/gmail_credentials.env`:

   ```env
   GMAIL_USER=your.email@gmail.com
   GMAIL_PASS=abcdefghijklmnop
   ```

Файл `gmail_credentials.env` ігнорується Git. **Ніколи не додавайте його до репозиторію.** Докладніше про налаштування: [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Запуск

Усі команди виконуйте **з кореня репозиторію**: шляхи до баз даних і журналів відносні до поточного каталогу.

### Графічний інтерфейс

```bash
python visual_advanced_gui.py
```

Альтернативні інтерфейси: `python gui/Ai_Gmail_ManagerV3_GUI.py` (є режим DEMO) і `python launchers/gmail_ai_gui.py`. У Windows можна скористатися `LAUNCH_DASHBOARD.bat`.

> `INSTALL_AND_RUN.bat` посилається на файл `gui/Inbox_ManagerV3_GUI.py`, якого в репозиторії немає (файл називається `Ai_Gmail_ManagerV3_GUI.py`). Скрипт у поточному вигляді не запустить GUI; виправте шлях у ньому або запускайте вручну.

### Демонстрація головного конвеєра

```bash
python master_gmail_ai.py
```

Обробляє три тестові листи (ставка вантажу, фішинг, LinkedIn) і створює `master_config.json` та звіти. Для цього режиму Gmail не потрібен.

### REST API

```bash
python mobile_api.py
```

Сервер стартує на `http://localhost:5000/api`. Перевірка:

```bash
curl http://localhost:5000/api/status
```

> **Увага.** Запуск командою вище вмикає режим налагодження (`debug=True`), слухає всі мережеві інтерфейси (`0.0.0.0`) і **не має автентифікації**. Використовуйте лише в ізольованій локальній мережі. Правила безпечного запуску: [SECURITY.md](SECURITY.md) та [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Основні ендпоінти:

| Метод | Шлях | Опис |
|---|---|---|
| GET | `/api/status` | Стан системи |
| GET | `/api/dashboard` | Зведення для панелі |
| POST | `/api/classify` | Класифікація листа (`content`, `subject`, `sender`) |
| POST | `/api/learning/feedback` | Відгук для навчання (`email_content`, `correct_category`) |
| GET | `/api/search?q=…&category=…&limit=…` | Пошук по оброблених листах |
| GET / POST | `/api/categories` | Список і додавання категорій |
| GET / POST | `/api/automation/rules` | Правила автоматизації |

Повний перелік: `docs/api_documentation.json`.

## Структура репозиторію

```
inbox-manager/
├── core/                      # ядро класифікатора за правилами
├── utilities/                 # конфігурація, логування, БД, облікові дані
├── gui/                       # графічні інтерфейси (V3 актуальніший)
├── launchers/                 # .bat/.vbs-запускачі
├── credentials/               # шаблон і інструкція для облікових даних
├── data/                      # навчальні дані та приклади звітів
├── docs/                      # документація
├── *.py                       # модулі системи (корінь)
├── old_versions/              # застарілий код, не використовується
└── requirements.txt
```

## Документація

- [docs/ROLES.md](docs/ROLES.md) — ролі користувачів
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) — базові налаштування
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — розгортання
- [SECURITY.md](SECURITY.md) — безпека

## Відомі обмеження

- ML-гілка в `core/email_classifier.py` — заглушка: гібридний режим фактично дорівнює правилам. Справжня модель працює у `smart_learning_classifier.py`.
- Спам-детектор позначає лист як Spam лише за 10 і більше різних індикаторів із 24, тому спам із меншою кількістю ознак потрапляє в Unknown.
- Правила класифікації англомовні й орієнтовані на логістику; українська мова не підтримується.
- Автоматичних тестів немає; `utilities/test_*.py` лише перевіряють підключення.
- Документи `docs/COMPLETE FEATURES.MD` і `docs/README*.md` містять застарілі відомості про структуру проєкту та завищені оцінки готовності.

## Ліцензія

Файл ліцензії в репозиторії відсутній; додайте `LICENSE`, перш ніж поширювати код.

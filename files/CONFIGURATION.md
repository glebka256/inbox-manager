# Базові налаштування

Усі шляхи наведено відносно **кореня репозиторію**. Запускайте програму з цього каталогу: бази даних, журнали та файли конфігурації створюються в поточному каталозі.

## 1. Де зберігаються налаштування

| Джерело | Файл | Хто читає | Примітка |
|---|---|---|---|
| Облікові дані Gmail | `credentials/gmail_credentials.env` | `utilities/secure_loader.py` | Шаблон: `credentials/gmail_credentials_template.env` |
| Зашифровані облікові дані | `credentials/gmail_credentials.encrypted` | `utilities/secure_loader.py` | Має пріоритет над `.env` |
| Конфігурація головного конвеєра | `master_config.json` у поточному каталозі | `master_gmail_ai.py` | Створюється автоматично при запуску; приклад — `data/master_config.json` |
| Єдина конфігурація (утиліти) | `config/gmail_ai_config.json` | `utilities/config_manager.py` | Якщо файлу немає, використовуються значення за замовчуванням |
| Правила класифікації, словник спаму | у коді `core/email_classifier.py` | — | Змінюються редагуванням коду або через `add_custom_rule` |

> **Увага.** Існують дві окремі системи конфігурації (`master_config.json` і `config/gmail_ai_config.json`), які не об’єднані. Перед зміною параметра перевірте, який модуль його фактично читає.

## 2. Облікові дані Gmail

Порядок завантаження: зашифрований файл → `.env` → шаблон (шаблон містить лише заглушки і для роботи не годиться).

| Змінна | Призначення |
|---|---|
| `GMAIL_USER` | Адреса Gmail (також приймається `GMAIL_EMAIL`) |
| `GMAIL_PASS` | Пароль додатка, 16 символів (також приймається `GMAIL_PASSWORD`) |
| `GMAIL_AI_MASTER_PASSWORD` | Майстер-пароль для шифрування/розшифрування облікових даних; якщо не задано, програма запитає його в консолі |

З’єднання з поштою: `imap.gmail.com`, порт `993`, SSL.

## 3. Параметри `master_config.json`

| Розділ | Параметр | За замовчуванням | Опис |
|---|---|---|---|
| `processing` | `batch_size` | `10` | Листів у пакеті |
| | `processing_interval` | `300` | Інтервал обробки, секунд |
| | `max_emails_per_batch` | `50` | Максимум листів за пакет |
| `features` | `smart_learning`, `analytics`, `business_intelligence`, `automation`, `security_monitoring` | `true` | Вмикання модулів |
| `thresholds` | `confidence_threshold` | `0.7` | Мінімальна впевненість класифікації |
| | `security_risk_threshold` | `50` | Оцінка ризику (0–100), за якої піднімається сповіщення |
| | `auto_retrain_feedback_count` | `15` | Кількість відгуків для перенавчання (див. примітку нижче) |
| `notifications` | `high_risk_security`, `dot_compliance_issues`, `overdue_invoices`, `system_errors` | `true` | Типи сповіщень |
| `automation` | `auto_label`, `auto_star_important`, `auto_archive_spam`, `create_tasks` | `true` | Автоматичні дії |
| `business_rules` | `rate_confirmation_priority` | `"high"` | Пріоритет підтверджень ставки |
| | `dot_compliance_escalation`, `invoice_tracking`, `linkedin_auto_archive` | `true` | Бізнес-правила |

## 4. Додаткові параметри `config/gmail_ai_config.json`

Значення за замовчуванням із `utilities/config_manager.py`. Файл можна задати частково: решта параметрів береться зі значень за замовчуванням.

| Розділ | Параметр | За замовчуванням |
|---|---|---|
| `processing` | `max_processing_time` | `30` (секунд на лист) |
| `features` | `mobile_api` | `true` |
| `security` | `encrypt_credentials` | `true` |
| | `enable_audit_logging` | `true` |
| `notifications` | `email_notifications` | `false` |
| `automation` | `enable_scheduling` | `true` |
| `business_rules` | `freight_keywords` | `freight, shipping, logistics, trucking, load, dispatch, rate confirmation, ratecon, carrier` |
| `database` | `path` | `gmail_ai_unified.db` |
| | `backup_enabled` / `backup_interval` | `true` / `24` (годин) |
| `logging` | `level` | `INFO` |
| | `file`, `max_size`, `backup_count` | `logs/gmail_ai.log`, `10` МБ, `5` |
| `gui` | `theme`, `window_size`, `auto_save` | `light`, `[1200, 800]`, `true` |

## 5. Значення, закладені в коді

| Параметр | Значення | Де |
|---|---|---|
| Поріг спаму | `score > 0.8`, де `score = min(n / 24 × 2, 1.0)`; фактично потрібно ≥ 10 різних індикаторів із 24 | `core/email_classifier.py` |
| Поріг впевненості самонавчального класифікатора | `0.7` | `smart_learning_classifier.py` |
| Перевірка перенавчання | на кожному 50-му відгуку; перенавчання, якщо за останню годину ≥ 100 відгуків або ≥ 10 виправлень із часткою понад 60 %; не частіше, ніж раз на 5 хвилин | `smart_learning_classifier.py` |
| Адреса API | `0.0.0.0:5000`, `debug=False` у функції, але `debug=True` при запуску `python mobile_api.py` | `mobile_api.py` |
| Журнали | `logs/gmail_ai.log`, ротація 10 МБ × 5 | `utilities/logger.py` |

> **Примітка.** `auto_retrain_feedback_count` (15) задається в обох конфігураціях, але в логіці перенавчання не використовується: там жорстко закладені значення з таблиці вище. Зміна цього параметра на поведінку не вплине.

## 6. Файли даних, що створюються під час роботи

Створюються в поточному каталозі при першому запуску відповідних модулів:

| Файл | Модуль |
|---|---|
| `smart_learning.db`, `smart_model.pkl` | самонавчальний класифікатор |
| `email_analytics.db` | аналітика |
| `business_intelligence.db` | бізнес-дані |
| `automation.db` | автоматизація |
| `security_compliance.db` | безпека |
| `gmail_ai_unified.db` | `utilities/database_manager.py` |
| `logs/gmail_ai.log` | журнал |

Усі вони виключені з Git (`.gitignore`). Робіть їхні резервні копії окремо (див. [DEPLOYMENT.md](DEPLOYMENT.md)).

## 7. Рекомендовані налаштування для безпечного першого запуску

- `automation.auto_archive_spam` → `false`, поки не перевірено якість класифікації;
- `automation.create_tasks` → `false`, якщо інтеграція із завданнями не потрібна;
- у GUI починайте з режиму **DEMO**;
- API запускайте лише на `127.0.0.1` (див. [DEPLOYMENT.md](DEPLOYMENT.md)).

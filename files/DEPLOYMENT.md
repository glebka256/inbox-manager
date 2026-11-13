# Розгортання

Система розрахована на **локальне використання на одному комп’ютері** (GUI + бази SQLite). Розгортання REST API на сервері можливе, але потребує додаткових заходів, бо API в поточному вигляді не має автентифікації (див. [SECURITY.md](../SECURITY.md)).

## 1. Вимоги до середовища

| Компонент | Вимога |
|---|---|
| ОС | Windows 10/11, Linux, macOS |
| Python | 3.12 або новіший (через `numpy==2.5.1`) |
| Tkinter | Для GUI (`sudo apt install python3-tk` у Ubuntu/Debian) |
| Мережа | Вихідний доступ до `imap.gmail.com:993` |
| Диск | Місце для баз SQLite, моделі й журналів (зростає з кількістю оброблених листів) |
| Пароль додатка Gmail | Потрібен двоетапний вхід у Google-акаунті |

Перевірка Python: `python --version`.

## 2. Варіант A. Локальне розгортання (рекомендований)

```bash
git clone https://github.com/glebka256/inbox-manager.git
cd inbox-manager
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp credentials/gmail_credentials_template.env credentials/gmail_credentials.env
# відредагуйте файл: GMAIL_USER і GMAIL_PASS (пароль додатка)

python visual_advanced_gui.py
```

Не запускайте програму з інших каталогів: бази й журнали створюються в поточному каталозі.

### Автозапуск у Windows

`LAUNCH_DARK_GUI.bat` запускає `visual_advanced_gui.py` без вікна консолі й шукає інтерпретатор у `.venv` або `gmail_ai_env`. Ярлик на нього можна покласти в каталог автозавантаження (`Win + R` → `shell:startup`).

## 3. Варіант B. REST API на сервері Linux

### 3.1. Порядок дій

1. Встановіть програму як у варіанті A на сервері, окремим користувачем без прав адміністратора.
2. Встановіть WSGI-сервер (у `requirements.txt` його немає):

   ```bash
   pip install gunicorn        # Linux/macOS
   # або на Windows:
   pip install waitress
   ```

3. Покладіть у корінь репозиторію файл `wsgi.py` (є серед згенерованих файлів). Він запускає планувальник автоматизації, який у режимі WSGI не стартує сам:

   ```python
   from mobile_api import app, automation

   automation.start_scheduler()
   ```

4. Запустіть **з одним воркером** (SQLite і планувальник не розраховані на кілька процесів) і лише на локальній адресі:

   ```bash
   gunicorn -w 1 -b 127.0.0.1:5000 wsgi:app
   # Windows:
   waitress-serve --listen=127.0.0.1:5000 wsgi:app
   ```

   Не використовуйте `python mobile_api.py` на сервері: він вмикає `debug=True` і слухає `0.0.0.0`.

5. Перевірте: `curl http://127.0.0.1:5000/api/status`.

### 3.2. Служба systemd

`/etc/systemd/system/inbox-manager.service`:

```ini
[Unit]
Description=Gmail AI Manager API
After=network-online.target

[Service]
User=inboxmgr
WorkingDirectory=/opt/inbox-manager
EnvironmentFile=/etc/inbox-manager.env
ExecStart=/opt/inbox-manager/.venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 wsgi:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

У `/etc/inbox-manager.env` (права `600`, власник `root`) вкажіть:

```
GMAIL_AI_MASTER_PASSWORD=<майстер-пароль для шифрування облікових даних>
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now inbox-manager
sudo journalctl -u inbox-manager -f
```

### 3.3. Зворотний проксі з TLS і автентифікацією

Поки API не має власної автентифікації, її має забезпечити проксі. Приклад для nginx (HTTP Basic; створіть файл паролів: `htpasswd -c /etc/nginx/.htpasswd user`):

```nginx
server {
    listen 443 ssl;
    server_name mail.example.com;

    ssl_certificate     /etc/letsencrypt/live/mail.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mail.example.com/privkey.pem;

    location /api/ {
        auth_basic           "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass           http://127.0.0.1:5000;
        proxy_set_header     Host $host;
        proxy_set_header     X-Forwarded-For $remote_addr;
    }
}
```

Це тимчасовий захід. Автентифікацію слід реалізувати в самому застосунку.

## 4. Варіант C. Docker (приклад, не перевірявся)

Лише для API; GUI в контейнері не працює.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
RUN useradd -m app && mkdir -p /app/logs /app/data && chown -R app /app
USER app
EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "wsgi:app"]
```

```bash
docker build -t inbox-manager .
docker run -d --name inbox-manager \
  -p 127.0.0.1:5000:5000 \
  -v inbox-data:/app \
  --env-file ./inbox.env \
  inbox-manager
```

Облікові дані не копіюйте в образ: передавайте через змінні середовища або том. Перед використанням додайте файл `.dockerignore` з рядками `.git`, `.venv`, `credentials/*.env`, `*.db`, `data/`.

## 5. Резервне копіювання

Резервуйте:

- `*.db` (див. список у [CONFIGURATION.md](CONFIGURATION.md));
- `smart_model.pkl`;
- `master_config.json` і `config/gmail_ai_config.json`;
- `credentials/gmail_credentials.encrypted` (якщо використовується).

Приклад для Linux (за cron раз на добу):

```bash
tar czf /backups/inbox-$(date +%F).tgz -C /opt/inbox-manager \
    --wildcards '*.db' smart_model.pkl master_config.json config credentials/*.encrypted
```

Зупиніть службу або виконайте копіювання у період простою, щоб не пошкодити відкриті бази SQLite.

## 6. Оновлення і відкат

```bash
cd /opt/inbox-manager
sudo systemctl stop inbox-manager
# резервна копія (розділ 5)
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl start inbox-manager
curl http://127.0.0.1:5000/api/status
```

Після оновлення залежностей перевірте, що завантажується `smart_model.pkl`: модель, збережена в одній версії scikit-learn, може не відкриватися в іншій. Якщо не відкривається, її потрібно перенавчити. Відкат: `git checkout <попередній коміт>`, повторне встановлення залежностей і відновлення копії баз.

## 7. Моніторинг

| Що | Як |
|---|---|
| Працездатність | `GET /api/status` (очікується `200` і `"status": "running"`) |
| Журнали застосунку | `logs/gmail_ai.log` (ротація 10 МБ × 5) |
| Журнали служби | `journalctl -u inbox-manager` |
| Помилки обробки | Сповіщення `GET /api/notifications` |

## 8. Перевірка після розгортання

- [ ] `GET /api/status` повертає `200`
- [ ] Запит без автентифікації через зовнішню адресу відхиляється
- [ ] Порт `5000` недоступний ззовні (лише через проксі)
- [ ] Debug вимкнено (відповідь на помилку не містить трасування)
- [ ] У журналі немає паролів і повного тексту листів
- [ ] Резервна копія створюється і відновлюється
- [ ] Автоматичне видалення вимкнено до перевірки якості класифікації

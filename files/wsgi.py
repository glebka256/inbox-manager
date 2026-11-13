"""WSGI-точка входу для запуску REST API через gunicorn/waitress.

Запуск (один воркер, лише локальна адреса):
    gunicorn -w 1 -b 127.0.0.1:5000 wsgi:app
    waitress-serve --listen=127.0.0.1:5000 wsgi:app   # Windows

Не використовуйте `python mobile_api.py` на сервері: він вмикає debug=True.
"""
from mobile_api import app, automation

# У режимі WSGI планувальник автоматизації сам не стартує
automation.start_scheduler()

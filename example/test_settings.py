import logging
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend

logging.disable(logging.CRITICAL)

DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '.sqlite-test-db',
    },
    'crate': {
        'ENGINE': 'django_crate.backend',
        'HOST': 'localhost',
        'PORT': 5432,
        'NAME': None,
    },
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

class TestEmailBackend(BaseEmailBackend):
    def send_messages(self, messages):
        mail.outbox.extend(messages)
        return len(messages)

EMAIL_BACKEND='conf.TestEmailBackend'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

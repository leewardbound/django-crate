import logging
logging.disable(logging.CRITICAL)
DEBUG = False
DATABASES = {'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '.sqlite-test-db',
    },
    'crate': {
        'ENGINE': 'django_crate.backend',
        'SERVERS': ['test_crate:4200',],
    },
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
from django.core.mail.backends.base import BaseEmailBackend
from django.core import mail
class TestEmailBackend(BaseEmailBackend):
    def send_messages(self, messages):
        mail.outbox.extend(messages)
        return len(messages)
EMAIL_BACKEND='conf.TestEmailBackend'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

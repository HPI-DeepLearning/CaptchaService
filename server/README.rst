A Captcha Service implemented in Django REST Framework using Python2
Installation
------------

Install with pip::

    pip install -r requirements.txt
    # create encryption keys for captcha results
    mkdir keys
    keyczart create --location=keys --purpose=crypt
    keyczart addkey --location=keys --status=primary --size=256
    cd api
    python manage.py migrate

Run
---

    python manage.py db_seed
    python manage.py runserver

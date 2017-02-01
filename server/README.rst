A Captcha Service implemented in Django REST Framework using Python2

Installation
------------

Install with pip::

    (sudo) pip install -r requirements.txt
    # create encryption keys for captcha results
    mkdir keys
    keyczart create --location=keys --purpose=crypt
    keyczart addkey --location=keys --status=primary --size=256
    cd api
    python manage.py migrate

Run
---
Run with manage.py::

    put the icdar_words, brontosaurus and platypus folder in the root project directory
    python manage.py db_seed
    python manage.py collectstatic
    python manage.py createsuperuser
    python manage.py runserver

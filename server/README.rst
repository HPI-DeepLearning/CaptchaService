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

Post-Installation
------------

Now start your server, visit your admin pages (e.g. http://localhost:8000/admin/) and follow these steps:

1. Add a Site for your domain, matching settings.SITE_ID (django.contrib.sites app).
2. For each OAuth based provider, add a Social App (socialaccount app).
3. Fill in the site and the OAuth app credentials obtained from the provider.

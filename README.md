# Mad Wreckin' Dolls

* website
* registration
* billing tools

### Required packages

We're currently on the bleeding edge:

* pip install git+git://github.com/django/django.git@1.5b2#egg=django
* pip install pip install MySQL-python
* pip install South
* pip install git+https://github.com/django/django-localflavor-us.git
* pip install django-crispy-forms
* pip install stripe
* pip install gunicorn

### Nginx + Supervisord + gunicorn

We use gunicorn to serve Django/FastCGI pages. See mwd/gunicorn.conf.py and nginx.conf in this repository.

Supervisord configuration:

    root@toupee:/etc/supervisor/conf.d# cat madwreckindolls.com.conf 

    [program:madwreckindolls]
    command=/home/mwd/.virtualenvs/mwd/bin/gunicorn_django -c /home/mwd/madwreckindolls.com/gunicorn.conf.py
    directory=/home/mwd/madwreckindolls.com/
    user=mwd
    autostart=true
    autorestart=true
    redirect_stderr=true





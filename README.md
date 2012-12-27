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

We use gunicorn to serve Django/FastCGI pages. See gunicorn.conf.py in this repository.

Supervisord configuration:

    root@toupee:/etc/supervisor/conf.d# cat madwreckindolls.com.conf 

    [program:madwreckindolls]
    command=/home/mwd/.virtualenvs/mwd/bin/gunicorn_django -c /home/mwd/madwreckindolls.com/gunicorn.conf.py
    directory=/home/mwd/madwreckindolls.com/
    user=mwd
    autostart=true
    autorestart=true
    redirect_stderr=true

nginx configuration:

    upstream mwd_server {
            # server unix:/home/mwd/gunicorn.sock fail_timeout=5;
            server 127.0.0.1:9001 fail_timeout=5;
    }

    server {
            listen 80;
            server_name  www.madwreckindolls.com;
            rewrite ^(.*) http://madwreckindolls.com$1 permanent;
            access_log off;
    }

    server {
            listen 80;
            client_max_body_size 4G;
            server_name madwreckindolls.com;

            access_log /var/log/nginx/madwreckindolls.com.access.log;
            error_log /var/log/nginx/madwreckindolls.com.error.log;

            keepalive_timeout 5;

            # path for static files
            root /home/mwd/madwreckindolls.com/static/;

            location / {
                # checks for static file, if not found proxy to app
                try_files $uri @proxy_to_app;
            }

            location @proxy_to_app {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $http_host;
                proxy_redirect off;

                proxy_pass   http://mwd_server;
            }

            #error_page 500 502 503 504 /500.html;
            #location = /500.html {
            #    root /path/to/app/current/public;
            #}
    }


### Settings

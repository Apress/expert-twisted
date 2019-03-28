from django import http, conf
from django.conf import urls
from django.core import wsgi

def index(request):
    return http.HttpResponse('Hello World')


urlpatterns = (
    urls.url(r'^$', index),
)

conf.settings.configure(
    DEBUG=True,
    SECRET_KEY='thisisthesecretkey',
    ROOT_URLCONF=__name__,
)

application = wsgi.get_wsgi_application()

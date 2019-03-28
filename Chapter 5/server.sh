python -c '
from wsgiref import simple_server
import pyramid_hello
simple_server.make_server(
       "127.0.0.1",
       8000,
       pyramid_hello.application
).serve_forever()
'

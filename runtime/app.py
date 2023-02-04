import logging 
import os
import sys
import json
import leangle
from chalice import Chalice, CORSConfig, Response
from chalice.app import ConvertToMiddleware
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
if 'LAMBDA_TASK_ROOT' in os.environ:
  from chalice_utils.swagger import TemplatedSwaggerGenerator #noqa
  from chalice_utils.planner import PlanEncoder #noqa
else:
  from chalice.deploy.swagger import TemplatedSwaggerGenerator
  from chalice.deploy.planner import PlanEncoder
from dotenv import load_dotenv

load_dotenv()

from chalicelib.authorizer import auth_blueprint
from chalicelib.api.user import auth_routes
from chalicelib.api.note import note_routes
from alembic.config import main 

app = Chalice(app_name='TU Feb 2023 <Mina>')
app.debug = True
logger = Logger()
app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))
tracer = Tracer()
app.register_middleware(ConvertToMiddleware(tracer.capture_lambda_handler))


app.register_blueprint(auth_blueprint)
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(note_routes, url_prefix='/notes')
app.log.setLevel(logging.DEBUG)

if os.getenv('RUN_MIGRATE', 'True') == 'True':
    sys.argv = "alembic -c ./chalicelib/alembic.ini upgrade heads".split()
    main()

@app.middleware('http')
def inject_route_info(event, get_response):
    logger.structure_logs(append=True, request_path=event.path)
    return get_response(event)

cors_config = CORSConfig(
    allow_origin='*',
    allow_headers=['X-Special-Header'],
    max_age=600,
    expose_headers=['X-Special-Header'],
    allow_credentials=True
)

@leangle.describe.tags(["Healthcheck"])
@app.route('/healthcheck', methods=['GET'], cors=True)
def index():
    return {'status': 'healthy'}

def get_base_url(current_request):
    headers = current_request.headers
    if 'x-forwarded-host' in headers:
      host = headers['x-forwarded-host']
    else:
      host = headers['host']
    base_url = '%s://%s' % (headers.get('x-forwarded-proto', 'http'), host)
    if 'stage' in current_request.context:
        base_url = '%s/%s' % (base_url, current_request.context.get('stage'))
    return base_url

@leangle.describe.tags(["Swaggers"])
@app.route("/docs")
def docs():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <meta
            name="description"
            content="SwaggerUI"
          />
          <title>SwaggerUI</title>
          <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
        </head>
        <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js" crossorigin></script>
        <script>
          window.onload = () => {
            window.ui = SwaggerUIBundle({
              url: '%s/openapi.json',
              dom_id: '#swagger-ui',
            });
          };
        </script>
        </body>
        </html>
    """%(get_base_url(app.current_request))
    return Response(body=html, status_code=200, headers={"Content-Type": "text/html"})


@leangle.describe.tags(["Swaggers"])
@app.route("/openapi.json")
def openapi():
    swagger_generator = TemplatedSwaggerGenerator()
    model = swagger_generator.generate_swagger(app)
    output = json.loads(json.dumps(model, indent=4, cls=PlanEncoder))
    return output

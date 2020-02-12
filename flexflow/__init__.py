from flask import Flask
from flexflow.dbengines.sqlchemy.models import db, migrate

def create_app(config_map_list=None, blue_print_list=None):
    app = Flask(__name__)
    if config_map_list:
        for m in config_map_list:
            app.config.update(m)
    db.init_app(app)
    with app.app_context():

        if db.engine.url.drivername == 'pymysql':
            migrate.init_app(app, db,  render_as_batch=True)
        else:
            migrate.init_app(app, db )
    
    if blue_print_list:
        for bp in blue_print_list:
            app.register_blueprint(bp)
    
    return app
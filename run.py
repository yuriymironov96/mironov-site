#!/usr/bin/env python
import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)

#coverage tests
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import User, Role, Post, Comment, Tag, Tag_Post_Relate
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
print os.getenv('FLASK_CONFIG')
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """
    Shell context settings: add new entities to work with them via terminal.
    """
    return dict(app=app, db=db, User=User, Role=Role, Post=Post,
                Comment=Comment, Tag=Tag, TPR=Tag_Post_Relate)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """
    Run the unit tests. They require declared config variables.
    """
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database
    # migrate database to latest revision
    engine = create_engine(os.environ.get('DATABASE_URL'))
    if not database_exists(engine.url):
        create_database(engine.url)
        db.create_all()
    upgrade()
    # create user roles
    Role.insert_roles()

@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
        profile_dir=profile_dir)
    app.run()

if __name__ == '__main__':
    manager.run()

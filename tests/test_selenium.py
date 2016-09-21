import unittest
from selenium import webdriver

class SeleniumTestCase(unittest.TestCase):

    client = None

    @classmethod
    def setUpClass(cls):

        # start Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:

            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            # add an administrator user
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='john@example.com',
            username='john', password='cat',
            role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()
            # destroy database
            db.drop_all()
            db.session.remove()
            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

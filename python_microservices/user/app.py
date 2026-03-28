from flask import Flask

#initialize the application
app = Flask(__name__)

#database configuration
app.config['SECRET_KEY'] = '' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize the database
models.init_app(app)

#import the routes
app.register_blueprint(routes.user_blueprint)

#run the application
app.run()
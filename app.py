from flask import Flask, render_template, request, session, flash, redirect, url_for
import mysql.connector
from mysql.connector import Error
import random as rand
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.secret_key = str(rand.randint(1, 1000000))


# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'inlamning_1'  
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

def set_up_logging():
    """Set up logging for the application."""
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Create a rotating file handler for logging, keeps the 10 most recent logs
    # removing the oldest when the log file exceeds 10KB
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    
    # sets up the log format (how the log messages will appear in the log file)
    file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
    # Set the logging level to INFO
    file_handler.setLevel(logging.INFO)

    # Add the handler to the app logger
    app.logger.addHandler(file_handler)

    # Set the overall logging level for the app
    app.logger.setLevel(logging.INFO)

    # Log that the app has started
    app.logger.info('Flask Error Handling Demo startup')

@app.route('/')
def index():
    if not "logged_in" in session or not session['logged_in']:
        return render_template('login.html')      
    else: 
        return render_template('index.html')

    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Hantera utloggning - rensa session
    print("DEBUG: /logout reached, method=", request.method)
    session.clear()
    flash('Du har loggats ut', 'info')
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':        
        username = request.form['username']
        password = request.form['password']

        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)

            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()         
            
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            if user and user['password'] == password:
                session['logged_in'] = True
                session['username'] = user['username']
                session['password'] = user['password']

                flash('Inloggning lyckades!', 'success')
                return redirect(url_for('index'))
                
            else:  
                flash('Ogiltigt användarnamn eller lösenord', 'error')
                return render_template('login.html'), 401

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@app.route('/test500error')
def test_500_error():
    """Route to deliberately raise a 500 error for testing purposes"""
    a = 1 / 0  # This will raise a ZeroDivisionError
    return f'Result: {a}'

@app.errorhandler(404)
def not_found_error(error):
    """Custom 404 error handler"""
    app.logger.warning(f'404 error: {request.url}')
    
    # it is posible to render a template and return a status code other than 200
    return render_template('errors/404.html'), 404 # 404 is the status code for not found errors

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error handler"""
    app.logger.error(f'Internal server error: {error}')
    return render_template('errors/500.html'), 500 # 500 is the status code for internal server error

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle any unhandled exceptions"""
    app.logger.error(f'Unhandled exception: {error}', exc_info=True)
    return render_template('errors/500.html'), 500 # 500 is the status code for internal server error

if __name__ == '__main__':
    set_up_logging()
    app.run(debug=True)
from flask import Flask, render_template, request, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '123321'  # TODO: Ändra detta till en slumpmässig hemlig nyckel

# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'masterkey',
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

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # hantera POST request från inloggningsformuläret
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
            cursor.execute(query, (username, password))
            user = cursor.fetchone()            
            
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            if user['password'] == password and user['username'] == username:
                session['logged_in'] = True
                session['username'] = user['username']
                session['password'] = user['password']
                return f'Inloggning lyckades! Välkommen {user["username"]}!'
            else:  
                return ('Ogiltigt användarnamn eller lösenord', 401)

            # Om lösenordet är korrekt så sätt sessionsvariabler och skicka tillbaka en hälsning med användarens namn.

            if user: # TODO: gör klart villkoret
                # Inloggning lyckades - spara användarinfo i session
            #    ... # TODO: spara i sessionen
                return f'Inloggning lyckades! Välkommen {...}!'
            else:
                return ('Ogiltigt användarnamn eller lösenord', 401)

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app.run(debug=True)
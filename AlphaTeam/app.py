from flask import Flask, request, redirect, url_for, render_template, session, flash, get_flashed_messages
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="project"
    )


def init_db():
    with connect_db() as db:
        cursor = db.cursor()
        db.commit()


#for login and Register
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'login':
            email = request.form['email']
            password = request.form['password']
            if check_credentials(email, password):
                return redirect(url_for('booking'))
            else:
                return redirect(url_for('wrong'))
        elif action == 'register':
            return redirect(url_for('register'))
    return render_template('index.html')



#For Checking Credintials
def check_credentials(email, password):
  with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT Name, Email,Gender FROM register WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['Name'] = user[0]
            session['Email'] = user[1]
            session['Gender'] = user[2]
        return user is not None
  
  #for Registering And saving data in SQL register Table
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']

        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO register (Name, Gender, Email, Password) VALUES (%s, %s, %s, %s)',
                           (name,gender,email, password))
            db.commit()
        return redirect(url_for('index'))
    return render_template('register.html')



# To redirect To booking Page
@app.route('/booking')
def booking():
    return render_template('booking.html')



#after Click on booking
@app.route('/Booking', methods=['POST'])
def Booking():
    source = request.form['source'].strip().lower()
    destination = request.form['destination'].strip().lower()
    date = request.form['date']
    session['source'] = source
    session['destination'] = destination
    session['date'] = date

    records = search_buses(source, destination)

    if not records:
        flash("No buses found for the selected route. Please try again.")
        return redirect(url_for('ifnot'))

    return render_template('buslist.html', records=records)

#searching for buses available
def search_buses(source, destination):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = ("SELECT bus_name, bus_type, ticket_price "
                 "FROM buslist WHERE LOWER(source) = %s AND LOWER(destination) = %s")
        cursor.execute(query, (source, destination))
        records = cursor.fetchall()
        cursor.close()
        db.close()
        return records

    except Error as e:
        print("Error while connecting to MySQL", e)
        return []
    


#For booking check seat Availaibility
def check_seat_availability(bus_name):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT SUM(total_seats) FROM booking_details WHERE bus_name = %s', (bus_name,))
        total_booked_seats = cursor.fetchone()[0] or 0  
    return total_booked_seats


#Book The seat
@app.route('/book', methods=['POST'])
def book():
    source = session.get('source')
    destination = session.get('destination')
    date = session.get('date')
    Name = session.get('Name')
    Email = session.get('Email')
    bus_name = request.form['bus_name']
    bus_type = request.form['bus_type']
    seats_book = int(request.form['seats_book'])
    ticket_price = float(request.form['ticket_price'])
    
    booked_tickets = check_seat_availability(bus_name)
    max_seats = 40 
    
    if booked_tickets + seats_book > max_seats:
        flash("Seats are Full")
        return redirect(url_for('error')) 
    
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO booking_details (source, destination, date, bus_name, bus_type, total_seats, ticket_price) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (source, destination, date, bus_name, bus_type, seats_book, ticket_price)
        )
        db.commit()

    # Store booking details in session
    session['booking_details'] = {
        'Email': Email,
        'Name': Name,
        'date': date,
        'source': source,
        'destination': destination,
        'bus_name': bus_name,
        'bus_type': bus_type,
        'total_tickets': seats_book,
        'total_price': f"Rs{ticket_price * seats_book}"
    }

    return redirect(url_for('confirm'))



@app.route('/confirm')
def confirm():
    booking_details = session.get('booking_details', {})
    return render_template('confirm.html', **booking_details)



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/home')
def home():
    return render_template('index.html')



#checking Admin Creditials
def check_admin(email, password):
  with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT username, password FROM admin WHERE username = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        return user is not None


#for admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'login':
            email = request.form['email']
            password = request.form['password']
            if check_admin(email, password):
                return redirect(url_for('addbus'))
            else:
                return redirect(url_for('wrong'))
        elif action == 'register':
            return redirect(url_for('register'))
    return render_template('index.html')



@app.route('/wrong')
def wrong():
    return render_template('wrong.html')


#For addbus funtionality
@app.route('/addbus', methods=['GET', 'POST'])
def addbus():
    if request.method == 'POST':
        source=request.form['source']
        destination=request.form['destination']
        busname = request.form['busname']
        bus_type = request.form['bus_type']
        total_seats = request.form['total_seats']
        price = request.form['price']
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO buslist (source, destination, bus_name, bus_type, total_seats, ticket_price) VALUES (%s, %s, %s, %s, %s, %s)',
                           (source, destination, busname,bus_type,total_seats,price))
            db.commit()
        return redirect(url_for('addbus'))

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT source, destination,bus_name, bus_type, total_seats, ticket_price FROM buslist")
        buses = cursor.fetchall()

    return render_template('addbus.html', buses=buses)


@app.route('/goregister')
def goregister():
    return render_template('register.html')


@app.route('/admin_page')
def admin_page():
    return render_template('admin.html')


@app.route('/error')
def error():
    return render_template('error.html')




if __name__ == '__main__':
    init_db()
    app.run(debug=True)
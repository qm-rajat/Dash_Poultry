import os
import sqlite3
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), 'dash_poultry.db')
ADMIN_USERNAME = 'a'
ADMIN_PASSWORD = 'a'

# Try to use SQLCipher, fallback to sqlite3
try:
    import pysqlcipher3.dbapi2 as sqlcipher
    USE_SQLCIPHER = True
except ImportError:
    USE_SQLCIPHER = False

def get_connection():
    if USE_SQLCIPHER:
        conn = sqlcipher.connect(DB_PATH)
        conn.execute("PRAGMA key = 'dashpoultry_secret_key';")
        return conn
    else:
        return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    # Batches table
    c.execute('''CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT UNIQUE NOT NULL,
        num_chicks INTEGER,
        breed TEXT,
        date_in TEXT,
        expected_out TEXT,
        mortality_rate REAL
    )''')
    # Feed logs
    c.execute('''CREATE TABLE IF NOT EXISTS feed_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        date TEXT,
        quantity_kg REAL
    )''')
    # Water logs
    c.execute('''CREATE TABLE IF NOT EXISTS water_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        date TEXT,
        quantity_l REAL
    )''')
    # Expenses
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT,
        payment_method TEXT
    )''')
    
    # Add missing columns if they don't exist (for existing databases)
    try:
        c.execute('ALTER TABLE expenses ADD COLUMN description TEXT')
    except:
        pass  # Column already exists
    try:
        c.execute('ALTER TABLE expenses ADD COLUMN payment_method TEXT')
    except:
        pass  # Column already exists
    # Revenue
    c.execute('''CREATE TABLE IF NOT EXISTS revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        batch_id TEXT,
        amount REAL
    )''')
    # Mortality
    c.execute('''CREATE TABLE IF NOT EXISTS mortality (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        date TEXT,
        count INTEGER,
        reason TEXT
    )''')
    # Vaccinations
    c.execute('''CREATE TABLE IF NOT EXISTS vaccinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        date TEXT,
        vaccine TEXT,
        status TEXT
    )''')
    # Workers
    c.execute('''CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        role TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        salary REAL,
        hire_date TEXT,
        status TEXT
    )''')
    # Insert default admin if not present
    c.execute('SELECT * FROM admin WHERE username=?', (ADMIN_USERNAME,))
    if not c.fetchone():
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt())
        c.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (ADMIN_USERNAME, hashed))
    # Insert sample data if tables are empty
    c.execute('SELECT COUNT(*) FROM batches')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO batches (batch_id, num_chicks, breed, date_in, expected_out, mortality_rate) VALUES ('B001', 500, 'Broiler', '2024-06-01', '2024-08-01', 0.02)")
        c.execute("INSERT INTO batches (batch_id, num_chicks, breed, date_in, expected_out, mortality_rate) VALUES ('B002', 400, 'Layer', '2024-06-15', '2024-09-15', 0.01)")
    c.execute('SELECT COUNT(*) FROM feed_logs')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO feed_logs (batch_id, date, quantity_kg) VALUES ('B001', '2024-06-01', 50)")
        c.execute("INSERT INTO feed_logs (batch_id, date, quantity_kg) VALUES ('B001', '2024-06-02', 48)")
        c.execute("INSERT INTO feed_logs (batch_id, date, quantity_kg) VALUES ('B002', '2024-06-15', 40)")
    c.execute('SELECT COUNT(*) FROM water_logs')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO water_logs (batch_id, date, quantity_l) VALUES ('B001', '2024-06-01', 300)")
        c.execute("INSERT INTO water_logs (batch_id, date, quantity_l) VALUES ('B001', '2024-06-02', 320)")
        c.execute("INSERT INTO water_logs (batch_id, date, quantity_l) VALUES ('B002', '2024-06-15', 250)")
    c.execute('SELECT COUNT(*) FROM expenses')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO expenses (date, category, amount, description, payment_method) VALUES ('2024-06-01', 'Feed', 100, 'Broiler feed for B001 batch', 'Cash')")
        c.execute("INSERT INTO expenses (date, category, amount, description, payment_method) VALUES ('2024-06-02', 'Electricity', 30, 'Monthly electricity bill', 'Bank Transfer')")
        c.execute("INSERT INTO expenses (date, category, amount, description, payment_method) VALUES ('2024-06-15', 'Medicine', 50, 'Vaccines and medicines', 'Cash')")
        c.execute("INSERT INTO expenses (date, category, amount, description, payment_method) VALUES ('2024-06-20', 'Labor', 5000, 'Worker salary payment', 'Bank Transfer')")
        c.execute("INSERT INTO expenses (date, category, amount, description, payment_method) VALUES ('2024-06-25', 'Equipment', 1500, 'New feeding equipment', 'UPI')")
    else:
        # Update existing records to have description and payment_method if they're NULL
        c.execute("UPDATE expenses SET description = 'Feed expense' WHERE description IS NULL AND category = 'Feed'")
        c.execute("UPDATE expenses SET description = 'Electricity bill' WHERE description IS NULL AND category = 'Electricity'")
        c.execute("UPDATE expenses SET description = 'Medicine expense' WHERE description IS NULL AND category = 'Medicine'")
        c.execute("UPDATE expenses SET payment_method = 'Cash' WHERE payment_method IS NULL")
    c.execute('SELECT COUNT(*) FROM revenue')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO revenue (date, batch_id, amount) VALUES ('2024-08-01', 'B001', 3000)")
        c.execute("INSERT INTO revenue (date, batch_id, amount) VALUES ('2024-09-15', 'B002', 2500)")
    c.execute('SELECT COUNT(*) FROM mortality')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO mortality (batch_id, date, count, reason) VALUES ('B001', '2024-06-02', 3, 'Sickness')")
        c.execute("INSERT INTO mortality (batch_id, date, count, reason) VALUES ('B002', '2024-06-16', 1, 'Accident')")
    c.execute('SELECT COUNT(*) FROM vaccinations')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO vaccinations (batch_id, date, vaccine, status) VALUES ('B001', '2024-06-05', 'Newcastle Disease', 'Completed')")
        c.execute("INSERT INTO vaccinations (batch_id, date, vaccine, status) VALUES ('B001', '2024-06-20', 'Infectious Bronchitis', 'Scheduled')")
        c.execute("INSERT INTO vaccinations (batch_id, date, vaccine, status) VALUES ('B002', '2024-06-20', 'Marek Disease', 'Completed')")
    c.execute('SELECT COUNT(*) FROM workers')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO workers (worker_id, name, role, phone, email, address, salary, hire_date, status) VALUES ('W001', 'Rajesh Kumar', 'Farm Manager', '9876543210', 'rajesh@farm.com', 'Village Road, District', 25000.00, '2024-01-15', 'Active')")
        c.execute("INSERT INTO workers (worker_id, name, role, phone, email, address, salary, hire_date, status) VALUES ('W002', 'Priya Singh', 'Feeder', '8765432109', 'priya@farm.com', 'Main Street, City', 15000.00, '2024-02-01', 'Active')")
        c.execute("INSERT INTO workers (worker_id, name, role, phone, email, address, salary, hire_date, status) VALUES ('W003', 'Amit Patel', 'Cleaner', '7654321098', 'amit@farm.com', 'Industrial Area, Town', 12000.00, '2024-03-10', 'Active')")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db() 
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = 'gymkey123'
DB = 'gym.db'

PLANS = {
    'Basic':    {'price': 499,  'duration': 30,  'features': 'Gym Access'},
    'Standard': {'price': 999,  'duration': 30,  'features': 'Gym + Cardio'},
    'Premium':  {'price': 1799, 'duration': 90,  'features': 'Gym + Cardio + PT'},
    'Annual':   {'price': 4999, 'duration': 365, 'features': 'All Access + Diet Plan'},
}

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        plan TEXT NOT NULL,
        amount_paid REAL,
        join_date TEXT,
        expiry_date TEXT,
        status TEXT DEFAULT 'Active'
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        check_in TEXT,
        FOREIGN KEY(member_id) REFERENCES members(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        plan TEXT,
        amount REAL,
        payment_date TEXT,
        FOREIGN KEY(member_id) REFERENCES members(id)
    )''')
    db.commit()

    # Seed data
    count = db.execute('SELECT COUNT(*) FROM members').fetchone()[0]
    if count == 0:
        seeds = [
            ('Arjun Sharma',   'arjun@gmail.com',   '9876543210', 24, 'Male',   'Premium',  1799),
            ('Priya Nair',     'priya@gmail.com',   '9123456780', 28, 'Female', 'Standard',  999),
            ('Ravi Kumar',     'ravi@gmail.com',    '9988776655', 32, 'Male',   'Annual',   4999),
            ('Sneha Reddy',    'sneha@gmail.com',   '9871234560', 22, 'Female', 'Basic',     499),
            ('Kiran Patel',    'kiran@gmail.com',   '9765432100', 35, 'Male',   'Premium',  1799),
        ]
        for s in seeds:
            name, email, phone, age, gender, plan, amount = s
            join = date.today() - timedelta(days=10)
            expiry = join + timedelta(days=PLANS[plan]['duration'])
            status = 'Active' if expiry >= date.today() else 'Expired'
            db.execute(
                'INSERT INTO members (name,email,phone,age,gender,plan,amount_paid,join_date,expiry_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)',
                (name, email, phone, age, gender, plan, amount, str(join), str(expiry), status)
            )
        db.commit()

# ── Routes ──────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    today = str(date.today())
    stats = {
        'total':   db.execute('SELECT COUNT(*) FROM members').fetchone()[0],
        'active':  db.execute("SELECT COUNT(*) FROM members WHERE status='Active'").fetchone()[0],
        'expired': db.execute("SELECT COUNT(*) FROM members WHERE status='Expired'").fetchone()[0],
        'revenue': db.execute('SELECT COALESCE(SUM(amount_paid),0) FROM members').fetchone()[0],
        'checkins_today': db.execute("SELECT COUNT(*) FROM attendance WHERE check_in LIKE ?", (today+'%',)).fetchone()[0],
    }
    expiring_soon = db.execute(
        "SELECT * FROM members WHERE expiry_date BETWEEN ? AND ? AND status='Active'",
        (today, str(date.today() + timedelta(days=7)))
    ).fetchall()
    recent = db.execute('SELECT * FROM members ORDER BY id DESC LIMIT 5').fetchall()
    return render_template('index.html', stats=stats, expiring_soon=expiring_soon, recent=recent, plans=PLANS)

@app.route('/members')
def members():
    db = get_db()
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    plan   = request.args.get('plan', '')
    query  = 'SELECT * FROM members WHERE 1=1'
    params = []
    if search:
        query += ' AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)'; params += [f'%{search}%']*3
    if status:
        query += ' AND status=?'; params.append(status)
    if plan:
        query += ' AND plan=?'; params.append(plan)
    query += ' ORDER BY id DESC'
    all_members = db.execute(query, params).fetchall()
    return render_template('members.html', members=all_members, search=search,
                           status=status, plan=plan, plans=PLANS)

@app.route('/member/new', methods=['GET','POST'])
def new_member():
    if request.method == 'POST':
        db = get_db()
        plan = request.form['plan']
        join = date.today()
        expiry = join + timedelta(days=PLANS[plan]['duration'])
        try:
            db.execute(
                'INSERT INTO members (name,email,phone,age,gender,plan,amount_paid,join_date,expiry_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)',
                (request.form['name'], request.form['email'], request.form['phone'],
                 request.form['age'], request.form['gender'], plan,
                 PLANS[plan]['price'], str(join), str(expiry), 'Active')
            )
            mid = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            db.execute('INSERT INTO payments (member_id,plan,amount,payment_date) VALUES (?,?,?,?)',
                       (mid, plan, PLANS[plan]['price'], str(join)))
            db.commit()
            flash('Member enrolled successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'error')
        return redirect(url_for('members'))
    return render_template('form.html', member=None, plans=PLANS)

@app.route('/member/<int:id>/edit', methods=['GET','POST'])
def edit_member(id):
    db = get_db()
    member = db.execute('SELECT * FROM members WHERE id=?', (id,)).fetchone()
    if request.method == 'POST':
        plan = request.form['plan']
        db.execute(
            'UPDATE members SET name=?,email=?,phone=?,age=?,gender=?,plan=?,status=? WHERE id=?',
            (request.form['name'], request.form['email'], request.form['phone'],
             request.form['age'], request.form['gender'], plan,
             request.form['status'], id)
        )
        db.commit()
        flash('Member updated!', 'success')
        return redirect(url_for('members'))
    return render_template('form.html', member=member, plans=PLANS)

@app.route('/member/<int:id>/delete', methods=['POST'])
def delete_member(id):
    db = get_db()
    db.execute('DELETE FROM members WHERE id=?', (id,))
    db.execute('DELETE FROM attendance WHERE member_id=?', (id,))
    db.execute('DELETE FROM payments WHERE member_id=?', (id,))
    db.commit()
    flash('Member removed.', 'info')
    return redirect(url_for('members'))

@app.route('/member/<int:id>/renew', methods=['POST'])
def renew_member(id):
    db = get_db()
    member = db.execute('SELECT * FROM members WHERE id=?', (id,)).fetchone()
    plan = member['plan']
    today = date.today()
    new_expiry = today + timedelta(days=PLANS[plan]['duration'])
    db.execute("UPDATE members SET expiry_date=?,status='Active' WHERE id=?", (str(new_expiry), id))
    db.execute('INSERT INTO payments (member_id,plan,amount,payment_date) VALUES (?,?,?,?)',
               (id, plan, PLANS[plan]['price'], str(today)))
    db.commit()
    flash('Membership renewed!', 'success')
    return redirect(url_for('members'))

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    db = get_db()
    if request.method == 'POST':
        mid = request.form['member_id']
        member = db.execute("SELECT * FROM members WHERE id=? AND status='Active'", (mid,)).fetchone()
        if member:
            db.execute('INSERT INTO attendance (member_id,check_in) VALUES (?,?)',
                       (mid, datetime.now().strftime('%Y-%m-%d %H:%M')))
            db.commit()
            flash(f'{member["name"]} checked in successfully!', 'success')
        else:
            flash('Member not found or membership expired!', 'error')
    today = str(date.today())
    today_log = db.execute(
        "SELECT a.*, m.name, m.plan FROM attendance a JOIN members m ON a.member_id=m.id WHERE a.check_in LIKE ? ORDER BY a.id DESC",
        (today+'%',)
    ).fetchall()
    all_members = db.execute("SELECT id,name,plan FROM members WHERE status='Active' ORDER BY name").fetchall()
    return render_template('attendance.html', today_log=today_log, all_members=all_members)

@app.route('/payments')
def payments():
    db = get_db()
    logs = db.execute(
        'SELECT p.*, m.name FROM payments p JOIN members m ON p.member_id=m.id ORDER BY p.id DESC'
    ).fetchall()
    total = db.execute('SELECT COALESCE(SUM(amount),0) FROM payments').fetchone()[0]
    return render_template('payments.html', logs=logs, total=total)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

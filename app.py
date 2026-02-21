from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
import sqlite3
import hashlib
import os
from datetime import datetime, date
import json
import pandas as pd
from io import BytesIO
import base64
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

def get_db_connection():
    conn = sqlite3.connect('school_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth():
    return 'user_id' in session and 'role' in session

def check_admin():
    return session.get('role') == 'admin'

def check_role(allowed_roles):
    """Check if user has one of the allowed roles"""
    user_role = session.get('role')
    return user_role in allowed_roles

def check_deadline():
    conn = get_db_connection()
    current_date = date.today()
    try:
        deadline = conn.execute('''
            SELECT deadline_date FROM deadlines 
            WHERE is_active = 1 
            ORDER BY deadline_date DESC LIMIT 1
        ''').fetchone()
        conn.close()
        
        if deadline and current_date > datetime.strptime(deadline['deadline_date'], '%Y-%m-%d').date():
            return False
        return True
    except:
        conn.close()
        return True  # If no deadline table or data, allow access

@app.route('/')
def index():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()
        
        if not user_id or not password:
            flash('Please enter both user ID and password', 'error')
            return render_template('login.html')
        
        hashed_password = hash_password(password)  # Hash the input password for comparison
        conn = get_db_connection()
        
        try:
            user = conn.execute('''
                SELECT * FROM users WHERE user_id = ? AND password = ? AND is_active = 1
            ''', (user_id, hashed_password)).fetchone()
            
            if user:
                session['user_id'] = user['user_id']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid user ID or password', 'error')
        except sqlite3.Error as e:
            flash('Database error occurred. Please try again later.', 'error')
            print(f"Database error: {e}")
        finally:
            conn.close()
    
    return render_template('login.html')


#manage streams 
@app.route('/manage_streams', methods=['GET', 'POST'])
def manage_streams():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    if not check_role(['admin', 'headteacher']):
        flash('Access denied. You do not have permission to manage streams.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        # Handle adding or updating streams
        stream_name = request.form.get('stream_name', '').strip()
        class_level = request.form.get('class_level', '').strip()
        
        if not stream_name or not class_level:
            flash('Please provide both class level and stream name.', 'error')
        else:
            try:
                conn.execute('INSERT INTO streams (class_level, stream_name) VALUES (?, ?)', (class_level, stream_name))
                conn.commit()
                flash('Stream added successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Database error: {e}', 'error')
    
    try:
        streams = conn.execute('SELECT * FROM streams ORDER BY class_level, stream_name').fetchall()
    except sqlite3.Error as e:
        streams = []
        flash(f'Database error: {e}', 'error')
    finally:
        conn.close()
    
    return render_template('manage_streams.html', streams=streams)


#manage subjects
@app.route('/manage_subjects', methods=['GET', 'POST'])
def manage_subjects():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    if not check_role(['admin', 'headteacher']):
        flash('Access denied. You do not have permission to manage subjects.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        # Handle adding a new subject
        subject_initial = request.form.get('subject_initial', '').strip()
        subject_full_name = request.form.get('subject_full_name', '').strip()
        
        if not subject_initial or not subject_full_name:
            flash('Please provide both subject initial and full name.', 'error')
        else:
            try:
                conn.execute(
                    'INSERT INTO subjects (subject_initial, subject_full_name) VALUES (?, ?)',
                    (subject_initial, subject_full_name)
                )
                conn.commit()
                flash('Subject added successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Database error: {e}', 'error')
    
    try:
        subjects = conn.execute('SELECT * FROM subjects ORDER BY subject_full_name').fetchall()
    except sqlite3.Error as e:
        subjects = []
        flash(f'Database error: {e}', 'error')
    finally:
        conn.close()
    
    return render_template('manage_subjects.html', subjects=subjects)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/marks_entry')
def marks_entry():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    # Allow admin, headteacher, and teacher roles
    if not check_role(['admin', 'headteacher', 'teacher']):
        flash('Access denied. You do not have permission to access marks entry.', 'error')
        return redirect(url_for('index'))
    
    if not check_deadline() and not check_admin():
        flash('Marks entry deadline has passed. Contact admin.', 'warning')
        return redirect(url_for('index'))
    
    return render_template('marks_entry.html')

@app.route('/report_card')
def report_card():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    # Allow admin, headteacher, and teacher roles
    if not check_role(['admin', 'headteacher', 'teacher']):
        flash('Access denied. You do not have permission to access report cards.', 'error')
        return redirect(url_for('index'))
    
    return render_template('report_card.html')

@app.route('/admin')
def admin_panel():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    if not check_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('admin.html')

@app.route('/library')
def library():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    # Allow admin, librarian, and headteacher roles
    if not check_role(['admin', 'librarian', 'headteacher']):
        flash('Access denied. You do not have permission to access the library system.', 'error')
        return redirect(url_for('index'))
    
    return render_template('library.html')

@app.route('/bursary')
def bursary():
    if not check_auth():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    # Allow admin, bursar, and headteacher roles
    if not check_role(['admin', 'bursar', 'headteacher']):
        flash('Access denied. You do not have permission to access the bursary system.', 'error')
        return redirect(url_for('index'))
    
    return render_template('bursary.html')

@app.route('/api/streams/<class_level>')
def get_streams(class_level):
    if not check_auth():
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = get_db_connection()
    try:
        streams = conn.execute('''
            SELECT DISTINCT stream_name FROM streams WHERE class_level = ?
        ''', (class_level,)).fetchall()
        return jsonify([stream['stream_name'] for stream in streams])
    except sqlite3.Error:
        # If streams table doesn't exist, return default streams
        return jsonify(['A', 'B', 'C', 'D'])
    finally:
        conn.close()

@app.route('/api/load_data', methods=['POST'])
def load_data():
    if not check_auth():
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    class_level = data['class']
    stream = data['stream']
    year = data['year']
    term = data['term']
    
    conn = get_db_connection()
    try:
        students = conn.execute(f'''
            SELECT * FROM {class_level} 
            WHERE stream = ? AND year = ? AND term = ?
            ORDER BY std_no
        ''', (stream, year, term)).fetchall()
        return jsonify([dict(student) for student in students])
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/save_data', methods=['POST'])
def save_data():
    if not check_auth():
        return jsonify({'success': False, 'message': 'Authentication required'})

    data = request.json
    class_level = data.get('class')
    students = data.get('students')

    if not class_level or not students:
        return jsonify({'success': False, 'message': 'Invalid data'})

    conn = get_db_connection()
    try:
        for student in students:
            conn.execute(f'''
                            INSERT INTO {class_level} (std_no, sdt_name, stream, year, term, gender, section, eng1, eng2, eng3, eng4, engBOT, engMOT, engEOT,
                            mtc1, mtc2, mtc3, mtc4, mtcBOT, mtcMOT, mtcEOT,
                            bio1, bio2, bio3, bio4, bioBOT, bioMOT, bioEOT,
                            phy1, phy2, phy3, phy4, phyBOT, phyMOT, phyEOT,
                            geo1, geo2, geo3, geo4, geoBOT, geoMOT, geoEOT,
                            his1, his2, his3, his4, hisBOT, hisMOT, hisEOT,
                            che1, che2, che3, che4, cheBOT, cheMOT, cheEOT,
                            ict1, ict2, ict3, ict4, ictBOT, ictMOT, ictEOT,
                            ent1, ent2, ent3, ent4, entBOT, entMOT, entEOT,
                            cre1, cre2, cre3, cre4, creBOT, creMOT, creEOT,
                            agr1, agr2, agr3, agr4, agrBOT, agrMOT, agrEOT,
                            phe1, phe2, phe3, phe4, pheBOT, pheMOT, pheEOT,
                            kis1, kis2, kis3, kis4, kisBOT, kisMOT, kisEOT,
                            art1, art2, art3, art4, artBOT, artMOT, artEOT,
                            ire1, ire2, ire3, ire4, ireBOT, ireMOT, ireEOT,
                            lit1, lit2, lit3, lit4, litBOT, litMOT, litEOT,
                            tad1, tad2, tad3, tad4, tadBOT, tadMOT, tadEOT,
                            fsn1, fsn2, fsn3, fsn4, fsnBOT, fsnMOT, fsnEOT,
                            lat1, lat2, lat3, lat4, latBOT, latMOT, latEOT,
                            ate1, ate2, ate3, ate4, ateBOT, ateMOT, ateEOT,
                            lum1, lum2, lum3, lum4, lumBOT, lumMOT, lumEOT,
                            lug1, lug2, lug3, lug4, lugBOT, lugMOT, lugEOT,
                            lus1, lus2, lus3, lus4, lusBOT, lusMOT, lusEOT,
                            lba1, lba2, lba3, lba4, lbaBOT, lbaMOT, lbaEOT,
                            lbl1, lbl2, lbl3, lbl4, lblBOT, lblMOT, lblEOT,
                            run1, run2, run3, run4, runBOT, runMOT, runEOT,
                            rut1, rut2, rut3, rut4, rutBOT, rutMOT, rutEOT,
                            fre1, fre2, fre3, fre4, freBOT, freMOT, freEOT,
                            ger1, ger2, ger3, ger4, gerBOT, gerMOT, gerEOT,
                            dho1, dho2, dho3, dho4, dhoBOT, dhoMOT, dhoEOT)   
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(std_no) DO UPDATE SET
                sdt_name = excluded.sdt_name,
                stream = excluded.stream,
                year = excluded.year,
                term = excluded.term,
                gender = excluded.gender,
                section = excluded.section,
                eng1 = excluded.eng1,
                eng2 = excluded.eng2,
                eng3 = excluded.eng3,
                eng4 = excluded.eng4,
                engBOT = excluded.engBOT,
                engMOT = excluded.engMOT,
                engEOT = excluded.engEOT,
                mtc1 = excluded.mtc1,
                mtc2 = excluded.mtc2,
                mtc3 = excluded.mtc3,
                mtc4 = excluded.mtc4,
                mtcBOT = excluded.mtcBOT,
                mtcMOT = excluded.mtcMOT,
                mtcEOT = excluded.mtcEOT,
                bio1 = excluded.bio1,
                bio2 = excluded.bio2,
                bio3 = excluded.bio3,
                bio4 = excluded.bio4,
                bioBOT = excluded.bioBOT,
                bioMOT = excluded.bioMOT,
                bioEOT = excluded.bioEOT,
                phy1 = excluded.phy1,
                phy2 = excluded.phy2,
                phy3 = excluded.phy3,
                phy4 = excluded.phy4,
                phyBOT = excluded.phyBOT,
                phyMOT = excluded.phyMOT,
                phyEOT = excluded.phyEOT,
                geo1 = excluded.geo1,
                geo2 = excluded.geo2,
                geo3 = excluded.geo3,
                geo4 = excluded.geo4,
                geoBOT = excluded.geoBOT,
                geoMOT = excluded.geoMOT,
                geoEOT = excluded.geoEOT,
                his1 = excluded.his1,
                his2 = excluded.his2,
                his3 = excluded.his3,
                his4 = excluded.his4,
                hisBOT = excluded.hisBOT,
                hisMOT = excluded.hisMOT,
                hisEOT = excluded.hisEOT,
                che1 = excluded.che1,
                che2 = excluded.che2,
                che3 = excluded.che3,
                che4 = excluded.che4,
                cheBOT = excluded.cheBOT,
                cheMOT = excluded.cheMOT,
                cheEOT = excluded.cheEOT,
                ict1 = excluded.ict1,
                ict2 = excluded.ict2,
                ict3 = excluded.ict3,
                ict4 = excluded.ict4,
                ictBOT = excluded.ictBOT,
                ictMOT = excluded.ictMOT,
                ictEOT = excluded.ictEOT,
                ent1 = excluded.ent1,
                ent2 = excluded.ent2,
                ent3 = excluded.ent3,
                ent4 = excluded.ent4,
                entBOT = excluded.entBOT,
                entMOT = excluded.entMOT,
                entEOT = excluded.entEOT,
                cre1 = excluded.cre1,
                cre2 = excluded.cre2,
                cre3 = excluded.cre3,
                cre4 = excluded.cre4,
                creBOT = excluded.creBOT,
                creMOT = excluded.creMOT,
                creEOT = excluded.creEOT,
                agr1 = excluded.agr1,
                agr2 = excluded.agr2,
                agr3 = excluded.agr3,
                agr4 = excluded.agr4,
                agrBOT = excluded.agrBOT,
                agrMOT = excluded.agrMOT,
                agrEOT = excluded.agrEOT,
                phe1 = excluded.phe1,
                phe2 = excluded.phe2,
                phe3 = excluded.phe3,
                phe4 = excluded.phe4,
                pheBOT = excluded.pheBOT,
                pheMOT = excluded.pheMOT,
                pheEOT = excluded.pheEOT,
                kis1 = excluded.kis1,
                kis2 = excluded.kis2,
                kis3 = excluded.kis3,
                kis4 = excluded.kis4,
                kisBOT = excluded.kisBOT,
                kisMOT = excluded.kisMOT,
                kisEOT = excluded.kisEOT,
                art1 = excluded.art1,
                art2 = excluded.art2,
                art3 = excluded.art3,
                art4 = excluded.art4,
                artBOT = excluded.artBOT,
                artMOT = excluded.artMOT,
                artEOT = excluded.artEOT,
                ire1 = excluded.ire1,
                ire2 = excluded.ire2,
                ire3 = excluded.ire3,
                ire4 = excluded.ire4,
                ireBOT = excluded.ireBOT,
                ireMOT = excluded.ireMOT,
                ireEOT = excluded.ireEOT,
                lit1 = excluded.lit1,
                lit2 = excluded.lit2,
                lit3 = excluded.lit3,
                lit4 = excluded.lit4,
                litBOT = excluded.litBOT,
                litMOT = excluded.litMOT,
                litEOT = excluded.litEOT,
                tad1 = excluded.tad1,
                tad2 = excluded.tad2,
                tad3 = excluded.tad3,
                tad4 = excluded.tad4,
                tadBOT = excluded.tadBOT,
                tadMOT = excluded.tadMOT,
                tadEOT = excluded.tadEOT,
                fsn1 = excluded.fsn1,
                fsn2 = excluded.fsn2,
                fsn3 = excluded.fsn3,
                fsn4 = excluded.fsn4,
                fsnBOT = excluded.fsnBOT,
                fsnMOT = excluded.fsnMOT,
                fsnEOT = excluded.fsnEOT,
                lat1 = excluded.lat1,
                lat2 = excluded.lat2,
                lat3 = excluded.lat3,
                lat4 = excluded.lat4,
                latBOT = excluded.latBOT,
                latMOT = excluded.latMOT,
                latEOT = excluded.latEOT,
                ate1 = excluded.ate1,
                ate2 = excluded.ate2,
                ate3 = excluded.ate3,
                ate4 = excluded.ate4,
                ateBOT = excluded.ateBOT,
                ateMOT = excluded.ateMOT,
                ateEOT = excluded.ateEOT,
                lum1 = excluded.lum1,
                lum2 = excluded.lum2,
                lum3 = excluded.lum3,
                lum4 = excluded.lum4,
                lumBOT = excluded.lumBOT,
                lumMOT = excluded.lumMOT,
                lumEOT = excluded.lumEOT,
                lug1 = excluded.lug1,
                lug2 = excluded.lug2,
                lug3 = excluded.lug3,
                lug4 = excluded.lug4,
                lugBOT = excluded.lugBOT,
                lugMOT = excluded.lugMOT,
                lugEOT = excluded.lugEOT,
                lus1 = excluded.lus1,
                lus2 = excluded.lus2,
                lus3 = excluded.lus3,
                lus4 = excluded.lus4,
                lusBOT = excluded.lusBOT,
                lusMOT = excluded.lusMOT,
                lusEOT = excluded.lusEOT,
                lba1 = excluded.lba1,
                lba2 = excluded.lba2,
                lba3 = excluded.lba3,
                lba4 = excluded.lba4,
                lbaBOT = excluded.lbaBOT,
                lbaMOT = excluded.lbaMOT,
                lbaEOT = excluded.lbaEOT,
                lbl1 = excluded.lbl1,
                lbl2 = excluded.lbl2,
                lbl3 = excluded.lbl3,
                lbl4 = excluded.lbl4,
                lblBOT = excluded.lblBOT,
                lblMOT = excluded.lblMOT,
                lblEOT = excluded.lblEOT,
                run1 = excluded.run1,
                run2 = excluded.run2,
                run3 = excluded.run3,
                run4 = excluded.run4,
                runBOT = excluded.runBOT,
                runMOT = excluded.runMOT,
                runEOT = excluded.runEOT,
                rut1 = excluded.rut1,
                rut2 = excluded.rut2,
                rut3 = excluded.rut3,
                rut4 = excluded.rut4,
                rutBOT = excluded.rutBOT,
                rutMOT = excluded.rutMOT,
                rutEOT = excluded.rutEOT,
                fre1 = excluded.fre1,
                fre2 = excluded.fre2,
                fre3 = excluded.fre3,
                fre4 = excluded.fre4,
                freBOT = excluded.freBOT,
                freMOT = excluded.freMOT,
                freEOT = excluded.freEOT,
                ger1 = excluded.ger1,
                ger2 = excluded.ger2,
                ger3 = excluded.ger3,
                ger4 = excluded.ger4,
                gerBOT = excluded.gerBOT,
                gerMOT = excluded.gerMOT,
                gerEOT = excluded.gerEOT,
                dho1 = excluded.dho1,
                dho2 = excluded.dho2,
                dho3 = excluded.dho3,
                dho4 = excluded.dho4,
                dhoBOT = excluded.dhoBOT,
                dhoMOT = excluded.dhoMOT,
                dhoEOT = excluded.dhoEOT
            ''', (
                student['std_no'], student['sdt_name'], student['stream'], student['year'], student['term'],
                student['gender'], student['section'], student['eng1'], student['eng2'], student['eng3'], student['eng4'], student['engBOT'], student['engMOT'], student['engEOT'],
                student['mtc1'], student['mtc2'], student['mtc3'], student['mtc4'], student['mtcBOT'], student['mtcMOT'], student['mtcEOT'],
                student['bio1'], student['bio2'], student['bio3'], student['bio4'], student['bioBOT'], student['bioMOT'], student['bioEOT'],
                student['phy1'], student['phy2'], student['phy3'], student['phy4'], student['phyBOT'], student['phyMOT'], student['phyEOT'],
                student['geo1'], student['geo2'], student['geo3'], student['geo4'], student['geoBOT'], student['geoMOT'], student['geoEOT'],
                student['his1'], student['his2'], student['his3'], student['his4'], student['hisBOT'], student['hisMOT'], student['hisEOT'],
                student['che1'], student['che2'], student['che3'], student['che4'], student['cheBOT'], student['cheMOT'], student['cheEOT'],
                student['ict1'], student['ict2'], student['ict3'], student['ict4'], student['ictBOT'], student['ictMOT'], student['ictEOT'],
                student['ent1'], student['ent2'], student['ent3'], student['ent4'], student['entBOT'], student['entMOT'], student['entEOT'],
                student['cre1'], student['cre2'], student['cre3'], student['cre4'], student['creBOT'], student['creMOT'], student['creEOT'],
                student['agr1'], student['agr2'], student['agr3'], student['agr4'], student['agrBOT'], student['agrMOT'], student['agrEOT'],
                student['phe1'], student['phe2'], student['phe3'], student['phe4'], student['pheBOT'], student['pheMOT'], student['pheEOT'],
                student['kis1'], student['kis2'], student['kis3'], student['kis4'], student['kisBOT'], student['kisMOT'], student['kisEOT'],
                student['art1'], student['art2'], student['art3'], student['art4'], student['artBOT'], student['artMOT'], student['artEOT'],
                student['ire1'], student['ire2'], student['ire3'], student['ire4'], student['ireBOT'], student['ireMOT'], student['ireEOT'],
                student['lit1'], student['lit2'], student['lit3'], student['lit4'], student['litBOT'], student['litMOT'], student['litEOT'],
                student['tad1'], student['tad2'], student['tad3'], student['tad4'], student['tadBOT'], student['tadMOT'], student['tadEOT'],
                student['fsn1'], student['fsn2'], student['fsn3'], student['fsn4'], student['fsnBOT'], student['fsnMOT'], student['fsnEOT'],
                student['lat1'], student['lat2'], student['lat3'], student['lat4'], student['latBOT'], student['latMOT'], student['latEOT'],
                student['ate1'], student['ate2'], student['ate3'], student['ate4'], student['ateBOT'], student['ateMOT'], student['ateEOT'],
                student['lum1'], student['lum2'], student['lum3'], student['lum4'], student['lumBOT'], student['lumMOT'], student['lumEOT'],
                student['lug1'], student['lug2'], student['lug3'], student['lug4'], student['lugBOT'], student['lugMOT'], student['lugEOT'],
                student['lus1'], student['lus2'], student['lus3'], student['lus4'], student['lusBOT'], student['lusMOT'], student['lusEOT'],
                student['lba1'], student['lba2'], student['lba3'], student['lba4'], student['lbaBOT'], student['lbaMOT'], student['lbaEOT'],
                student['lbl1'], student['lbl2'], student['lbl3'], student['lbl4'], student['lblBOT'], student['lblMOT'], student['lblEOT'],
                student['run1'], student['run2'], student['run3'], student['run4'], student['runBOT'], student['runMOT'], student['runEOT'],
                student['rut1'], student['rut2'], student['rut3'], student['rut4'], student['rutBOT'], student['rutMOT'], student['rutEOT'],
                student['fre1'], student['fre2'], student['fre3'], student['fre4'], student['freBOT'], student['freMOT'], student['freEOT'],
                student['ger1'], student['ger2'], student['ger3'], student['ger4'], student['gerBOT'], student['gerMOT'], student['gerEOT'],
                student['dho1'], student['dho2'], student['dho3'], student['dho4'], student['dhoBOT'], student['dhoMOT'], student['dhoEOT']
                ))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        conn.close()

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    if not check_auth():
        return jsonify({'success': False, 'message': 'Authentication required'})
    
    if not check_role(['admin', 'headteacher', 'teacher']):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    data = request.json
    std_no = data['std_no']
    class_level = data['class']
    stream = data['stream']
    year = data['year']
    term = data['term']
    report_type = data['report_type']  # BOT, MOT, EOT
    
    conn = get_db_connection()
    
    try:
        # Get student data
        student = conn.execute(f'''
            SELECT * FROM {class_level} 
            WHERE std_no = ? AND stream = ? AND year = ? AND term = ?
        ''', (std_no, stream, year, term)).fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        # Get school settings
        try:
            school = conn.execute('SELECT * FROM admin_settings ORDER BY id DESC LIMIT 1').fetchone()
        except:
            school = None
        
        # Get subjects
        try:
            subjects = conn.execute('SELECT * FROM subjects').fetchall()
        except:
            subjects = []
        
        # Get grading system
        try:
            grading = conn.execute('SELECT * FROM grading_system ORDER BY min_score DESC').fetchall()
        except:
            grading = []
        
        # Calculate grades and prepare report data
        report_data = {
            'student': dict(student),
            'school': dict(school) if school else {},
            'subjects': [dict(subject) for subject in subjects],
            'grading': [dict(grade) for grade in grading],
            'report_type': report_type
        }
        
        return jsonify({'success': True, 'data': report_data})
    except sqlite3.Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        conn.close()

@app.route('/api/export_excel', methods=['POST'])
def export_excel():
    if not check_auth():
        return jsonify({'error': 'Authentication required'}), 401
    
    if not check_role(['admin', 'headteacher', 'teacher']):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    class_level = data['class']
    stream = data['stream']
    year = data['year']
    term = data['term']
    
    conn = get_db_connection()
    try:
        students = conn.execute(f'''
            SELECT * FROM {class_level} 
            WHERE stream = ? AND year = ? AND term = ?
            ORDER BY std_no
        ''', (stream, year, term)).fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(student) for student in students])
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Marks', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{class_level}_{stream}_{year}_{term}_marks.xlsx'
        )
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

#add user route and functionality
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        # Extract form data
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        subjects_taught = request.form.get('subjects_taught', '')
        classes_taught = request.form.get('classes_taught', '')

        # Generate user ID and temporary password
        user_id = 'USR' + str(int(datetime.now().timestamp()))[-6:]
        temp_password = 'temp' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))
        hashed_password = hash_password(temp_password)  # Hash the temporary password

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert user into the database
        cursor.execute('''
            INSERT INTO users (user_id, full_name, email, phone, role, subjects_taught, classes_taught, password, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, full_name, email, phone, role, subjects_taught, classes_taught, hashed_password, 1))

        conn.commit()
        conn.close()

        # Return success response
        return jsonify({'success': True, 'user_id': user_id, 'temp_password': temp_password})
    except sqlite3.Error as e:
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_unique_user_id(cursor):
    while True:
        user_id = 'USR' + str(int(datetime.now().timestamp()))[-6:]
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():  # If user_id does not exist
            return user_id


#delete user route and functionality
@app.route('/delete_user', methods=['POST'])
def delete_user():
    if not check_auth():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    if not check_role(['admin']):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except sqlite3.Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()
        
#reset password route and functionality
@app.route('/reset_password', methods=['POST'])
def reset_password():
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    # Simulate resetting the password
    temp_password = 'temp' + str(hash(user_id))[:6]

    # Here, you would update the user's password in the database
    # For now, we'll simulate success
    return jsonify({'success': True, 'message': f'Password reset successfully! Temporary password: {temp_password}'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

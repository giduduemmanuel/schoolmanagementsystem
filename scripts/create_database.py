import sqlite3
import os

def create_database():
    # Create database connection
    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()
    
    # Create admin settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT,
            school_email TEXT,
            school_motto TEXT,
            school_address TEXT,
            school_box TEXT,
            school_contacts TEXT,
            school_logo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create streams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_level TEXT,
            stream_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_initial TEXT,
            subject_full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            subjects_taught TEXT,
            classes_taught TEXT,
            role TEXT,
            password TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create grading system table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grading_system (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            min_score INTEGER,
            max_score INTEGER,
            grade TEXT,
            descriptor TEXT,
            comment TEXT
        )
    ''')
    
    # Create deadline table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            year INTEGER,
            deadline_date DATE,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Create class tables (S1, S2, S3, S4, S5, S6)
    classes = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
    
    for class_name in classes:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {class_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                std_no INTEGER,
                sdt_name TEXT,
                class_level TEXT,
                stream TEXT,
                year INTEGER,
                term TEXT,
                gender TEXT,
                section TEXT,
                eng1 REAL, eng2 REAL, eng3 REAL, eng4 REAL, engBOT REAL, engMOT REAL, engEOT REAL,
                mtc1 REAL, mtc2 REAL, mtc3 REAL, mtc4 REAL, mtcBOT REAL, mtcMOT REAL, mtcEOT REAL,
                bio1 REAL, bio2 REAL, bio3 REAL, bio4 REAL, bioBOT REAL, bioMOT REAL, bioEOT REAL,
                phy1 REAL, phy2 REAL, phy3 REAL, phy4 REAL, phyBOT REAL, phyMOT REAL, phyEOT REAL,
                geo1 REAL, geo2 REAL, geo3 REAL, geo4 REAL, geoBOT REAL, geoMOT REAL, geoEOT REAL,
                his1 REAL, his2 REAL, his3 REAL, his4 REAL, hisBOT REAL, hisMOT REAL, hisEOT REAL,
                che1 REAL, che2 REAL, che3 REAL, che4 REAL, cheBOT REAL, cheMOT REAL, cheEOT REAL,
                ict1 REAL, ict2 REAL, ict3 REAL, ict4 REAL, ictBOT REAL, ictMOT REAL, ictEOT REAL,
                ent1 REAL, ent2 REAL, ent3 REAL, ent4 REAL, entBOT REAL, entMOT REAL, entEOT REAL,
                cre1 REAL, cre2 REAL, cre3 REAL, cre4 REAL, creBOT REAL, creMOT REAL, creEOT REAL,
                agr1 REAL, agr2 REAL, agr3 REAL, agr4 REAL, agrBOT REAL, agrMOT REAL, agrEOT REAL,
                phe1 REAL, phe2 REAL, phe3 REAL, phe4 REAL, pheBOT REAL, pheMOT REAL, pheEOT REAL,
                kis1 REAL, kis2 REAL, kis3 REAL, kis4 REAL, kisBOT REAL, kisMOT REAL, kisEOT REAL,
                art1 REAL, art2 REAL, art3 REAL, art4 REAL, artBOT REAL, artMOT REAL, artEOT REAL,
                ire1 REAL, ire2 REAL, ire3 REAL, ire4 REAL, ireBOT REAL, ireMOT REAL, ireEOT REAL,
                lit1 REAL, lit2 REAL, lit3 REAL, lit4 REAL, litBOT REAL, litMOT REAL, litEOT REAL,
                tad1 REAL, tad2 REAL, tad3 REAL, tad4 REAL, tadBOT REAL, tadMOT REAL, tadEOT REAL,
                fsn1 REAL, fsn2 REAL, fsn3 REAL, fsn4 REAL, fsnBOT REAL, fsnMOT REAL, fsnEOT REAL,
                lat1 REAL, lat2 REAL, lat3 REAL, lat4 REAL, latBOT REAL, latMOT REAL, latEOT REAL,
                ate1 REAL, ate2 REAL, ate3 REAL, ate4 REAL, ateBOT REAL, ateMOT REAL, ateEOT REAL,
                lum1 REAL, lum2 REAL, lum3 REAL, lum4 REAL, lumBOT REAL, lumMOT REAL, lumEOT REAL,
                lug1 REAL, lug2 REAL, lug3 REAL, lug4 REAL, lugBOT REAL, lugMOT REAL, lugEOT REAL,
                lus1 REAL, lus2 REAL, lus3 REAL, lus4 REAL, lusBOT REAL, lusMOT REAL, lusEOT REAL,
                lba1 REAL, lba2 REAL, lba3 REAL, lba4 REAL, lbaBOT REAL, lbaMOT REAL, lbaEOT REAL,
                lbl1 REAL, lbl2 REAL, lbl3 REAL, lbl4 REAL, lblBOT REAL, lblMOT REAL, lblEOT REAL,
                run1 REAL, run2 REAL, run3 REAL, run4 REAL, runBOT REAL, runMOT REAL, runEOT REAL,
                rut1 REAL, rut2 REAL, rut3 REAL, rut4 REAL, rutBOT REAL, rutMOT REAL, rutEOT REAL,
                fre1 REAL, fre2 REAL, fre3 REAL, fre4 REAL, freBOT REAL, freMOT REAL, freEOT REAL,
                ger1 REAL, ger2 REAL, ger3 REAL, ger4 REAL, gerBOT REAL, gerMOT REAL, gerEOT REAL,
                dho1 REAL, dho2 REAL, dho3 REAL, dho4 REAL, dhoBOT REAL, dhoMOT REAL, dhoEOT REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Create LEFT table for graduated/deleted students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LEFT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            std_no INTEGER,
            sdt_name TEXT,
            class_level TEXT,
            stream TEXT,
            year INTEGER,
            term TEXT,
            gender TEXT,
            section TEXT,
            eng1 REAL, eng2 REAL, eng3 REAL, eng4 REAL, engBOT REAL, engMOT REAL, engEOT REAL,
            mtc1 REAL, mtc2 REAL, mtc3 REAL, mtc4 REAL, mtcBOT REAL, mtcMOT REAL, mtcEOT REAL,
            bio1 REAL, bio2 REAL, bio3 REAL, bio4 REAL, bioBOT REAL, bioMOT REAL, bioEOT REAL,
            phy1 REAL, phy2 REAL, phy3 REAL, phy4 REAL, phyBOT REAL, phyMOT REAL, phyEOT REAL,
            geo1 REAL, geo2 REAL, geo3 REAL, geo4 REAL, geoBOT REAL, geoMOT REAL, geoEOT REAL,
            his1 REAL, his2 REAL, his3 REAL, his4 REAL, hisBOT REAL, hisMOT REAL, hisEOT REAL,
            che1 REAL, che2 REAL, che3 REAL, che4 REAL, cheBOT REAL, cheMOT REAL, cheEOT REAL,
            ict1 REAL, ict2 REAL, ict3 REAL, ict4 REAL, ictBOT REAL, ictMOT REAL, ictEOT REAL,
            ent1 REAL, ent2 REAL, ent3 REAL, ent4 REAL, entBOT REAL, entMOT REAL, entEOT REAL,
            cre1 REAL, cre2 REAL, cre3 REAL, cre4 REAL, creBOT REAL, creMOT REAL, creEOT REAL,
            agr1 REAL, agr2 REAL, agr3 REAL, agr4 REAL, agrBOT REAL, agrMOT REAL, agrEOT REAL,
            phe1 REAL, phe2 REAL, phe3 REAL, phe4 REAL, pheBOT REAL, pheMOT REAL, pheEOT REAL,
            kis1 REAL, kis2 REAL, kis3 REAL, kis4 REAL, kisBOT REAL, kisMOT REAL, kisEOT REAL,
            art1 REAL, art2 REAL, art3 REAL, art4 REAL, artBOT REAL, artMOT REAL, artEOT REAL,
            ire1 REAL, ire2 REAL, ire3 REAL, ire4 REAL, ireBOT REAL, ireMOT REAL, ireEOT REAL,
            lit1 REAL, lit2 REAL, lit3 REAL, lit4 REAL, litBOT REAL, litMOT REAL, litEOT REAL,
            tad1 REAL, tad2 REAL, tad3 REAL, tad4 REAL, tadBOT REAL, tadMOT REAL, tadEOT REAL,
            fsn1 REAL, fsn2 REAL, fsn3 REAL, fsn4 REAL, fsnBOT REAL, fsnMOT REAL, fsnEOT REAL,
            lat1 REAL, lat2 REAL, lat3 REAL, lat4 REAL, latBOT REAL, latMOT REAL, latEOT REAL,
            ate1 REAL, ate2 REAL, ate3 REAL, ate4 REAL, ateBOT REAL, ateMOT REAL, ateEOT REAL,
            lum1 REAL, lum2 REAL, lum3 REAL, lum4 REAL, lumBOT REAL, lumMOT REAL, lumEOT REAL,
            lug1 REAL, lug2 REAL, lug3 REAL, lug4 REAL, lugBOT REAL, lugMOT REAL, lugEOT REAL,
            lus1 REAL, lus2 REAL, lus3 REAL, lus4 REAL, lusBOT REAL, lusMOT REAL, lusEOT REAL,
            lba1 REAL, lba2 REAL, lba3 REAL, lba4 REAL, lbaBOT REAL, lbaMOT REAL, lbaEOT REAL,
            lbl1 REAL, lbl2 REAL, lbl3 REAL, lbl4 REAL, lblBOT REAL, lblMOT REAL, lblEOT REAL,
            run1 REAL, run2 REAL, run3 REAL, run4 REAL, runBOT REAL, runMOT REAL, runEOT REAL,
            rut1 REAL, rut2 REAL, rut3 REAL, rut4 REAL, rutBOT REAL, rutMOT REAL, rutEOT REAL,
            fre1 REAL, fre2 REAL, fre3 REAL, fre4 REAL, freBOT REAL, freMOT REAL, freEOT REAL,
            ger1 REAL, ger2 REAL, ger3 REAL, ger4 REAL, gerBOT REAL, gerMOT REAL, gerEOT REAL,
            dho1 REAL, dho2 REAL, dho3 REAL, dho4 REAL, dhoBOT REAL, dhoMOT REAL, dhoEOT REAL,
            reason TEXT,
            moved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            std_no INTEGER,
            class_level TEXT,
            mother_contact TEXT,
            father_contact TEXT,
            sibling_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create library tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT,
            author TEXT,
            isbn TEXT,
            category TEXT,
            total_copies INTEGER,
            available_copies INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_borrowing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            std_no INTEGER,
            class_level TEXT,
            borrow_date DATE,
            return_date DATE,
            actual_return_date DATE,
            fine_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'borrowed',
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    # Create fees tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_level TEXT,
            term TEXT,
            amount REAL,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            std_no INTEGER,
            class_level TEXT,
            term TEXT,
            year INTEGER,
            amount_paid REAL,
            payment_date DATE,
            receipt_no TEXT,
            payment_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, full_name, email, role, password)
        VALUES ('admin', 'System Administrator', 'admin@school.com', 'admin', 'admin123')
    ''')
    
    # Insert default grading system
    grading_data = [
        (80, 100, 'A', 'Exceptional', 'Demonstrates an extraordinary level of competency'),
        (70, 79, 'B', 'Outstanding', 'Demonstrates a high level of competency'),
        (60, 69, 'C', 'Satisfactory', 'Demonstrates an adequate level of competency'),
        (50, 59, 'D', 'Basic', 'Demonstrates a minimum level of competency'),
        (0, 49, 'E', 'Elementary', 'Demonstrates below the basic level of competency')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO grading_system (min_score, max_score, grade, descriptor, comment)
        VALUES (?, ?, ?, ?, ?)
    ''', grading_data)
    
    # Insert default subjects
    subjects_data = [
        ('ENG1', 'English Language'),
        ('ENG2', 'English Literature'),
        ('MATH', 'Mathematics'),
        ('BIO', 'Biology'),
        ('PHY', 'Physics'),
        ('CHEM', 'Chemistry'),
        ('GEO', 'Geography'),
        ('HIST', 'History & Political Education'),
        ('ENT', 'Entrepreneurship'),
        ('CRE', 'Christian Religious Education'),
        ('ICT', 'Information Communication Technology'),
        ('AGR', 'Agriculture'),
        ('ART', 'Art & Design'),
        ('KIS', 'Kiswahili'),
        ('PE', 'Physical Education'),
        ('LIT', 'Literature')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO subjects (subject_initial, subject_full_name)
        VALUES (?, ?)
    ''', subjects_data)
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()

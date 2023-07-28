import os
import re
import sqlite3
import datetime
from datetime import timedelta
import time
import schedule



def check_file(file):  # τσεκάρει αν το αρχείο περιέχει το ERROR:1 ανάμεσα απο DEVICE INFO + KEY STATUS
    check_result = False
    with open(file, 'r') as file:
        lines = file.read()
        match = re.search(r"DEVICE INFO\s+(.*?)\s+KEY STATUS", lines, re.DOTALL)
        if match:
            section_text = match.group(1)
            if re.search(r"ERROR\s+:\s+1", section_text):
                check_result = True
            else:
                check_result = True
    return check_result


def find_file(start_dir, target_file):  # Βρίσκει το path του αρχείου τσεκάροντας φακέλους, υποφάκελους και αρχεία
    for dirpath, dirnames, filenames in os.walk(start_dir):  # τσεκάρει τον ελέγχο με αρχή το start_dir
        if target_file in filenames:  # τσεκάρει αν το όνομα αρχείου που του είπαμε βρίσκεται στα αρχεία του pc
            file_path = os.path.join(dirpath, target_file)  # ενώνει αρχή και τέλος για το τελικό path
            file_check = check_file(file_path) # τσεκάρει το Error
            if file_check:
                if len(file_path) == 72:
                    split_result_and_sql_it(file_path)  # φτιάχνει τη βάση δεδομένων


def split_result_and_sql_it(path):
    path = path
    splited = path.split('\\')  # χωρίζει το path σε τμήματα
    file_name = splited[-1]
    time = splited[-2].replace("_", ":")
    date = splited[-3].replace("_", "/")
    tid = splited[-4]
    bank_id = splited[-5]
    date_added = datetime.date.today()
    added = date_added.strftime("%d/%m/%Y")
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()


    # δημιουργία table αν δεν υπάρχει στο pc
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bank_id int,
                        added TEXT,
                        tid TEXT,
                        date TEXT,
                        time TEXT,
                        file_name TEXT,
                        path TEXT)''')

    '''not_before = "03/08/2023" 
        if date > not_before : run all above #αν χρειαστει να γινει τσεκ μετα απο μια ημ/νια
        else: pass'''

    # ελέγχει αν το path υπάρχει στη βάση
    cursor.execute(f'''SELECT path FROM logs WHERE bank_id=?
                         AND tid=? AND date=? AND time=? AND file_name=?
                         AND path=?''', (bank_id, tid, date, time, file_name, path))
    result = cursor.fetchone()

    if result is not None:
        pass
        #print(f'Η Βάση Δεδομένων έχει ηδη τo στοιχείο :  {result[0]}')
    else:  # αλλιώς περνάει τα στοιχεία στη βάση
        cursor.execute(f'''INSERT INTO logs (bank_id,added, tid, date, time, file_name, path)
                        VALUES (?,?,?,?,?,?,?)''', (bank_id, added, tid, date, time, file_name, path))
    conn.commit()
    conn.close()

counter = 0
date_added = datetime.date.today() - timedelta(days=1)  # εχθές
added = date_added.strftime("%d/%m/%Y")

def all_entries():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM logs")
    new_logs = cursor.fetchall()
    counter = len(new_logs)
    print(f"Σύνολο εισαγωγών : {counter}")
    conn.commit()
    conn.close()

def check_new_entries(date):  # ελέγχει αν υπάρχουν αλλαγές στη βάση τη χθεσινή μέρα υποθέτοντας οτι τρέχει το πρωί
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT path FROM logs WHERE added=?", (date,))  # χωρίς το ¨,¨ δε θα ψάξει για ολα τα στοιχεία με αυτήν την ημ/ια
    new_logs = cursor.fetchall()
    counter = len(new_logs)
    if len(new_logs) > 0:  # αν δε βρει τπτ μας επιστρέφει []
        print(f"{counter} εισαγωγές")
    else:
        print('Καμία νεα Εισαγωγή σήμερα')
    conn.commit()
    conn.close()


start_directory = r"C:\Users\v.damis\Downloads\16"  # αρχή path
target_file_name = 'APPINFO_T3'  # όνομα αρχείου προς αναζήτηση (τέλος path)


def job():  # δημιουργία ενός job για να καλείται στο schedule
    find_file(start_directory, target_file_name)
    check_new_entries(added)
    all_entries()


job()  # καλώ τη job για να τρέξει αμέσως
schedule.every(15).seconds.do(job)  # κάθε πότε θα τρέχει


# Τρέχει συνεχόμενα το script
while True:
    schedule.run_pending()
    time.sleep(1)

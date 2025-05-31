import random
import sys
import os
import sqlite3 # Added for SQLite
import datetime # Added for timestamping

DB_NAME = "queue.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            priority_level INTEGER NOT NULL,
            serving_time INTEGER NOT NULL,
            added_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if os.name == 'nt': 
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        print("Warning: Could not reconfigure stdout/stderr for UTF-8 automatically. Special characters might not display correctly. Consider running in a UTF-8 compatible terminal or setting PYTHONIOENCODING=UTF-8.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while trying to reconfigure stdout/stderr: {e}", file=sys.stderr)


# Șanse de generare și Priorități pentru fiecare tip client
client_types = {
    'urgenta': 1,
    'client_cu_dizabilitati': 3,
    'familie_cu_dizabilitati': 5,
    'familie_cu_copii': 12,
    'client_cu_abonament': 15,
    'mama_insarcinata': 7,
    'angajatii': 4,
    'client_fara_abonament': 53
}

client_priorities = {
    'urgenta': (1, 5),  # (prioritate, timp_servire_minute)
    'client_cu_dizabilitati': (2, 10),
    'familie_cu_dizabilitati': (3, 12),
    'familie_cu_copii': (4, 8),
    'client_cu_abonament': (5, 7),
    'mama_insarcinata': (6, 10),
    'angajatii': (7, 3),
    'client_fara_abonament': (8, 6)
}

def generator_for_priority(prio_level, count):
    # Generează 'count' număr de clienți pentru o prioritate dată
    clients = []
    for _ in range(count):
        client_name = None
        client_serving_time = 0
        for name, (p, t) in client_priorities.items():
            if p == prio_level:
                client_name = name
                client_serving_time = t
                break
        if client_name is None:
            continue  # ignoră dacă nu găsește
        clients.append((client_name, prio_level, client_serving_time))
    return clients

def afisare_coada():
    print("\nStarea curentă a cozii (ordonată crescător după prioritate):")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_name, priority_level, serving_time, added_timestamp FROM clients ORDER BY priority_level, added_timestamp")
    clients_in_db = cursor.fetchall()
    conn.close()

    if not clients_in_db:
        print("Coada este goală.")
        return
    
    cumulative_eta = 0
    for idx, client_row in enumerate(clients_in_db, 1):
        eta_pana_la_client = cumulative_eta
        print(f"{idx}. {client_row['client_name']} - Prioritate {client_row['priority_level']} (Timp servire: {client_row['serving_time']} min) - ETA pornire servire: {eta_pana_la_client} min")
        cumulative_eta += client_row['serving_time']
    print(f"Timp total estimat pentru golirea cozii: {cumulative_eta} minute.")

def adauga_clienti_bundle():
    while True:
        try:
            prio_level = int(input("Introduceți prioritatea clienților de adăugat (1-8): "))
            if not 1 <= prio_level <= 8:
                print("Prioritatea trebuie să fie între 1 și 8.")
                continue
            
            valid_prio = False
            client_name_for_prio, serving_time_for_prio = None, None
            for name, (p, t) in client_priorities.items():
                if p == prio_level:
                    valid_prio = True
                    client_name_for_prio = name # We need a representative name for this prio
                    serving_time_for_prio = t
                    break 
            if not valid_prio:
                print(f"Nu există un tip de client definit pentru prioritatea {prio_level}.")
                continue

            count = int(input("Câți clienți doriți să adăugați? "))
            if count < 1:
                print("Numărul trebuie să fie cel puțin 1.")
                continue
            
            # The generator_for_priority helps find the client_name and serving_time
            # for the given prio_level. We'll use the first one it finds.
            clients_to_add_data = generator_for_priority(prio_level, count)

            if not clients_to_add_data:
                print("Prioritate invalidă sau nu s-au putut genera datele clienților.")
                continue
            
            conn = get_db_connection()
            cursor = conn.cursor()
            for c_name, c_prio, c_time in clients_to_add_data:
                cursor.execute("INSERT INTO clients (client_name, priority_level, serving_time, added_timestamp) VALUES (?, ?, ?, ?)",
                               (c_name, c_prio, c_time, datetime.datetime.now()))
            conn.commit()
            conn.close()
            
            print(f"{count} clienți cu prioritatea {prio_level} au fost adăugați în baza de date.")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid.")

def sterge_clienti_bundle():
    while True:
        try:
            prio_level = int(input("Introduceți prioritatea clienților pe care doriți să-i ștergeți (1-8): "))
            if prio_level < 1 or prio_level > 8:
                print("Prioritatea trebuie să fie între 1 și 8.")
                continue

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE priority_level = ?", (prio_level,))
            clients_to_delete = cursor.fetchall()
            numar_gasiti = len(clients_to_delete)
            
            if numar_gasiti == 0:
                print(f"Nu există clienți cu prioritatea {prio_level} în coadă.")
                return
            print(f"Există {numar_gasiti} clienți cu prioritatea {prio_level} în coadă.")

            count = int(input("Câți clienți doriți să ștergeți? "))
            if count < 1:
                print("Numărul trebuie să fie cel puțin 1.")
                continue
            if count > numar_gasiti:
                print(f"Nu puteți șterge {count} clienți deoarece există doar {numar_gasiti} cu prioritatea {prio_level}.")
                print("Vă rugăm să introduceți un număr mai mic sau egal cu cel disponibil.")
                continue

            # Ștergem clienții din baza de date
            for i in range(count):
                client_id = clients_to_delete[i]['id']
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            
            conn.commit()
            conn.close()
            print(f"{count} clienți cu prioritatea {prio_level} au fost șterși cu succes.")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid.") # Eroarea

def serve_next():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, client_name, priority_level, serving_time FROM clients ORDER BY priority_level, added_timestamp LIMIT 1")
    client_to_serve = cursor.fetchone()

    if client_to_serve is None:
        print("Coada este goală. Nu există clienți de servit.")
        return
    
    # Ștergem clientul din baza de date (servirea lui)
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_to_serve['id'],))
    conn.commit()
    conn.close()

    print(f"Clientul '{client_to_serve['client_name']}' cu prioritatea {client_to_serve['priority_level']} (timp estimat servire: {client_to_serve['serving_time']} min) a fost servit.")

def update_priority():
    while True:
        try:
            current_prio_level = int(input("Introduceți prioritatea curentă a clienților pe care doriți să-i actualizați (1-8): "))
            if not 1 <= current_prio_level <= 8:
                print("Prioritatea trebuie să fie între 1 și 8.")
                continue

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, client_name, priority_level, serving_time FROM clients WHERE priority_level = ?", (current_prio_level,))
            clients_with_current_prio = cursor.fetchall()
            num_found = len(clients_with_current_prio)

            if num_found == 0:
                print(f"Nu există clienți cu prioritatea {current_prio_level} în coadă.")
                return
            
            print(f"Există {num_found} clienți cu prioritatea {current_prio_level} în coadă.")

            count_to_update = int(input(f"Câți clienți cu prioritatea {current_prio_level} doriți să actualizați? "))
            if count_to_update < 1:
                print("Numărul trebuie să fie cel puțin 1.")
                continue
            if count_to_update > num_found:
                print(f"Nu puteți actualiza {count_to_update} clienți deoarece există doar {num_found} cu prioritatea {current_prio_level}.")
                print("Vă rugăm să introduceți un număr mai mic sau egal cu cel disponibil.")
                continue

            new_prio_val = int(input(f"Introduceți noua prioritate pentru acești {count_to_update} clienți (1-8): "))
            if not 1 <= new_prio_val <= 8:
                print("Noua prioritate trebuie să fie între 1 și 8.")
                continue
            
            # Verificăm dacă noua prioritate are un tip de client definit (și implicit un timp de servire)
            new_serving_time_for_new_prio = None
            new_client_type_for_new_prio = None
            for c_type, (p, t) in client_priorities.items():
                if p == new_prio_val:
                    # Teoretic, ar trebui să actualizăm și tipul clientului dacă prioritatea se schimbă
                    # Dar pentru a păstra timpul de servire original, vom ignora timpul de servire al noii priorități
                    # și vom păstra timpul de servire original al clientului.
                    # Dacă am dori să preluăm noul timp de servire, am face: new_serving_time_for_new_prio = t
                    new_client_type_for_new_prio = c_type # Să presupunem că tipul se schimbă cu prioritatea
                    break 
            
            if new_client_type_for_new_prio is None:
                 print(f"Noua prioritate {new_prio_val} nu corespunde unui tip de client valid. Actualizare anulată.")
                 continue


            updated_count = 0
            for i in range(count_to_update):
                client_row = clients_with_current_prio[i]
                client_id = client_row['id']
                client_name = client_row['client_name']
                original_serving_time = client_row['serving_time'] # Păstrăm timpul de servire original
                
                # Găsim noul nume de client corespunzător noii priorități
                # Aceasta este o simplificare; ideal, ar trebui să întrebăm ce tip de client devine.
                # Pentru acest exemplu, vom lua primul tip de client care are noua prioritate.
                new_client_name_for_new_prio = client_name # Default to old name if no type matches new prio
                for c_type_key, (p_val, _) in client_priorities.items():
                    if p_val == new_prio_val:
                        new_client_name_for_new_prio = c_type_key
                        break

                cursor.execute("UPDATE clients SET client_name = ?, priority_level = ? WHERE id = ?",
                               (new_client_name_for_new_prio, new_prio_val, client_id))
                updated_count += 1
            
            conn.commit()
            conn.close()
            print(f"{updated_count} clienți au fost actualizați la prioritatea {new_prio_val} (păstrând timpii de servire originali).")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid.")
        except Exception as e:
            print(f"A apărut o eroare neașteptată: {e}")
            break

def calculate_eta_for_client():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, client_name, priority_level, serving_time FROM clients ORDER BY priority_level, added_timestamp")
    all_clients_ordered = cursor.fetchall()

    if not all_clients_ordered:
        print("Coada este goală. Nu se poate calcula ETA.")
        return
    
    while True:
        try:
            position = int(input(f"Introduceți poziția clientului în coadă (1-{len(all_clients_ordered)}): "))
            if not 1 <= position <= len(all_clients_ordered):
                print(f"Poziția trebuie să fie între 1 și {len(all_clients_ordered)}.")
                continue

            eta_att = 0
            for i in range(position - 1): # Timpul de așteptare până la clientul din față
                eta_att += all_clients_ordered[i]['serving_time'] # Adunăm timpul de servire al fiecărui client din față
            
            client_la_pozitie = all_clients_ordered[position-1]
            timp_servire_client = client_la_pozitie['serving_time']
            eta_finalizare_client = eta_att + timp_servire_client

            print(f"Clientul '{client_la_pozitie['client_name']}' (Prioritate {client_la_pozitie['priority_level']}) la poziția {position}:")
            print(f"  - Timp estimat de așteptare până la servire: {eta_att} minute.")
            print(f"  - Timp estimat de servire propriu-zis: {timp_servire_client} minute.")
            print(f"  - ETA finalizare servire: {eta_finalizare_client} minute de la momentul actual.")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid pentru poziție.")
        except IndexError: # Ar trebui acoperit de validarea poziției
            print("Poziție invalidă.")
            break


def main():
    init_db() # Initialize database and table
    print("=== Sistem Gestionare Cozi cu Prioritate și ETA (cu SQLite) ===")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    client_count_in_db = cursor.fetchone()[0]
    conn.close()

    if client_count_in_db == 0:
        print("Baza de date este goală. Se generează 100 de clienți inițiali...")
        types_available = list(client_types.keys()) 
        weights = list(client_types.values())
        
        conn_populate = get_db_connection()
        cursor_populate = conn_populate.cursor()
        for _ in range(100):
            selected_client_type_name = random.choices(types_available, weights=weights, k=1)[0]
            prio_level, serving_time = client_priorities[selected_client_type_name]
            cursor_populate.execute("INSERT INTO clients (client_name, priority_level, serving_time, added_timestamp) VALUES (?, ?, ?, ?)",
                               (selected_client_type_name, prio_level, serving_time, datetime.datetime.now()))
        conn_populate.commit()
        conn_populate.close()
        print("100 de clienți inițiali adăugați în baza de date.")

    while True:
        afisare_coada()
        alegere = input("\n[A] Adaugă clienți, [S] Servește următorul client, [U] Actualizează prioritatea, [D] Șterge clienți, [E] Calculează ETA client, [I] Ieșire: ").strip().lower()
        if alegere == 'a':
            adauga_clienti_bundle()
        elif alegere == 's':
            serve_next()
        elif alegere == 'u':
            update_priority()
        elif alegere == 'd': 
            sterge_clienti_bundle()
        elif alegere == 'e':
            calculate_eta_for_client()
        elif alegere == 'i':
            print("La revedere!")
            break
        else:
            print("Opțiune invalidă, vă rog încercați din nou.")

if __name__ == "__main__":
    main()
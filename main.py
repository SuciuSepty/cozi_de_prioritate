import random
import sys
import os

# Configure stdout/stderr for UTF-8 on Windows, if possible
if os.name == 'nt':  # 'nt' is for Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # sys.stdout.reconfigure might not be available on older Python versions
        # or in some environments.
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
    'urgenta': 1,
    'client_cu_dizabilitati': 2,
    'familie_cu_dizabilitati': 3,
    'familie_cu_copii': 4,
    'client_cu_abonament': 5,
    'mama_insarcinata': 6,
    'angajatii': 7,
    'client_fara_abonament': 8
}

arr = []

def generator_for_priority(prio, count):
    # Generează 'count' număr de clienți pentru o prioritate dată
    clients = []
    for _ in range(count):
        client_name = None
        for name, priority in client_priorities.items():
            if priority == prio:
                client_name = name
                break
        if client_name is None:
            continue  # ignoră dacă nu găsește
        clients.append((client_name, prio))
    return clients

def afisare_coada():
    print("\nStarea curentă a cozii (ordonată crescător după prioritate):")
    if not arr:
        print("Coada este goală.")
        return
    for idx, (nume, prio) in enumerate(arr, 1):
        print(f"{idx}. {nume} - Prioritate {prio}")

def adauga_clienti_bundle():
    while True:
        try:
            prio = int(input("Introduceți prioritatea clienților de adăugat (1-8): "))
            if prio < 1 or prio > 8:
                print("Prioritatea trebuie să fie între 1 și 8.")
                continue
            count = int(input("Câți clienți doriți să adăugați? "))
            if count < 1:
                print("Numărul trebuie să fie cel puțin 1.")
                continue
            clienti = generator_for_priority(prio, count)
            if not clienti:
                print("Prioritate invalidă sau nu s-au generat clienți.")
                continue
            arr.extend(clienti)
            arr.sort(key=lambda x: x[1])  # Sortează după prioritate
            print(f"{count} clienți cu prioritatea {prio} au fost adăugați.")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid.")

def sterge_clienti_bundle():
    while True:
        try:
            prio = int(input("Introduceți prioritatea clienților pe care doriți să-i ștergeți (1-8): "))
            if prio < 1 or prio > 8:
                print("Prioritatea trebuie să fie între 1 și 8.")
                continue

            gasiti = [i for i, client in enumerate(arr) if client[1] == prio]
            numar_gasiti = len(gasiti)
            if numar_gasiti == 0:
                print(f"Nu există clienți cu prioritatea {prio} în coadă.")
                return
            print(f"Există {numar_gasiti} clienți cu prioritatea {prio} în coadă.")

            count = int(input("Câți clienți doriți să ștergeți? "))
            if count < 1:
                print("Numărul trebuie să fie cel puțin 1.")
                continue
            if count > numar_gasiti:
                print(f"Nu puteți șterge {count} clienți deoarece există doar {numar_gasiti} cu prioritatea {prio}.")
                print("Vă rugăm să introduceți un număr mai mic sau egal cu cel disponibil.")
                continue

            indices_de_sters = gasiti[:count]
            for i in reversed(indices_de_sters):
                arr.pop(i)
            arr.sort(key=lambda x: x[1])  # Sortează după prioritate
            print(f"{count} clienți cu prioritatea {prio} au fost șterși cu succes.")
            break
        except ValueError:
            print("Vă rugăm să introduceți un număr valid.")

def main():
    print("=== Sistem Gestionare Cozi cu Prioritate ===")

    # Generăm automat 100 de clienți la start
    types = list(client_types.keys())
    weights = list(client_types.values())
    initial_clients = []
    for _ in range(100):
        selected_client = random.choices(types, weights=weights, k=1)[0]
        prio = client_priorities[selected_client]
        initial_clients.append((selected_client, prio))
    arr.extend(initial_clients)
    arr.sort(key=lambda x: x[1])  # Sortează la început de coada

    while True:
        afisare_coada()
        alegere = input("\n[A] Adaugă clienți, [Ș] Șterge clienți, [I] Ieșire: ").strip().lower()
        if alegere == 'a':
            adauga_clienti_bundle()
        elif alegere == 'ș' or alegere == 's':
            sterge_clienti_bundle()
        elif alegere == 'i':
            print("La revedere!")
            break
        else:
            print("Opțiune invalidă, vă rog încercați din nou.")

if __name__ == "__main__":
    main()

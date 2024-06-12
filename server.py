# -*- coding: utf-8 -*-
"""
Created on Tue June 11 16:38:52 2024

@author: matteo
"""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# Dizionari per tenere traccia dei client e dei loro indirizzi
clients = {}
addresses = {}

# Configurazione del server
host = '127.0.0.1'
port = 42069
buffsize = 1024
adrr = (host, port)

# Creazione del socket del server

# Crea un socket IPv4 (AF_INET) di tipo stream (SOCK_STREAM).
server = socket(AF_INET, SOCK_STREAM)
# associa il socket all'indirizzo IP e alla porta specificati.
server.bind(adrr)

# Accetta nuove connessioni in un ciclo continuo.
# Usa un try-except per catturare e gestire eventuali eccezioni durante l'accettazione delle connessioni.
# Avvia un nuovo thread per ogni client connesso per gestire la comunicazione.
def incoming_connections():
    """Accetta le connessioni in entrata da parte dei client."""
    while True:
        try:
            client, client_address = server.accept()
            print("%s:%s si è collegato." % client_address)
            client.send(bytes("Salve, digita il tuo nome seguito da invio!", "utf8"))
            addresses[client] = client_address
            # Avvia un nuovo thread per gestire il client
            Thread(target=manage_client, args=(client,)).start()
        except Exception as e:
            print(f"Errore nell'accettare la connessione: {e}")

# Riceve il nome del client e invia un messaggio di benvenuto.
# Gestisce i messaggi del client in un ciclo continuo.
# Rimuove il client dalla lista quando questo si disconnette (inviando {quit}).
# Usa un try-except per catturare e gestire eventuali eccezioni durante la gestione del client.
def manage_client(client):
    """Gestisce un singolo client."""
    try:
        name = client.recv(buffsize).decode("utf8")
        welcome_message = "Benvenuto! %s, per lasciare la chat digitare {quit}." % name
        client.send(bytes(welcome_message, "utf8"))
        msg = "%s si è unito alla chat!" % name
        broadcast(bytes(msg, "utf8"))

        clients[client] = name
        
        while True:
            msg = client.recv(buffsize)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg, name + ": ")
            else:
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                broadcast(bytes("%s ha abbandonato la chat!" % name, "utf8"))
                print(addresses[client], " si è scollegato.")
                break
    except Exception as e:
        print(f"Errore nella gestione del client: {e}")
        client.close()
        if client in clients:
            del clients[client]
            broadcast(bytes("%s ha abbandonato la chat!" % clients[client], "utf8"))
            print(addresses[client], " si è scollegato.")

# Invia un messaggio a tutti i client connessi.
# Usa un try-except per catturare e gestire eventuali eccezioni durante l'invio dei messaggi.
# Rimuove il client dalla lista se non è possibile inviargli un messaggio.
def broadcast(msg, prefisso=""):
    """Invia un messaggio a tutti i client connessi."""
    for utente in clients:
        try:
            utente.send(bytes(prefisso, "utf8") + msg)
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {e}")
            utente.close()
            del clients[utente]

if __name__ == "__main__":
    # Il server ascolta le connessioni in arrivo
    server.listen(5)
    print("In attesa di connessioni...")
    
    # Thread per accettare le connessioni in entrata
    accept_thread = Thread(target=incoming_connections)
    accept_thread.start()
    accept_thread.join()
    
    # Chiude il server quando il thread principale termina
    server.close()
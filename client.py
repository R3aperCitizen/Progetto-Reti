# -*- coding: utf-8 -*-
"""
Created on Tue June 11 16:37:49 2024

@author: matteo
"""

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter as tkt

# Funzione per ricevere i messaggi, che verrà invocata 
# in un thread sempre attivo dall'inizio della connessione
def receive_messages():
    while True:
        try:
            # Ricezione dei messaggi in arrivo sul socket
            message=client_socket.recv(BUFSIZE).decode("utf8")
            # Inserimento del messaggio nella lista dei messaggi visualizzati nella finestra
            messages_list.insert(tkt.END, message)
            
        # Se ci sono eccezioni dovute all'abbandono della chat non si attendono più nuovi messaggi
        except OSError:
            break
        

# Funzione per inviare messaggi, chiamata al momento della pressione del pulsante invio
def send_messages(event = None):
    # Lettura del messaggio da inviare dalla casella di invio e liberazione della casella
    message=my_msg.get()
    my_msg.set("")
    # Invio del messaggio sul socket
    client_socket.send(bytes(message, "utf8"))
    # Se il messaggio è quello con cui si termina la connessione si attende l'ultimo messaggio mandato dal server
    # e si chiudono il socket e la finestra
    if message == "{quit}":
        client_socket.recv(BUFSIZE)
        client_socket.close()
        window.destroy()
        
# Funzione che viene chiamata al momento della chiusura della finestra che chiude anche il socket
def close(event = None):
    my_msg.set("{quit}")
    send_messages()
    
# Creazione della finestra e impostazione del titolo
window = tkt.Tk()
window.title("Chat Client-Server")

# Creazione del frame per contenere i messaggi
messages_frame = tkt.Frame(window)
# Stringa per memorizzare i messaggi da inviare
my_msg = tkt.StringVar()
# Indicazione della casella per inviare i messaggi
my_msg.set("Scrivi un messaggio")
# Scrollbar per navigare nei messaggi precedenti
scrollbar = tkt.Scrollbar(messages_frame)

# Creazione della lista per contenere i messaggi in arrivo
messages_list = tkt.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
messages_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
messages_list.pack()
messages_frame.pack()

# Creazione del campo di input e associazione alla variabile stringa
entry_field = tkt.Entry(window, textvariable=my_msg)
# Collegamento della funzione invio al tasto Return
entry_field.bind("<Return>", send_messages)

entry_field.pack()
# Creazione del pulsante invio e associazione alla funzione invio
send_button = tkt.Button(window, text="Invio", command=send_messages)
# Integrazione del tasto nel pacchetto
send_button.pack()

# Associazione della funzione chiusura alla chiusura della finestra
window.protocol("WM_DELETE_WINDOW", close)


# Richiesta di inserimento della coppia indirizzo-porta del server
# se non viene specificato uno dei due vengono chiesti nuovamente
while True: 
    INDIRIZZO_SERVER=input("Inserire l'indirizzo IP del server host: ")
    PORTA_SERVER=input("Inserire la porta del server host: ")
    if not INDIRIZZO_SERVER or not PORTA_SERVER:
        print("Indirizzo non valido, inserire nuovamente")
    else:
        break

# Numero massimo di byte da ricevere
BUFSIZE=1024

PORTA_SERVER=int(PORTA_SERVER)
SERVER = (INDIRIZZO_SERVER, PORTA_SERVER)

# Creazione del socket e collegamento al server
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(SERVER)
# Creazione e avvio del thread che si occuperà di ricevere i messaggi
thread_ric = Thread(target=receive_messages)
thread_ric.start()
tkt.mainloop()

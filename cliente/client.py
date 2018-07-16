# -*- coding: utf-8 -*-
####################################################################################
# Autores: Domingo Arteaga y Edwar Yepez
# 
# Profesor: Yudith Cardinale
#
####################################################################################
from libro import *
from stat import *
import socket, pickle, os, sys , time, struct
from getopt import getopt, GetoptError


class Client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.connect_to_server()

    # Esta función conecta al cliente con el host y puerto recibido en el constructor
    def connect_to_server(self):
        print("Iniciando conexión con " + self.HOST + ":" + str(self.PORT) + "...")
        try:
            self.sock_central.connect( (self.HOST, self.PORT) )
            self.connected = True
            print("Conexión establecida con " + self.HOST + ":" + str(self.PORT))
        except Exception, error:
            print("No se ha podido establecer una conexión con el servidor :(")
        

    # Esta función le pide al servidor-maestro que nos liste los distintos autores y
    # libros que se encuentran en él.
    def recv_collections(self, mensaje):
        try:
            print("Pidiendo colecciones de libros...\n")
            self.sock_central.sendall(mensaje)
            data = self.sock_central.recv(4096)
            data_array = pickle.loads(data)
            print('¡Recibidas las colecciones disponibles!\n')
            
            if len(data_array[0]):
                print("\nEstos son los escritores:")
                for w in data_array[0]:
                    print(w)
            else:
                print("No hay libros disponibles :(")

            if len(data_array[1]):
                print("\nEstos son los generos:")
                for g in data_array[1]:
                    print(g)
        except Exception, error:
            print(error)
        finally:
            pass

    #Función que toma la elección del cliente sobre el criterio de busqueda para
    #la descarga de los libros.
    def download_lookup(self):
        while True:
            eleccion = raw_input("Quieres hacer la busqueda por genero o por autor? (g/a): \n")
            if eleccion.lower().replace(' ', '') == "g":
                categoria = raw_input("¿Cuál género te interesa? \n")
                mensaje = eleccion + ';' + categoria
                break
            elif eleccion.lower().replace(' ', '') == "a":
                escritor = raw_input("¿Cuál autor te interesa? \n")
                mensaje = eleccion + ';' + escritor
                break
            else:
                print("Ha introducido un caracter no valido. Recuerde escribir 'g' si quiere por genero o 'a' por autor. \n")
        return mensaje

    # Esta funcion le manda al cliente servidor-maestro el criterio de busqueda y recibe
    # las direcciones ip de los servidores de descarga y que libros quiere de cada
    # uno.
    def get_servers(self, mensaje):
        data_array = []
        try:
            self.sock_central.sendall(mensaje)
            data = self.sock_central.recv(4096)
            data_array = pickle.loads(data)
        except Exception, error:
            print (error)

        return data_array

    #Función que gestiona la descarga de los libros desde el servidor de descarga.
    #Recibe el peso del titulo y del archivo para leer de manera exacta cada libro.
    #La condición principal es que no voy a dejar de escribir mi archivo hasta que
    #pese lo mismo que su homólogo en el servidor de descarga.
    def download(self, data_array):
        
        for x in xrange(0,len(data_array)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the socket to the port where the server is listening
            server_address = (data_array[x][0], int(data_array[x][1]))
            
            data_array[x].pop(0)
            data_array[x].pop(0)
            print >>sys.stderr, 'connecting to %s port %s' % server_address
            sock.connect(server_address)

            try:
                
                # Send data
                mensaje = pickle.dumps(data_array[x])
                
                sock.sendall(mensaje)
                while True:
                    titulo_peso = sock.recv(4)
                    if titulo_peso == '':
                        break
                    titulo_peso = struct.unpack("<L",titulo_peso)[0]
           
                    titulo = sock.recv(titulo_peso)
                

                    f = os.open(titulo, os.O_WRONLY | os.O_CREAT | os.O_TRUNC , 0o666)
                    libro_peso = sock.recv(4)
                    libro_peso = struct.unpack("<L",libro_peso)[0]
                   

                    libro_recibido = os.fstat(f).st_size
                    libro_restante = 0
                    
                    while libro_recibido < libro_peso:
                        
                        libro_restante = libro_peso - libro_recibido
                        if libro_restante < 4096:
                            l = sock.recv(libro_restante)
                            os.write(f,l)
                        else:
                            l = sock.recv(4096)
                            os.write(f,l)
                        
                        libro_recibido = os.fstat(f).st_size


                    os.close(f)


            finally:
                print >>sys.stderr, 'Descarga exitosa.'
                sock.close()

#Función principal que toma la opción del menu y ejecuta el procedimiento
#adecuado.

if __name__ == "__main__":
    try:
        opts, args = getopt(sys.argv[1:], "", ['host=', 'port='])
    except GetoptError as err:
        print(err) 
        sys.exit(2)

    HOST = 'localhost'
    PORT = '10855'
    for o, a in opts:
        if o == "--host":
            HOST = a
        elif o == "--port":
            PORT = int(a)
        else:
            assert False, "unhandled option"

    # print(HOST, PORT)

    client = Client(HOST, PORT)

    while True:
        if not client.connected:
            choice = raw_input("¿Quieres volver a intentarlo? (y/n): ")
            if choice.replace(' ', '').lower() == "y":
                client.connect_to_server()
            else:
                sys.exit(0)
        else:
            break    

    while True:
        os.system('clear')
        print('Menu')
        print('1. Imprimir colecciones de libros')
        print('2. Descargar libros')
        print('3. Salir')
        choice = raw_input("Escoja una opcion valida: ")

        if choice.replace(' ', '') == "2":
            lookup = client.download_lookup()
            petitions = client.get_servers(lookup)
            client.download(petitions)
            raw_input("\npulsa enter para continuar")
        elif choice.replace(' ', '') == "1":
            client.recv_collections(choice)
            raw_input("\npulsa enter para continuar")
        elif choice.replace(' ', '') == "3":
            sys.exit(0)
        else:
            print('Esa no es una opción válida. Vuelva a intentar')

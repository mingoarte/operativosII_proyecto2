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


#Función que toma la elección del cliente sobre el criterio de busqueda para
#la descarga de los libros.
def libros_autor_genero():
    
    while True:
        eleccion = raw_input("Quieres hacer la busqueda por genero o por autor? (g/a): \n")
        if eleccion.lower().replace(' ', '') == "g":
            categoria = raw_input("Cual genero te interesa? \n")
            mensaje = eleccion + ';' + categoria
            break
        elif eleccion.lower().replace(' ', '') == "a":
            escritor = raw_input("Cual autor te interesa? \n")
            mensaje = eleccion + ';' + escritor
            break
        else:
            print("Ha introducido un caracter no valido. Recuerde escribir g si quiere por genero o a por autor. \n")



    return mensaje

#Esta funcion le manda al cliente servidor-maestro el criterio de busqueda y recibe
#las direcciones ip de los servidores de descarga y que libros quiere de cada
#uno.
def lista_libros(mensaje):
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Direccion del servidor maestro.
    master_server_address = ('192.168.0.106', 10776)
    sock_central.connect(master_server_address)

    try:

        sock_central.sendall(mensaje)
        data = sock_central.recv(4096)
        data_array = pickle.loads(data)

    finally:
        print >>sys.stderr, 'closing socket to master'
        sock_central.close()

    return data_array

#Esta función le pide al servidor-maestro que nos liste los distintos autores y
#libros que se encuentran en él.
def coleccion_libros(mensaje):
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Direccion del servidor maestro.
    master_server_address = ('192.168.0.106', 10776)
    sock_central.connect(master_server_address)

    try:

        sock_central.sendall(mensaje)
        data = sock_central.recv(4096)
        print('recibi colecciones')
        data_array = pickle.loads(data)
        print("\nEstos son los escritores:")
        for y in xrange(0,len(data_array[0])):
            print(data_array[0][y])
        print("\nEstos son los generos:")
        for y in xrange(0,len(data_array[1])):
            print(data_array[1][y])

                

    finally:
        sock_central.close()

#Función para tomar un número en bytes y pasarlo a enteros.
def bytes_to_number(b):
    # if Python2.x
    b = map(ord, b)
    res = 0
    for i in range(4):
        res += b[i] << (i*8)
    return res

#Función que gestiona la descarga de los libros desde el servidor de descarga.
#Recibe el peso del titulo y del archivo para leer de manera exacta cada libro.
#La condición principal es que no voy a dejar de escribir mi archivo hasta que
#pese lo mismo que su homólogo en el servidor de descarga.
def descarga(data_array):
    
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
def menu():
    while True:
        os.system('clear')
        print('Menu')
        print('1. Imprimir colecciones de libros')
        print('2. Descargar libros')
        eleccion = raw_input("Escoja una opcion valida \n")

        if eleccion.replace(' ', '') == "2":
            mensaje = libros_autor_genero()
            peticion = lista_libros(mensaje)
            descarga(peticion)
            raw_input("\npulsa enter para continuar")
        elif eleccion.replace(' ', '') == "1":
            coleccion_libros(eleccion)
            raw_input("\npulsa enter para continuar")
        else:
            print('Esa no es una opcion valida. Vuelva a intentar')


menu()

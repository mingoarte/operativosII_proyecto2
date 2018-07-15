# -*- coding: utf-8 -*-
####################################################################################
# Autores: Domingo Arteaga y Edwar yepez
# 
# Profesor: Yudith Cardinale
####################################################################################

from linkedList import *
from libro import *
import pickle , threading, sys, socket


master_biblioteca = []
libros_descargados = []


#Creacion del socket por el que se conectan los servidores
#de descarga.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.0.106', 10777)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(10)

#Creacion del socket por el que se conectan los clientes.
sock_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.0.106', 10776)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock_cliente.bind(server_address)
sock_cliente.listen(10)


#Funcion que recolecta la lista de libros que hay en cada servidor
#de descarga, su direccion ip y su puerto de escucha.
def recoleccion():
	
	while True:
		print >>sys.stderr, 'waiting for a connection'
		connection, client_address = sock.accept()
		try:

			data = connection.recv(4096)
			data_array = pickle.loads(data)
			master_biblioteca.append(data_array)
			libros_descargados.append([])

		
		finally:
			# Clean up the connection
			connection.close()

#Funcion de busqueda de libros por genero para filtrarlos y
#devolver una lista de servidores que los contienen.
def busqueda_genero(genero):
	lista_servidores = []
	lista_enlazada = LinkedList()
	for x in xrange(0,len(master_biblioteca)):
		direccion = []
		find = False
		for y in xrange(2,len(master_biblioteca[x])):
			if (master_biblioteca[x][y].genero == genero):
				if master_biblioteca[x][y] not in lista_enlazada:
					lista_enlazada.add(master_biblioteca[x][y])
					direccion.append(master_biblioteca[x][y])

					find = True

					if len(libros_descargados[x]) != 0:
						is_in = False
						for i in xrange(0,len(libros_descargados[x])):
							if master_biblioteca[x][y] == libros_descargados[x][i][0]:
								libros_descargados[x][i][1]+=1
								is_in = True
						if not is_in:
							libros_descargados[x].append( [master_biblioteca[x][y], 1] )
							
					else:
						libros_descargados[x].append( [master_biblioteca[x][y], 1] )



		if find:
			direccion.insert(0,master_biblioteca[x][0])
			direccion.insert(1,master_biblioteca[x][1])
			lista_servidores.append(direccion)
	return(lista_servidores)

#Funcion de busqueda de libros por autor para filtrarlos y
#devolver una lista de servidores que los contienen.
def busqueda_autor(autor):
	lista_servidores = []
	lista_enlazada = LinkedList()
	for x in xrange(0,len(master_biblioteca)):
		direccion = []
		find = False
		for y in xrange(2,len(master_biblioteca[x])):
			if (master_biblioteca[x][y].autor == autor):
				if master_biblioteca[x][y] not in lista_enlazada:
					lista_enlazada.add(master_biblioteca[x][y])
					direccion.append(master_biblioteca[x][y])
					find = True

					if len(libros_descargados[x]) != 0:
						is_in = False
						for i in xrange(0,len(libros_descargados[x])):
							if master_biblioteca[x][y] == libros_descargados[x][i][0]:
								libros_descargados[x][i][1]+=1
								is_in = True
						if not is_in:
							libros_descargados[x].append( [master_biblioteca[x][y], 1] )
							
					else:
						libros_descargados[x].append( [master_biblioteca[x][y], 1] )



		if find:
			direccion.insert(0,master_biblioteca[x][0])
			direccion.insert(1,master_biblioteca[x][1])
			lista_servidores.append(direccion)
	return(lista_servidores)

#Funcion principal que crea los hilos para escuchar a los clientes
#y a los servidores de descarga, ademas de manejar las opciones del menu.
def menu():
	hilo = threading.Thread(target=conexion_cliente)
	hilo.start()
	hilo2 = threading.Thread(target = recoleccion)
	hilo2.start()
	while True:
		os.system('clear')
		print('Menu')
		print('1. Descargas por servidor')
		eleccion = raw_input("Escoja una opcion valida: ")
		if eleccion.replace(' ', '') == '1':
			os.system('clear')
			print('Descargas por servidor:')
			for x in xrange(0,len(libros_descargados)):
				print('Servidor ' + master_biblioteca[x][0] + ':\n')
				for y in xrange(0,len(libros_descargados[x])):
					print ('Libro: ' + str(libros_descargados[x][y][0]) + '\tNo Descargas: ' + str(libros_descargados[x][y][1]))
			raw_input("\npulsa enter para continuar")
		else:
			print("Esa no es una opcion valida. Vuelva a intentar")
			raw_input("\npulsa enter para continuar")

 

#Funcion que se encarga buscar todos los autores y generos a los 
#que pertenecen los libros y mandarlos como catalogos.	

def conexion_cliente():
	while True:
		connection, client_address = sock_cliente.accept()
		
		try:

			# Receive the data in small chunks and retransmit it
			data = connection.recv(99)
			if data.replace(' ', '') != "1":
				data = data.split(';')


				if data[0].lower().replace(' ', '') == 'a':
					lista_servidores = busqueda_autor(data[1])
				else:
					lista_servidores = busqueda_genero(data[1])

				data_string = pickle.dumps(lista_servidores)
				connection.sendall(data_string)
			else:
				envio = []
				escritores = []
				generos = []
				for x in xrange(0,len(master_biblioteca)):
					for y in xrange(2,len(master_biblioteca[x])):
						if master_biblioteca[x][y].autor not in escritores:
							escritores.append(master_biblioteca[x][y].autor)
						if master_biblioteca[x][y].genero not in generos:
							generos.append(master_biblioteca[x][y].genero)
				envio.append(escritores)
				envio.append(generos)
				data_string = pickle.dumps(envio)
				connection.sendall(data_string)
					
		finally:
			# Clean up the connection
			connection.close()


menu()

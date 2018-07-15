# -*- coding: utf-8 -*-
####################################################################################
# Autores: Domingo Arteaga y edwar Yepez
# 
# Profesor: Yudith Cardinale
#
####################################################################################
from stat import *
from os import path
from libro import *
from pathlib import Path
import socket , pickle , copy, sys , time, threading




#Variables globales:

#La mayoria son listas que se usan para el envio y la recepcion
#de la transmision. Además tenemos como variable la ruta de la 
#carpeta en la que nos encontramos y el socket que se utiliza para
#escuchar
biblioteca = []
libros_descargados = []
libros_en_descarga = []
clientes = []
descargas_clientes = []
cwd = os.getcwd()
sock_escucha = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#Esta función toma un entero y lo representa en bytes:
def convert_to_bytes(no):
    result = bytearray()
    result.append(no & 255)
    for i in range(3):
        no = no >> 8
        result.append(no & 255)
    return result

#En esta funcion nos inscribimos en el servidor-maestro y creamos
#el socket para transmitir a los clientes.
def levantarse():
	inscripcion_central()
	# Create a TCP/IP socket

	# Bind the socket to the port
	server_address = ('192.168.0.106', 10000)
	print >>sys.stderr, 'starting up on %s port %s' % server_address
	sock_escucha.bind(server_address)


	# Listen for incoming connections
	sock_escucha.listen(3)


#Agregar libro a la biblioteca del servidor de descarga. Al final esta
#lista de libros se guarda en un archivo de texto para ser cargada la 
#próxima vez que se corra el servidor.
def agregar_libro():
	listo = True
	while listo:
		name = raw_input('Introduzca el titulo del libro: ')
		print(name)
		author = raw_input('Introduzca el autor: ')
		print(author)
		genre = raw_input('Introduzca el genero: ')
		print(genre)
		biblioteca.append(libro(name, author, genre))
		libros_descargados.append(False)
		respuesta = raw_input('Quiere agregar otro libro?')
		if respuesta.lower().replace(' ', '') != 'si':
			listo = False
		guardar_biblioteca()

#Esta funcion muestra el menu con el que se puede interactuar durante
#toda la ejecución.
def print_menu():
	os.system('clear')
	print('Menu')
	print('1. Agregar libro')
	print('2. Listar libros')
	print('3. Ver libros en descarga')
	print('4. Ver libros descargados')
	print('5. Ver clientes favoritos')
	print('6. Salir')

#Este es el proceso que gestiona la elección del menú anterior. Además se 
#encarga de cargar los libros de la biblioteca y empezar el hilo de la 
#descarga.
def menu():
	if biblioteca == []:
		cargar_biblioteca()
	levantarse()
	hilo = threading.Thread(target=descarga)
	hilo.start()
	while True:
		print_menu()
		choice = input('Introduzca su opcion: ')

		if choice == 1:
			agregar_libro()
			print('Se ha agregado el libro exitosamente\n')
			raw_input("\npulsa enter para continuar")

		elif choice == 2:
			os.system('clear')
			print('Esta es la lista de libros disponible actualmente: \n\n')
			for x in xrange(0,len(biblioteca)):
				print(str(biblioteca[x]))
			raw_input("\npulsa enter para continuar")
		elif choice == 3:
			os.system('clear')
			print('Estos son los libros que se estan descargando: \n\n')
			for x in xrange(0, len(libros_en_descarga) ):
				print(libros_en_descarga[x] )
			raw_input("\npulsa enter para continuar")
		elif choice == 4:
			os.system('clear')
			print('Estos son los libros que se han descargado: \n\n')
			for x in xrange(0,len(libros_descargados)):
				if libros_descargados[x]:
					print(biblioteca[x] )
			raw_input("\npulsa enter para continuar")
		
		elif choice == 5:
			os.system('clear')
			print('Este es el ranking de clientes que han descargado de este servidor: \n\n')
			buscar_favorito()
			raw_input("\npulsa enter para continuar")

		elif choice == 6:
			sys.exit(0)
		
		else:
			print('Esa no es una opcion valida. Intente de nuevo')
			raw_input("\npulsa enter para continuar")
	
#Función que se encarga de guardar los libros que creemos en en archivo 
#de texto.
def guardar_biblioteca():
	f = open('biblioteca.txt','wb')
	f.write( str(len(biblioteca)) + '\n' )
	for x in xrange(0,len(biblioteca)):
		f.write(biblioteca[x].titulo + '\n')
		f.write(biblioteca[x].autor + '\n')
		f.write(biblioteca[x].genero + '\n\n')
	f.close()

#Función que se encarga de cargar los libros que tengamos en el 
#archivo de texto.
def cargar_biblioteca():
	
	biblioteca_exist = Path(path.join(cwd,'biblioteca.txt'))
	if biblioteca_exist.is_file():
		f = open('biblioteca.txt','r')
		num_libros = int(f.readline())
		for x in xrange(0,num_libros):
			name = f.readline().replace('\n','')
			author = f.readline().replace('\n','')
			genre = f.readline().replace('\n', '')
			biblioteca.append(libro(name, author, genre))
			libros_descargados.append(False)
			f.readline()

		f.close()
	else:
		print('No hay archivo de carga. Hay que hacerlo manualmente.\n')

#Función que se encarga de enviar al servidor-maestro mi dirección ip, 
#mi puerto de escucha y la lista de libros que poseo.
def inscripcion_central():
	sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Direccion del servidor maestro.
	master_server_address = ('192.168.0.106', 10777)
	sock_central.connect(master_server_address)
	try:
	# Send data
		server_ip = '192.168.0.106'
		server_port = '10000'
		biblioteca.insert(0,server_ip)
		biblioteca.insert(1,server_port)
		data_string = pickle.dumps(biblioteca)
		sock_central.sendall(data_string)


	finally:
		#print >>sys.stderr, 'closing socket to master'
		sock_central.close()
		biblioteca.pop(0)
		biblioteca.pop(0)

#Función que busca cuales son los clientes que mas libros han descargado
#de mi biblioteca.
def buscar_favorito():
	list_temp = copy.deepcopy(descargas_clientes)
	list_temp.sort(reverse = True)
	list_temp = list(set(list_temp))
	if len(list_temp) >= 3:
		for x in xrange(0, 3):
			print('Top ' + str(x+1))
			for y in xrange(0,len(descargas_clientes)):
				if descargas_clientes[y] == list_temp[x]:
					print('Cliente: ' + str(clientes[y]) + '\tNumero de descargas: ' + str(descargas_clientes[y]) )
	else:
		for x in xrange(0, len(list_temp)):
			print('Top ' + str(x+1))
			for y in xrange(0,len(descargas_clientes)):
				if descargas_clientes[y] == list_temp[x]:
					print('Cliente: ' + str(clientes[y]) + '\tNumero de descargas: ' + str(descargas_clientes[y]) )		

#Función que gestiona la descarga de libros con el cliente. Manda primero el peso,
#del título y del archivo para que el cliente sepa exactamente cuanto tiene que 
#leer.
def descarga():
	while True:
		connection, client_address = sock_escucha.accept()
		if client_address[0] not in clientes:
			clientes.append(client_address[0])
			descargas_clientes.append(0)
		
		try:

			while True:
				data = connection.recv(4096)
				libros_en_descarga = pickle.loads(data)
				descargas_clientes[len(clientes)-1] += len(libros_en_descarga)
				for x in xrange(0,len(biblioteca)):

					for y in xrange(0,len(libros_en_descarga)):
						
						if (biblioteca[x] == libros_en_descarga[y]) :
							libros_descargados[x] = True

							libro_titulo = convert_to_bytes(len(biblioteca[x].titulo))
							connection.send(libro_titulo)
							
							connection.send(biblioteca[x].titulo)
							
							peso = convert_to_bytes(os.stat(biblioteca[x].titulo).st_size)
							connection.send(peso)

							file = open(biblioteca[x].titulo,'rb')
							l = file.read(os.stat(biblioteca[x].titulo).st_size)
							connection.send(l)

				break
					
		finally:

			connection.close()

menu()

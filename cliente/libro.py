# -*- coding: utf-8 -*-
####################################################################################
# Autores: Domingo Arteaga y Edwar Yepez
# 
# Profesor: Yudith Cardinale 
#
####################################################################################
import os
from pathlib import Path


# Clase que representa los libros de descarga
# Atributos: titulo: titulo del libro
#            autor: autor de la cancion
#            genero: genero del libro
#            contenido: ruta completa del libro de descarga 
class libro:
	def __init__(self, titulo, autor, genero):
		cwd = os.getcwd()
		self.titulo = titulo
		self.autor = autor
		self.genero = genero
		self.contenido = os.path.join(cwd,titulo)


	#Función que compara dos libros y retorna si son iguales o no. 
	# Atributos: libro: libro a comparar
	def __eq__(self, libro):
		igual = False
		if 	self.titulo.upper().replace(' ','') == libro.titulo.upper().replace(' ','')\
		 	and self.autor.upper().replace(' ','') == libro.autor.upper().replace(' ',''):
			igual = True
		return igual

	def __str__(self):
		return self.titulo + ', ' + self.autor + ', ' + self.genero

	def __ne__(self, libro):
		distinto = True
		if 	self.titulo.upper().replace(' ','') == libro.titulo.upper().replace(' ','')\
		 	and self.autor.upper().replace(' ','') == libro.autor.upper().replace(' ',''):
			distinto = False
		return distinto

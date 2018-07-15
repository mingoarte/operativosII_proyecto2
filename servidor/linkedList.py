# -*- coding: utf-8 -*-
####################################################################################
# Autor: Domingo Arteaga y Edwar yepez
# 
# Profesor: Yudith Cardinale
# Credito: Basado en una lista enlazada del Prof. Federico Flaviani
####################################################################################

# Descripcion: Clase que implementa el nodo de una lista
#   Atributos: data: almacena el contenido del nodo
#              next: referencia al proximo nodo

class ListNode:
  def __init__(self,data, link = None):
    self.data = data
    self.next = link

# Clase que implementa una lista enlazada
#   Atributos: _head: atributo privado que referencia al primer elemento de la lista
#              _size: atributo privado entero que indica la longitud de la lista

class LinkedList:
  def __init__(self):
    self._head = None
    self._size = 0

#Funcion que devuelve la longitud de la lista.
  def __len__(self):
    return self._size

#funcion que verifica si el elemento target se encuentra
#en algun nodo de la lista.
  def __contains__(self, target):
    curNode = self._head
    while curNode is not None and curNode.data != target:
      curNode = curNode.next
    return curNode is not None

#funcion que agrega un nuevo elemeto item dentro de la lista
  def add(self, item):
    newNode = ListNode(item)
    newNode.next = self._head
    self._head = newNode
    self._size += 1

#funcion que elimina el elemento item y su respectivo
#nodo de la lista.
  def remove(self,item):
    predNode = None
    curNode = self._head
    while curNode is not None and curNode.data != item :
      predNode = curNode
      curNode = curNode.next

    assert curNode is not None, "El elemento tiene que estar en la lista para poder eliminarlo."

    self._size -= 1
    if curNode is self._head:
       self._head = curNode.next
    else:
       predNode.next = curNode.next
    return curNode.data

#funcion que devuelve un iterador de la lista

  def __iter__(self):
    return ListIterator(self._head)

# Clase que implementa un iterador de lista
#   Atributos: _curNode: atributo privado que hace referencia al
#              nodo "actual" en el que se encuentra el iterador

class ListIterator:
  def __init__(self,listHead):
    self._curNode = listHead

# funcion que devuelve un iterador de la lista
  def __iter__(self):
    return self

#funcion que devuelve el elemento del proximo nodo 
#en el que se encuentra el iterador y actualiza el
#nodo "actual" a su sucesor.

  def next(self):
    if self._curNode is None:
      raise StopIteration
    else :
      item = self._curNode.data
      self._curNode = self._curNode.next
      return item

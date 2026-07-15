#BACKEND ACCIONES.py

import random, time, colorama

# Variables globales para persistencia
_saldo = 100000
_acciones = 0
_valor_accion = 100

def saldo():
    global _saldo
    return _saldo

def actualizar_saldo(cantidad):
    global _saldo
    _saldo += cantidad
    return _saldo

def acciones():
    global _acciones
    return _acciones

def actualizar_acciones(cantidad):
    global _acciones
    _acciones += cantidad
    return _acciones

def valor_accion():
    global _valor_accion
    return _valor_accion

def actualizar_valor_accion(nuevo_valor):
    global _valor_accion
    _valor_accion = nuevo_valor
    return _valor_accion

def comprar(cantidad):
    global _saldo, _acciones, _valor_accion
    costo = cantidad * _valor_accion
    if _saldo >= costo:
        _saldo -= costo
        _acciones += cantidad
        return True, f"Compraste {cantidad} acciones por ${costo}"
    else:
        return False, f"Saldo insuficiente. Necesitas ${costo}"

def vender(cantidad):
    global _saldo, _acciones, _valor_accion
    if _acciones >= cantidad:
        ganancia = cantidad * _valor_accion
        _saldo += ganancia
        _acciones -= cantidad
        return True, f"Vendiste {cantidad} acciones por ${ganancia}"
    else:
        return False, f"No tienes suficientes acciones. Tienes {_acciones}"

def verificar_victoria():
    global _saldo
    return _saldo >= 1000000


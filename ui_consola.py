#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades de colores ANSI, limpieza de pantalla y paginación limpia para consola.
"""

import os
import sys

# Códigos ANSI estándar
RESET = "\033[0m"
NEGRITA = "\033[1m"
CYAN = "\033[96m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
ROJO = "\033[91m"
AZUL = "\033[94m"
MAGENTA = "\033[95m"
BLANCO = "\033[97m"
GRIS = "\033[90m"


def inicializar_consola():
    """Habilita UTF-8 y secuencias ANSI de color en Windows CMD / PowerShell / Terminal."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            os.system("")


def limpiar_pantalla():
    """Limpia la pantalla visible y el historial de scroll para que nunca se mezcle nada."""
    if sys.stdout.isatty():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        # Secuencia ANSI: limpia buffer de scrollback + pantalla + cursor en (1,1)
        sys.stdout.write("\033[3J\033[2J\033[H")
        sys.stdout.flush()


def c(texto: str, color: str) -> str:
    return f"{color}{texto}{RESET}"


def imprimir_banner(linea1: str, linea2: str = None, color: str = CYAN):
    print(f"\n{color}{NEGRITA}" + "=" * 78 + RESET)
    print(f"{color}{NEGRITA}  {linea1}{RESET}")
    if linea2:
        print(f"{color}{NEGRITA}  {linea2}{RESET}")
    print(f"{color}{NEGRITA}" + "=" * 78 + RESET)
    print()


def pausa_seccion(siguiente_texto: str, permitir_saltar: bool = False) -> bool:
    """
    Pausa entre bloques grandes de salida y limpia la consola antes de mostrar el siguiente.
    En modo no interactivo (redirección / pruebas CLI) continúa sin pausar.
    Retorna True si el usuario eligió saltar (cuando permitir_saltar=True), False en caso contrario.
    """
    if not sys.stdin.isatty():
        print()
        return False

    print(f"\n{AMARILLO}" + "-" * 78 + RESET)
    if permitir_saltar:
        resp = input(
            f"  {AMARILLO}>> Presione ENTER para continuar ({siguiente_texto}) o 's' para terminar: {RESET}"
        ).strip().lower()
        limpiar_pantalla()
        return resp == "s"
    else:
        input(f"  {AMARILLO}>> Presione ENTER para ver: {siguiente_texto}...{RESET}")
        limpiar_pantalla()
        return False

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Carrera    : Ingeniería en Sistemas
Asignatura : Análisis y Diseño de Algoritmos (2026)
Evaluación : Examen 2 - Práctica (Sistema Interactivo de Resolución)
================================================================================
"""

import sys
import ui_consola as ui
import punto1_corrector
import punto2_floyd_warshall
import punto3_sopa_letras
import punto4_utilidad


def mostrar_menu_principal():
    ui.limpiar_pantalla()
    ui.imprimir_banner(
        "UNIVERSIDAD NACIONAL DE VILLA MERCEDES - ANÁLISIS Y DISEÑO DE ALGORITMOS",
        "              EXAMEN 2 - PRÁCTICA | MENÚ INTERACTIVO (2026)",
        ui.CYAN,
    )
    print(f"\n  {ui.BLANCO}{ui.NEGRITA}OPCIONES DEL MENÚ:{ui.RESET}\n")
    print(
        f"    {ui.VERDE}{ui.NEGRITA}1){ui.RESET} Punto 1 — Corrector Ortográfico (Levenshtein - PD)          "
        f"{ui.VERDE}{ui.NEGRITA}[LISTO]{ui.RESET}"
    )
    print(
        f"    {ui.VERDE}{ui.NEGRITA}2){ui.RESET} Punto 2 — Caminos Mínimos en Grafo (Floyd-Warshall)         "
        f"{ui.VERDE}{ui.NEGRITA}[LISTO]{ui.RESET}"
    )
    print(
        f"    {ui.VERDE}{ui.NEGRITA}3){ui.RESET} Punto 3 — Búsqueda de Palabras en Matriz de Caracteres      "
        f"{ui.VERDE}{ui.NEGRITA}[LISTO]{ui.RESET}"
    )
    print(
        f"    {ui.VERDE}{ui.NEGRITA}4){ui.RESET} Punto 4 — \"Mejor período de utilidad\" (1.000.000 datos)     "
        f"{ui.VERDE}{ui.NEGRITA}[LISTO]{ui.RESET}"
    )
    print()
    print(f"    {ui.ROJO}s){ui.RESET} Salir del programa")
    print(f"\n{ui.CYAN}" + "=" * 78 + ui.RESET)


def main():
    ui.inicializar_consola()

    # Modo ejecución directa para pruebas automatizadas
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg == "--punto1":
            punto1_corrector.ejecutar_resolucion_completa()
            return
        if arg == "--punto2":
            punto2_floyd_warshall.ejecutar_resolucion_completa()
            return
        if arg == "--punto3":
            punto3_sopa_letras.ejecutar_resolucion_completa()
            return
        if arg == "--punto4":
            punto4_utilidad.ejecutar_resolucion_completa()
            return

    while True:
        mostrar_menu_principal()
        opcion = input(f"  {ui.AMARILLO}Seleccione una opción [1-4 / s para salir]: {ui.RESET}").strip().lower()

        if opcion == "1":
            punto1_corrector.mostrar_submenu_punto1()
        elif opcion == "2":
            punto2_floyd_warshall.mostrar_submenu_punto2()
        elif opcion == "3":
            punto3_sopa_letras.mostrar_submenu_punto3()
        elif opcion == "4":
            punto4_utilidad.mostrar_submenu_punto4()
        elif opcion in ("s", "salir", "0", "q"):
            print(f"\n  {ui.CYAN}Saliendo del programa. ¡Hasta luego!{ui.RESET}")
            break
        else:
            print(f"\n  {ui.ROJO}[!] Opción '{opcion}' no válida. Intente nuevamente.{ui.RESET}")
            input(f"\n  {ui.GRIS}Presione ENTER para volver al menú principal...{ui.RESET}")


if __name__ == "__main__":
    main()

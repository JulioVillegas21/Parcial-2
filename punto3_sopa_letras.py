#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Asignatura : Análisis y Diseño de Algoritmos
Examen 2 - Práctica | Punto 3: Búsqueda de Palabras en una Matriz de Caracteres
================================================================================

Implementa dos enfoques y los compara empíricamente:
1. Estrategia principal elegida — Árbol Trie (Transforma y Conquista: Cambio de
   Representación, Unidad 6 + búsqueda de múltiples patrones, Unidad 3 Diap. 28-29)
   combinado con recorrido en las 8 direcciones y poda temprana en O(1) por prefijo.
2. Estrategia baseline — Fuerza Bruta (Brute Force String Match 2D, Unidad 3
   Diap. 25-27), buscando cada palabra independientemente en las 8 direcciones.
"""

import time
import ui_consola as ui

# Matriz exacta de 20x20 caracteres tomada de la hoja del examen
MATRIZ_EXAMEN = [
    "WREDLQWERTYUIOPASDFG",  # Fila 0
    "ZXUVBNMLKJHARBOLQWER",  # Fila 1  -> ARBOL (1,11)..(1,15) Derecha
    "TYUIOPASDFGHJKLZXCVB",  # Fila 2
    "MOUKSQWERTYUIOPHSDFG",  # Fila 3  -> HEAPS empieza en (3,15) Abajo
    "MNBVCXZLKJHGFDSEQWER",  # Fila 4
    "QWERTYUIOPASDFGAJKLZ",  # Fila 5
    "XCVBNMLKJHGFDSAPWERT",  # Fila 6
    "HQWPNODOSTYUIOPSSDFG",  # Fila 7  -> NODOS (7,4)..(7,8) Derecha | HEAPS termina (7,15)
    "ZXCVBNMLKJHGFDSAQWER",  # Fila 8
    "RREFOQWERTYUIOPASDFG",  # Fila 9
    "ASDFGHJKLZXCVBNMQWER",  # Fila 10
    "TYUIOPASDFGHJKLZXCVB",  # Fila 11
    "NMQWERTYUIOSORTSGHJK",  # Fila 12 -> SORTS (12,11)..(12,15) Derecha
    "LZXCVBNMQWERTYUIOPAS",  # Fila 13
    "DFGHJKLZXCVBNMQWERTY",  # Fila 14
    "UIOPGSDFGHJKLZXCVBNM",  # Fila 15 -> GRAFO empieza en (15,4) Abajo
    "LQRKRQWERTYUIOPASDFG",  # Fila 16
    "ZXCVANMLKJHGFDSAQWER",  # Fila 17
    "TYUIFPASDFGHJKLZXCVB",  # Fila 18
    "NMQWORTYUIOPASDFGHJK",  # Fila 19 -> GRAFO termina en (19,4)
]

PALABRAS_OCULTAS = ["ARBOL", "HEAPS", "SORTS", "NODOS", "GRAFO"]

# Las 8 direcciones posibles indicadas en el enunciado
DIRECCIONES = [
    (-1, 0, "Arriba"),
    (1, 0, "Abajo"),
    (0, -1, "Izquierda"),
    (0, 1, "Derecha"),
    (-1, -1, "Diagonal superior izquierda"),
    (-1, 1, "Diagonal superior derecha"),
    (1, -1, "Diagonal inferior izquierda"),
    (1, 1, "Diagonal inferior derecha"),
]

COLORES_PALABRAS = {
    "ARBOL": ui.VERDE,
    "HEAPS": ui.AMARILLO,
    "SORTS": ui.CYAN,
    "NODOS": ui.MAGENTA,
    "GRAFO": ui.ROJO,
}


class NodoTrie:
    """Nodo del Árbol de Prefijos (Trie) para búsqueda simultánea de múltiples palabras."""

    def __init__(self):
        self.hijos = {}
        self.palabra_completa = None


class Trie:
    def __init__(self):
        self.raiz = NodoTrie()

    def insertar(self, palabra: str):
        actual = self.raiz
        for ch in palabra.upper():
            if ch not in actual.hijos:
                actual.hijos[ch] = NodoTrie()
            actual = actual.hijos[ch]
        actual.palabra_completa = palabra.upper()

    def imprimir(self):
        print(f"  {ui.CYAN}{ui.NEGRITA}(raíz Trie){ui.RESET}")
        self._imprimir_nodo(self.raiz, "  ")

    def _imprimir_nodo(self, nodo: NodoTrie, prefijo: str):
        items = sorted(nodo.hijos.items(), key=lambda kv: kv[0])
        for idx, (letra, hijo) in enumerate(items):
            es_ultimo = idx == len(items) - 1
            conector = "└── " if es_ultimo else "├── "
            fin = (
                f"  {ui.VERDE}{ui.NEGRITA}[FIN: {hijo.palabra_completa}]{ui.RESET}"
                if hijo.palabra_completa
                else ""
            )
            print(f"{ui.GRIS}{prefijo}{conector}{ui.RESET}{ui.AMARILLO}{letra}{ui.RESET}{fin}")
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            self._imprimir_nodo(hijo, nuevo_prefijo)


def buscar_con_trie(matriz, palabras):
    """
    Estrategia Principal: Árbol Trie (Transforma y Conquista) + Recorrido en 8 direcciones.
    - Preprocesamiento: inserta todas las palabras en un Trie en O(sum(L)).
    - Recorre la matriz UNA SOLA VEZ: si la celda inicial no está en la raíz del Trie,
      descarta en O(1) todas las palabras y las 8 direcciones de golpe.
    """
    t0 = time.perf_counter()

    trie = Trie()
    for p in palabras:
        trie.insertar(p)

    filas = len(matriz)
    cols = len(matriz[0])
    hallazgos = {p.upper(): [] for p in palabras}
    comparaciones = 0
    celdas_descartadas_raiz = 0

    for r in range(filas):
        for c in range(cols):
            ch0 = matriz[r][c]
            comparaciones += 1  # Consulta de prefijo inicial en la raíz del Trie
            if ch0 not in trie.raiz.hijos:
                celdas_descartadas_raiz += 1
                continue

            nodo_inicial = trie.raiz.hijos[ch0]
            if nodo_inicial.palabra_completa:
                hallazgos[nodo_inicial.palabra_completa].append({
                    "palabra": nodo_inicial.palabra_completa,
                    "inicio": (r, c),
                    "fin": (r, c),
                    "direccion": "Única celda",
                    "celdas": [(r, c)],
                })

            # Explorar las 8 direcciones avanzando solo mientras exista la rama en el Trie
            for dr, dc, nombre_dir in DIRECCIONES:
                actual = nodo_inicial
                nr, nc = r + dr, c + dc
                celdas = [(r, c)]

                while 0 <= nr < filas and 0 <= nc < cols:
                    ch = matriz[nr][nc]
                    comparaciones += 1
                    if ch not in actual.hijos:
                        break
                    actual = actual.hijos[ch]
                    celdas.append((nr, nc))
                    if actual.palabra_completa:
                        hallazgos[actual.palabra_completa].append({
                            "palabra": actual.palabra_completa,
                            "inicio": (r, c),
                            "fin": (nr, nc),
                            "direccion": nombre_dir,
                            "celdas": list(celdas),
                        })
                    nr += dr
                    nc += dc

    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return {
        "estrategia": "Árbol Trie + Búsqueda en 8 Direcciones",
        "trie": trie,
        "hallazgos": hallazgos,
        "comparaciones": comparaciones,
        "celdas_descartadas_raiz": celdas_descartadas_raiz,
        "tiempo_ms": tiempo_ms,
    }


def buscar_fuerza_bruta(matriz, palabras):
    """
    Estrategia Baseline: Fuerza Bruta (Unidad 3 — Brute Force String Match 2D).
    Para cada palabra recorre todas las celdas y prueba las 8 direcciones letra por letra.
    """
    t0 = time.perf_counter()

    filas = len(matriz)
    cols = len(matriz[0])
    hallazgos = {p.upper(): [] for p in palabras}
    comparaciones = 0

    for palabra in palabras:
        p = palabra.upper()
        L = len(p)
        for r in range(filas):
            for c in range(cols):
                comparaciones += 1
                if matriz[r][c] != p[0]:
                    continue
                if L == 1:
                    hallazgos[p].append({
                        "palabra": p,
                        "inicio": (r, c),
                        "fin": (r, c),
                        "direccion": "Única celda",
                        "celdas": [(r, c)],
                    })
                    continue

                for dr, dc, nombre_dir in DIRECCIONES:
                    fin_r = r + dr * (L - 1)
                    fin_c = c + dc * (L - 1)
                    if not (0 <= fin_r < filas and 0 <= fin_c < cols):
                        continue

                    coincide = True
                    celdas = [(r, c)]
                    for k in range(1, L):
                        nr, nc = r + dr * k, c + dc * k
                        comparaciones += 1
                        if matriz[nr][nc] != p[k]:
                            coincide = False
                            break
                        celdas.append((nr, nc))

                    if coincide:
                        hallazgos[p].append({
                            "palabra": p,
                            "inicio": (r, c),
                            "fin": (fin_r, fin_c),
                            "direccion": nombre_dir,
                            "celdas": celdas,
                        })

    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return {
        "estrategia": "Fuerza Bruta (2D en 8 Direcciones)",
        "hallazgos": hallazgos,
        "comparaciones": comparaciones,
        "tiempo_ms": tiempo_ms,
    }


def _imprimir_separador_inciso(letra: str, titulo: str):
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)
    print(f"  {ui.AMARILLO}{ui.NEGRITA}INCISO {letra} — {titulo}{ui.RESET}")
    print(f"  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)


def imprimir_matriz_coloreada(matriz, hallazgos):
    """Imprime la matriz 20x20 resaltando cada palabra encontrada en su propio color."""
    mapa_colores = {}
    for palabra, lista in hallazgos.items():
        color = COLORES_PALABRAS.get(palabra, ui.VERDE)
        for h in lista:
            for celda in h["celdas"]:
                mapa_colores[celda] = color

    filas = len(matriz)
    cols = len(matriz[0])

    # Encabezado de columnas (0..19)
    enc = "       " + "".join(f"{c:>3}" for c in range(cols))
    print(f"  {ui.CYAN}{enc}{ui.RESET}")
    print(f"  {ui.GRIS}     +-{'---' * cols}+{ui.RESET}")

    for r in range(filas):
        linea = f"  {ui.CYAN}{r:>3}{ui.RESET}  {ui.GRIS}|{ui.RESET} "
        for c in range(cols):
            ch = matriz[r][c]
            if (r, c) in mapa_colores:
                color = mapa_colores[(r, c)]
                linea += f"{color}{ui.NEGRITA}[{ch}]{ui.RESET}"
            else:
                linea += f"{ui.GRIS} {ch} {ui.RESET}"
        linea += f"{ui.GRIS}|{ui.RESET}"
        print(linea)

    print(f"  {ui.GRIS}     +-{'---' * cols}+{ui.RESET}")

    # Leyenda de colores
    leyenda = []
    for p in hallazgos:
        color = COLORES_PALABRAS.get(p, ui.VERDE)
        leyenda.append(f"{color}{ui.NEGRITA}[{p}]{ui.RESET}")
    print(f"  Leyenda: {'   '.join(leyenda)}")


def ejecutar_resolucion_completa():
    """Ejecuta los incisos A y B del Punto 3 bien diferenciados."""
    res_trie = buscar_con_trie(MATRIZ_EXAMEN, PALABRAS_OCULTAS)
    res_fb = buscar_fuerza_bruta(MATRIZ_EXAMEN, PALABRAS_OCULTAS)

    ui.imprimir_banner(
        "PUNTO 3 — BÚSQUEDA DE PALABRAS EN MATRIZ DE CARACTERES (INCISOS A y B)",
        f"Matriz {len(MATRIZ_EXAMEN)}x{len(MATRIZ_EXAMEN[0])} | 8 direcciones | Palabras: {', '.join(PALABRAS_OCULTAS)}",
        ui.CYAN,
    )

    # =========================================================================
    # INCISO A: ¿Qué estrategia elegiste?
    # =========================================================================
    _imprimir_separador_inciso("A", "¿Qué estrategia elegiste? (Justificación teórica y comparativa)")
    print(f"  {ui.VERDE}{ui.NEGRITA}Estrategia elegida:{ui.RESET} {ui.BLANCO}{ui.NEGRITA}Árbol de Prefijos (Trie) + Recorrido en 8 direcciones con poda temprana{ui.RESET}")
    print(f"  {ui.CYAN}Paradigma (Unidades 3 y 6):{ui.RESET} Transforma y Conquista (Cambio de Representación)\n")
    print("  ¿Por qué se eligió esta estrategia frente a Fuerza Bruta pura?")
    print("    1. En Fuerza Bruta (Unidad 3), por cada una de las W palabras se vuelve a")
    print("       recorrer toda la matriz R×C y se prueban las 8 direcciones: O(W·R·C·L).")
    print("    2. Al transformar el conjunto de palabras en un Árbol Trie (preprocesamiento")
    print("       O(ΣL)), recorremos la matriz UNA SOLA VEZ buscando todas las palabras en")
    print("       simultáneo: O(R·C·L_máx), escalando incluso con miles de palabras.")
    print("    3. Poda inmediata en O(1): si la letra de la celda (r, c) no existe como")
    print("       inicio de ninguna palabra en la raíz del Trie, se descartan las 8")
    print("       direcciones sin hacer ninguna comparación adicional.")
    print(f"       -> En esta matriz 20x20 (400 celdas), {ui.VERDE}{ui.NEGRITA}{res_trie['celdas_descartadas_raiz']} celdas{ui.RESET} se podaron en el primer paso.\n")

    ahorro = (1.0 - res_trie["comparaciones"] / res_fb["comparaciones"]) * 100.0
    print(f"  {ui.CYAN}Comparativa empírica real sobre esta matriz 20x20 ({len(PALABRAS_OCULTAS)} palabras):{ui.RESET}")
    print(f"  {ui.GRIS}+-------------------------------------------+---------------+------------+{ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}Estrategia                               {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Comparaciones{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Tiempo(ms){ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+-------------------------------------------+---------------+------------+{ui.RESET}")
    print(
        f"  {ui.GRIS}|{ui.RESET} {ui.VERDE}Trie + 8 direcciones (Elegida)           {ui.RESET} {ui.GRIS}|{ui.RESET} "
        f"{ui.VERDE}{ui.NEGRITA}{res_trie['comparaciones']:>13}{ui.RESET} {ui.GRIS}|{ui.RESET} {res_trie['tiempo_ms']:>10.4f} {ui.GRIS}|{ui.RESET}"
    )
    print(
        f"  {ui.GRIS}|{ui.RESET} Fuerza Bruta 2D (Baseline Unidad 3)       {ui.GRIS}|{ui.RESET} "
        f"{ui.AMARILLO}{res_fb['comparaciones']:>13}{ui.RESET} {ui.GRIS}|{ui.RESET} {res_fb['tiempo_ms']:>10.4f} {ui.GRIS}|{ui.RESET}"
    )
    print(f"  {ui.GRIS}+-------------------------------------------+---------------+------------+{ui.RESET}")
    print(f"  {ui.VERDE}* Reducción de comparaciones de caracteres con Trie: {ahorro:.1f}% menos trabajo.{ui.RESET}")

    # Pausa y limpieza antes de mostrar Inciso B (tabla de palabras)
    ui.pausa_seccion("Palabras ocultas encontradas (Inciso B - Coordenadas)")

    # =========================================================================
    # INCISO B: Palabras ocultas encontradas y mapa visual 20x20
    # =========================================================================
    ui.imprimir_banner("PUNTO 3 — INCISO B: PALABRAS OCULTAS ENCONTRADAS", None, ui.CYAN)
    _imprimir_separador_inciso("B", "Ubicación de las palabras ocultas (ARBOL, HEAPS, SORTS, NODOS, GRAFO)")
    print(f"  {ui.GRIS}(Se informan coordenadas base 0: [0..19] y base 1: [1..20] para facilitar lectura en papel){ui.RESET}\n")

    print(f"  {ui.GRIS}+---------+----------------+----------------+-----------------+-----------------+{ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}Palabra{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Inicio (0-idx){ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Fin (0-idx)   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Inicio->Fin (1){ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Dirección      {ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+---------+----------------+----------------+-----------------+-----------------+{ui.RESET}")
    for p in PALABRAS_OCULTAS:
        color = COLORES_PALABRAS.get(p, ui.VERDE)
        lista = res_trie["hallazgos"].get(p, [])
        if not lista:
            print(f"  {ui.GRIS}|{ui.RESET} {color}{p:<7}{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.ROJO}NO ENCONTRADA {ui.RESET} {ui.GRIS}|{ui.RESET} {'-':<14} {ui.GRIS}|{ui.RESET} {'-':<15} {ui.GRIS}|{ui.RESET} {'-':<15} {ui.GRIS}|{ui.RESET}")
        else:
            for h in lista:
                r0, c0 = h["inicio"]
                r1, c1 = h["fin"]
                ini0 = f"({r0:>2}, {c0:>2})"
                fin0 = f"({r1:>2}, {c1:>2})"
                b1 = f"({r0+1},{c0+1})->({r1+1},{c1+1})"
                print(
                    f"  {ui.GRIS}|{ui.RESET} {color}{ui.NEGRITA}{p:<7}{ui.RESET} {ui.GRIS}|{ui.RESET} "
                    f"{ini0:<14} {ui.GRIS}|{ui.RESET} {fin0:<14} {ui.GRIS}|{ui.RESET} "
                    f"{b1:<15} {ui.GRIS}|{ui.RESET} {ui.BLANCO}{h['direccion']:<15}{ui.RESET} {ui.GRIS}|{ui.RESET}"
                )
    print(f"  {ui.GRIS}+---------+----------------+----------------+-----------------+-----------------+{ui.RESET}\n")

    print(f"  {ui.CYAN}Detalle de celdas recorridas por palabra (fila, columna base 0):{ui.RESET}\n")
    for p in PALABRAS_OCULTAS:
        color = COLORES_PALABRAS.get(p, ui.VERDE)
        for h in res_trie["hallazgos"].get(p, []):
            coords = " -> ".join(f"({r},{c})[{MATRIZ_EXAMEN[r][c]}]" for r, c in h["celdas"])
            print(f"    {color}{ui.NEGRITA}{p:<6}{ui.RESET}: {coords}")

    # Pausa y limpieza antes de mostrar la matriz 20x20 coloreada sola en pantalla
    ui.pausa_seccion("Matriz 20x20 con las 5 palabras resaltadas en color")

    ui.imprimir_banner("PUNTO 3 — VISUALIZACIÓN DE LA MATRIZ 20x20 COLOREADA", None, ui.CYAN)
    imprimir_matriz_coloreada(MATRIZ_EXAMEN, res_trie["hallazgos"])


def _buscar_palabra_personalizada():
    print(f"\n  {ui.CYAN}Puede probar cualquier palabra (incluso al revés o en diagonal, ej. 'LOBRA', 'SPAEH', 'WXO'):{ui.RESET}")
    palabra = input(f"  {ui.AMARILLO}Ingrese la palabra a buscar en la matriz 20x20: {ui.RESET}").strip().upper()
    if not palabra or not palabra.isalpha():
        print(f"  {ui.ROJO}[!] Ingrese una palabra válida (solo letras A-Z).{ui.RESET}")
        return

    res = buscar_con_trie(MATRIZ_EXAMEN, [palabra])
    lista = res["hallazgos"].get(palabra, [])
    if not lista:
        print(f"\n  {ui.ROJO}La palabra \"{palabra}\" NO aparece en la matriz en ninguna de las 8 direcciones.{ui.RESET}")
        return

    print(f"\n  {ui.VERDE}{ui.NEGRITA}¡Se encontraron {len(lista)} coincidencia(s) para \"{palabra}\"!{ui.RESET}")
    for idx, h in enumerate(lista, 1):
        r0, c0 = h["inicio"]
        r1, c1 = h["fin"]
        print(
            f"    {idx}. Inicio ({r0},{c0}) -> Fin ({r1},{c1}) [base 1: ({r0+1},{c0+1})->({r1+1},{c1+1})] | "
            f"Dirección: {ui.AMARILLO}{h['direccion']}{ui.RESET}"
        )
    print()
    imprimir_matriz_coloreada(MATRIZ_EXAMEN, {palabra: lista})


def _ver_arbol_trie():
    ui.imprimir_banner("ESTRUCTURA DEL ÁRBOL TRIE CONSTRUIDO (PALABRAS OCULTAS)", None, ui.MAGENTA)
    trie = Trie()
    for p in PALABRAS_OCULTAS:
        trie.insertar(p)
    print(f"  {ui.GRIS}Cada rama representa un prefijo válido. Si una celda de la matriz no coincide")
    print(f"  con ningún hijo del nodo actual, la búsqueda corta inmediatamente.{ui.RESET}\n")
    trie.imprimir()


def _comparar_trie_vs_fuerza_bruta():
    ui.imprimir_banner("COMPARATIVA DETALLADA: ÁRBOL TRIE VS. FUERZA BRUTA (2D)", None, ui.MAGENTA)
    res_trie = buscar_con_trie(MATRIZ_EXAMEN, PALABRAS_OCULTAS)
    res_fb = buscar_fuerza_bruta(MATRIZ_EXAMEN, PALABRAS_OCULTAS)

    # Verificar que ambos encontraron exactamente lo mismo
    coinciden = True
    for p in PALABRAS_OCULTAS:
        c1 = [(h["inicio"], h["fin"], h["direccion"]) for h in res_trie["hallazgos"][p]]
        c2 = [(h["inicio"], h["fin"], h["direccion"]) for h in res_fb["hallazgos"][p]]
        if sorted(c1) != sorted(c2):
            coinciden = False

    print(f"  Validación de equivalencia : {ui.VERDE + '100% IDÉNTICOS' if coinciden else ui.ROJO + 'DIFIEREN'}{ui.RESET}")
    print(f"  Tamaño de la matriz        : 20 x 20 = 400 celdas (8 direcciones por celda)")
    print(f"  Palabras buscadas (W)      : {len(PALABRAS_OCULTAS)} ({', '.join(PALABRAS_OCULTAS)})\n")
    print(f"  {ui.VERDE}1) Estrategia Trie (Transforma y Conquista):{ui.RESET}")
    print(f"     - Recorridos de matriz      : 1 sola pasada")
    print(f"     - Celdas podadas en raíz    : {res_trie['celdas_descartadas_raiz']} / 400")
    print(f"     - Comparaciones totales     : {ui.VERDE}{ui.NEGRITA}{res_trie['comparaciones']}{ui.RESET}")
    print(f"     - Tiempo medido             : {res_trie['tiempo_ms']:.4f} ms")
    print(f"     - Complejidad teórica       : O(ΣL + R · C · L_máx)\n")
    print(f"  {ui.AMARILLO}2) Estrategia Fuerza Bruta (Unidad 3):{ui.RESET}")
    print(f"     - Recorridos de matriz      : {len(PALABRAS_OCULTAS)} pasadas (una por cada palabra)")
    print(f"     - Comparaciones totales     : {ui.AMARILLO}{ui.NEGRITA}{res_fb['comparaciones']}{ui.RESET}")
    print(f"     - Tiempo medido             : {res_fb['tiempo_ms']:.4f} ms")
    print(f"     - Complejidad teórica       : O(W · R · C · L)")


def mostrar_submenu_punto3():
    while True:
        ui.limpiar_pantalla()
        ui.imprimir_banner("PUNTO 3: BÚSQUEDA DE PALABRAS EN MATRIZ DE CARACTERES", None, ui.CYAN)
        print(f"  Matriz            : {ui.BLANCO}20 x 20 caracteres (400 celdas){ui.RESET}")
        print(f"  Palabras ocultas  : {ui.AMARILLO}{ui.NEGRITA}{', '.join(PALABRAS_OCULTAS)}{ui.RESET}")
        print(f"  Direcciones       : {ui.CYAN}8 (Arriba, Abajo, Izq, Der y las 4 Diagonales){ui.RESET}")
        print(f"  Estrategia elegida: {ui.VERDE}Árbol Trie (Transforma y Conquista) + 8 direcciones{ui.RESET}")
        print(f"{ui.GRIS}" + "-" * 78 + ui.RESET)
        print(f"    {ui.VERDE}a){ui.RESET} Ejecutar resolución COMPLETA del Punto 3 (Incisos A y B + Matriz coloreada)")
        print(f"    {ui.VERDE}b){ui.RESET} Buscar OTRA palabra personalizada en las 8 direcciones (ej. inversas/diagonales)")
        print(f"    {ui.MAGENTA}c){ui.RESET} Ver la estructura gráfica del Árbol Trie construido")
        print(f"    {ui.CYAN}d){ui.RESET} Ver comparativa detallada: Árbol Trie vs. Fuerza Bruta")
        print(f"    {ui.ROJO}v){ui.RESET} Volver al menú principal")
        print(f"{ui.CYAN}" + "=" * 78 + ui.RESET)

        op = input(f"  {ui.AMARILLO}Seleccione una opción [a-d / v para volver]: {ui.RESET}").strip().lower()
        if op == "a":
            ui.limpiar_pantalla()
            ejecutar_resolucion_completa()
        elif op == "b":
            ui.limpiar_pantalla()
            _buscar_palabra_personalizada()
        elif op == "c":
            ui.limpiar_pantalla()
            _ver_arbol_trie()
        elif op == "d":
            ui.limpiar_pantalla()
            _comparar_trie_vs_fuerza_bruta()
        elif op in ("v", "0", "volver", "s"):
            return
        else:
            print(f"\n  {ui.ROJO}[!] Opción '{op}' no válida. Intente nuevamente.{ui.RESET}")

        input(f"\n  {ui.GRIS}Presione ENTER para volver al menú del Punto 3...{ui.RESET}")

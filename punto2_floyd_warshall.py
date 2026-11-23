#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Asignatura : Análisis y Diseño de Algoritmos
Examen 2 - Práctica | Punto 2: Caminos Mínimos (Algoritmo de Floyd-Warshall)
================================================================================

Implementa Programación Dinámica (Unidad 7 - Diapositivas 25 a 30):
- Matriz de distancias mínimas entre todos los pares de vértices D[i][j].
- Matriz de predecesores / reconstrucción de caminos P[i][j].
- Detección de ciclos negativos verificando la diagonal principal D[i][i] < 0.
Complejidad Temporal: O(V^3) | Complejidad Espacial: O(V^2).
"""

import ui_consola as ui

INF = 10**9

# Los 13 vértices del grafo del práctico (orden alfabético)
VERTICES = ["A", "B", "C", "D", "E", "H", "I", "J", "K", "L", "M", "O", "P"]

# 15 aristas bidireccionales (flecha en ambos extremos, pesos positivos)
ARISTAS_BIDIRECCIONALES = [
    ("A", "B", 5),
    ("A", "J", 5),
    ("B", "C", 3),
    ("B", "E", 4),
    ("C", "L", 7),
    ("D", "E", 3),
    ("D", "H", 3),
    ("E", "L", 5),
    ("E", "P", 7),
    ("H", "K", 2),
    ("H", "M", 3),
    ("I", "J", 2),
    ("I", "O", 6),
    ("J", "P", 6),
    ("K", "O", 3),
]

# 5 arcos unidireccionales (flecha en un solo sentido, todos con peso negativo)
ARCOS_UNIDIRECCIONALES = [
    ("D", "B", -2),
    ("I", "C", -2),
    ("K", "E", -1),
    ("L", "K", -2),
    ("P", "O", -3),
]


def construir_matrices_iniciales(vertices=None, bidir=None, unidir=None):
    """Construye la matriz de adyacencia inicial D^0 y la matriz de predecesores P^0."""
    if vertices is None:
        vertices = VERTICES
    if bidir is None:
        bidir = ARISTAS_BIDIRECCIONALES
    if unidir is None:
        unidir = ARCOS_UNIDIRECCIONALES

    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    pred = [[i if i == j else None for j in range(n)] for i in range(n)]
    pesos_directos = {}

    for u, v, w in bidir:
        for a, b in ((u, v), (v, u)):
            ia, ib = idx[a], idx[b]
            dist[ia][ib] = w
            pred[ia][ib] = ia
            pesos_directos[(a, b)] = w

    for u, v, w in unidir:
        iu, iv = idx[u], idx[v]
        dist[iu][iv] = w
        pred[iu][iv] = iu
        pesos_directos[(u, v)] = w

    return dist, pred, idx, pesos_directos


def ejecutar_floyd_warshall(vertices=None, bidir=None, unidir=None, registrar_pasos=False):
    """
    Aplica el algoritmo de Floyd-Warshall sobre el grafo dirigido ponderado.
    Actualiza:
      D[i][j] = min(D[i][j], D[i][k] + D[k][j])
      P[i][j] = P[k][j]  si el camino pasando por k mejora el actual.
    """
    if vertices is None:
        vertices = VERTICES
    dist_inicial, pred_inicial, idx, pesos_directos = construir_matrices_iniciales(vertices, bidir, unidir)
    n = len(vertices)

    dist = [fila[:] for fila in dist_inicial]
    pred = [fila[:] for fila in pred_inicial]
    historial_k = []

    for k in range(n):
        mejoras = []
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[k][j] == INF:
                    continue
                nuevo_costo = dist[i][k] + dist[k][j]
                if nuevo_costo < dist[i][j]:
                    viejo = dist[i][j]
                    dist[i][j] = nuevo_costo
                    pred[i][j] = pred[k][j]
                    if registrar_pasos:
                        mejoras.append((vertices[i], vertices[j], viejo, nuevo_costo))
        if registrar_pasos:
            historial_k.append({
                "k_idx": k,
                "k_vertice": vertices[k],
                "cantidad_mejoras": len(mejoras),
                "mejoras": mejoras,
            })

    # Inciso F: Verificación de ciclos negativos en la diagonal principal
    ciclos_negativos = [
        (vertices[i], dist[i][i]) for i in range(n) if dist[i][i] < 0
    ]

    return {
        "vertices": vertices,
        "idx": idx,
        "dist_inicial": dist_inicial,
        "dist": dist,
        "pred": pred,
        "pesos_directos": pesos_directos,
        "ciclos_negativos": ciclos_negativos,
        "historial_k": historial_k,
    }


def reconstruir_camino(res: dict, origen: str, destino: str):
    """
    Reconstruye el camino mínimo desde 'origen' hasta 'destino' usando
    la matriz de predecesores P (Unidad 7 - Diapositiva 29).
    Retorna (distancia, lista_nodos, lista_traza_P, lista_arcos_con_peso).
    """
    idx = res["idx"]
    vertices = res["vertices"]
    dist = res["dist"]
    pred = res["pred"]
    pesos = res["pesos_directos"]

    i = idx[origen]
    j = idx[destino]

    if dist[i][j] >= INF:
        return None, [], [], []

    # Verificar si hay ciclo negativo afectando el recorrido
    if res["ciclos_negativos"]:
        # Protección contra bucle infinito al reconstruir si hubo ciclo negativo
        visitados = set()
    else:
        visitados = None

    traza_p = []
    camino_inv = [destino]
    actual = j

    while actual != i:
        anterior = pred[i][actual]
        if anterior is None:
            return None, [], [], []
        traza_p.append((origen, vertices[actual], vertices[anterior]))
        if visitados is not None:
            if actual in visitados:
                return dist[i][j], ["(Camino afectado por ciclo negativo)"], traza_p, []
            visitados.add(actual)
        camino_inv.append(vertices[anterior])
        actual = anterior

    camino = list(reversed(camino_inv))
    arcos = []
    for k in range(len(camino) - 1):
        u, v = camino[k], camino[k + 1]
        arcos.append((u, v, pesos.get((u, v), 0)))

    return dist[i][j], camino, traza_p, arcos


def _imprimir_separador_inciso(letra: str, titulo: str):
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)
    print(f"  {ui.AMARILLO}{ui.NEGRITA}INCISO {letra} — {titulo}{ui.RESET}")
    print(f"  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)


def imprimir_camino_detallado(res: dict, origen: str, destino: str):
    """Muestra distancia, camino paso a paso, traza en matriz P y verificación de suma."""
    distancia, camino, traza_p, arcos = reconstruir_camino(res, origen, destino)
    if distancia is None:
        print(f"    {ui.ROJO}No existe camino dirigido desde {origen} hasta {destino} (distancia = ∞).{ui.RESET}")
        return

    ruta_flechas = f" {ui.GRIS}->{ui.RESET} ".join(f"{ui.VERDE}{ui.NEGRITA}{v}{ui.RESET}" for v in camino)
    print(f"    Distancia mínima  : {ui.VERDE}{ui.NEGRITA}{distancia}{ui.RESET}")
    print(f"    Camino mínimo     : {ruta_flechas}")

    if arcos:
        tramos = []
        suma_partes = []
        for u, v, w in arcos:
            color_w = ui.MAGENTA if w < 0 else ui.CYAN
            tramos.append(f"{u} {color_w}--({w})-->{ui.RESET} {v}")
            suma_partes.append(f"({w})" if w < 0 else str(w))
        print(f"    Detalle por arcos : {'  |  '.join(tramos)}")
        print(f"    Verificación suma : {' + '.join(suma_partes)} = {ui.VERDE}{ui.NEGRITA}{sum(w for _, _, w in arcos)}{ui.RESET}")

    if traza_p:
        pasos_p = " , ".join(f"P[{o}][{d}]={ant}" for o, d, ant in traza_p)
        print(f"    {ui.GRIS}Reconstrucción en P (atrás -> adelante): {pasos_p}{ui.RESET}")


def imprimir_matriz_distancias(vertices, matriz, titulo: str):
    """Imprime una matriz V x V de distancias bien alineada con colores."""
    n = len(vertices)
    print(f"\n  {ui.CYAN}{ui.NEGRITA}{titulo}{ui.RESET}")
    encabezado = "      | " + "".join(f"{v:>4}" for v in vertices)
    print(f"  {ui.CYAN}{encabezado}{ui.RESET}")
    print(f"  {ui.GRIS}  ----+-" + "----" * n + ui.RESET)

    for i in range(n):
        linea = f"  {ui.CYAN}  {vertices[i]:>2}  {ui.GRIS}|{ui.RESET} "
        for j in range(n):
            val = matriz[i][j]
            if val >= INF:
                linea += f"{ui.GRIS}{'∞':>4}{ui.RESET}"
            elif i == j:
                if val < 0:
                    linea += f"{ui.ROJO}{ui.NEGRITA}{val:>4}{ui.RESET}"
                else:
                    linea += f"{ui.GRIS}{val:>4}{ui.RESET}"
            elif val < 0:
                linea += f"{ui.MAGENTA}{ui.NEGRITA}{val:>4}{ui.RESET}"
            else:
                linea += f"{ui.BLANCO}{val:>4}{ui.RESET}"
        print(linea)


def imprimir_matriz_predecesores(vertices, pred, titulo: str):
    """Imprime la matriz de reconstrucción de caminos P[i][j] (predecesores)."""
    n = len(vertices)
    print(f"\n  {ui.CYAN}{ui.NEGRITA}{titulo}{ui.RESET}")
    print(f"  {ui.GRIS}  (P[i][j] indica el vértice anterior a 'j' en el camino mínimo desde 'i' hasta 'j'){ui.RESET}")
    encabezado = "      | " + "".join(f"{v:>4}" for v in vertices)
    print(f"  {ui.CYAN}{encabezado}{ui.RESET}")
    print(f"  {ui.GRIS}  ----+-" + "----" * n + ui.RESET)

    for i in range(n):
        linea = f"  {ui.CYAN}  {vertices[i]:>2}  {ui.GRIS}|{ui.RESET} "
        for j in range(n):
            p = pred[i][j]
            if p is None:
                linea += f"{ui.GRIS}{'-':>4}{ui.RESET}"
            elif i == j:
                linea += f"{ui.GRIS}{vertices[p]:>4}{ui.RESET}"
            else:
                linea += f"{ui.VERDE}{vertices[p]:>4}{ui.RESET}"
        print(linea)


def ejecutar_resolucion_completa():
    """Ejecuta todos los incisos A hasta F del Punto 2 bien diferenciados."""
    res = ejecutar_floyd_warshall(registrar_pasos=False)

    ui.imprimir_banner(
        "PUNTO 2 — RESOLUCIÓN COMPLETA (ALGORITMO DE FLOYD-WARSHALL | INCISOS A - F)",
        f"Grafo dirigido ponderado: {len(VERTICES)} vértices | 15 aristas bidireccionales + 5 arcos negativos (35 arcos)",
        ui.CYAN,
    )

    print(f"  {ui.CYAN}Fórmula de Programación Dinámica aplicada (Unidad 7 - Diap. 26-29):{ui.RESET}")
    print("    Para cada vértice intermedio k ∈ V, origen i ∈ V y destino j ∈ V:")
    print(f"      Si D[i][k] + D[k][j] < D[i][j]:")
    print(f"        D[i][j] = D[i][k] + D[k][j]   {ui.GRIS}# Actualiza distancia mínima{ui.RESET}")
    print(f"        P[i][j] = P[k][j]             {ui.GRIS}# Actualiza predecesor para reconstruir camino{ui.RESET}")
    print(f"    {ui.GRIS}Complejidad: Tiempo O(V^3) = O({len(VERTICES)}^3) = {len(VERTICES)**3} iteraciones | Espacio O(V^2){ui.RESET}")

    # INCISO A: M -> J
    _imprimir_separador_inciso("A", "Distancia mínima y camino mínimo de M a J")
    imprimir_camino_detallado(res, "M", "J")

    # INCISO B: O -> P
    _imprimir_separador_inciso("B", "Distancia mínima y camino mínimo de O a P")
    imprimir_camino_detallado(res, "O", "P")

    # INCISO C: C -> K
    _imprimir_separador_inciso("C", "Distancia mínima y camino mínimo de C a K")
    imprimir_camino_detallado(res, "C", "K")

    # Pausa y limpieza antes de Matriz D
    ui.pausa_seccion("Matriz Final de Distancias D (Inciso D)")

    # INCISO D: Matriz final de distancias
    ui.imprimir_banner("PUNTO 2 — INCISO D: MATRIZ FINAL DE DISTANCIAS MÍNIMAS D", None, ui.CYAN)
    _imprimir_separador_inciso("D", "Matriz final de distancias mínimas D (todos los pares)")
    imprimir_matriz_distancias(
        res["vertices"],
        res["dist"],
        "Matriz Final de Distancias D (filas = origen, columnas = destino):",
    )

    # Pausa y limpieza antes de Matriz P y Ciclos Negativos F
    ui.pausa_seccion("Matriz de Predecesores P (Inciso E) y Ciclos Negativos (Inciso F)")

    # INCISO E: Matriz de reconstrucción de caminos
    ui.imprimir_banner("PUNTO 2 — INCISOS E y F: RECONSTRUCCIÓN DE CAMINOS Y CICLOS NEGATIVOS", None, ui.CYAN)
    _imprimir_separador_inciso("E", "Matriz de reconstrucción de caminos / Predecesores P")
    imprimir_matriz_predecesores(
        res["vertices"],
        res["pred"],
        "Matriz Final de Predecesores P (filas = origen, columnas = destino):",
    )

    # INCISO F: Verificación de ciclos negativos
    _imprimir_separador_inciso("F", "Verificación de existencia de ciclos negativos")
    print("    Criterio de Floyd-Warshall (Unidad 7 - Diap. 20 y 25):")
    print("    Existe un ciclo negativo si y solo si algún elemento de la diagonal")
    print("    principal cumple D[i][i] < 0 tras ejecutar todas las iteraciones k.\n")

    diag_str = "  ".join(f"D[{v}][{v}]={res['dist'][res['idx'][v]][res['idx'][v]]}" for v in VERTICES)
    print(f"    Diagonal principal verificada:")
    print(f"      {ui.CYAN}{diag_str}{ui.RESET}\n")

    if not res["ciclos_negativos"]:
        print(f"    {ui.VERDE}{ui.NEGRITA}[RESULTADO] NO EXISTE NINGÚN CICLO NEGATIVO en el grafo.{ui.RESET}")
        print(f"    {ui.GRIS}Todos los valores de la diagonal principal son iguales a 0.{ui.RESET}")
        print(f"    {ui.GRIS}Nota: Aunque existen 5 arcos con peso negativo (D->B:-2, I->C:-2, K->E:-1,{ui.RESET}")
        print(f"    {ui.GRIS}L->K:-2 y P->O:-3), ninguno pertenece a un ciclo cerrado cuya suma sea < 0,{ui.RESET}")
        print(f"    {ui.GRIS}por lo que todas las distancias calculadas por Floyd-Warshall son válidas.{ui.RESET}")
    else:
        print(f"    {ui.ROJO}{ui.NEGRITA}[ALERTA] SE DETECTARON CICLOS NEGATIVOS en:{ui.RESET}")
        for v, val in res["ciclos_negativos"]:
            print(f"      - Vértice {v}: D[{v}][{v}] = {val} < 0")


def _consultar_par_personalizado():
    res = ejecutar_floyd_warshall(registrar_pasos=False)
    print(f"\n  {ui.CYAN}Vértices disponibles:{ui.RESET} {', '.join(VERTICES)}")
    origen = input(f"  {ui.AMARILLO}Ingrese vértice de ORIGEN : {ui.RESET}").strip().upper()
    destino = input(f"  {ui.AMARILLO}Ingrese vértice de DESTINO: {ui.RESET}").strip().upper()

    if origen not in res["idx"] or destino not in res["idx"]:
        print(f"\n  {ui.ROJO}[!] Vértice inválido. Debe elegir entre: {', '.join(VERTICES)}{ui.RESET}")
        return

    print(f"\n  {ui.CYAN}{ui.NEGRITA}Resultado para {origen} -> {destino}:{ui.RESET}")
    imprimir_camino_detallado(res, origen, destino)


def _ver_grafo_y_matriz_inicial():
    res = ejecutar_floyd_warshall(registrar_pasos=False)
    ui.imprimir_banner("DETALLE DEL GRAFO DEL PRÁCTICO Y MATRIZ INICIAL D⁰", None, ui.CYAN)
    print(f"  {ui.BLANCO}{ui.NEGRITA}Vértices ({len(VERTICES)}):{ui.RESET} {', '.join(VERTICES)}\n")

    print(f"  {ui.VERDE}{ui.NEGRITA}Aristas Bidireccionales ({len(ARISTAS_BIDIRECCIONALES)} pares = {len(ARISTAS_BIDIRECCIONALES)*2} arcos positivos):{ui.RESET}")
    for i in range(0, len(ARISTAS_BIDIRECCIONALES), 5):
        fila = ARISTAS_BIDIRECCIONALES[i:i + 5]
        print("    " + "  |  ".join(f"{u} <-> {v} ({w:>2})" for u, v, w in fila))

    print(f"\n  {ui.MAGENTA}{ui.NEGRITA}Arcos Unidireccionales ({len(ARCOS_UNIDIRECCIONALES)} arcos de peso negativo):{ui.RESET}")
    print("    " + "  |  ".join(f"{u} -> {v} ({w})" for u, v, w in ARCOS_UNIDIRECCIONALES))

    imprimir_matriz_distancias(
        res["vertices"],
        res["dist_inicial"],
        "Matriz de Adyacencia Inicial D⁰ (antes de ejecutar iteraciones k):",
    )


def _ver_iteraciones_k():
    res = ejecutar_floyd_warshall(registrar_pasos=True)
    ui.imprimir_banner("EVOLUCIÓN DE FLOYD-WARSHALL POR CADA VÉRTICE INTERMEDIO k", None, ui.MAGENTA)
    print(f"  {ui.GRIS}Muestra cuántas distancias D[i][j] mejoraron al permitir pasar por cada nodo intermedio k.{ui.RESET}\n")

    for paso in res["historial_k"]:
        k_v = paso["k_vertice"]
        cant = paso["cantidad_mejoras"]
        color = ui.VERDE if cant > 0 else ui.GRIS
        print(f"  {ui.CYAN}{ui.NEGRITA}Iteración k={paso['k_idx']:>2} (nodo intermedio {k_v}):{ui.RESET} {color}{cant} distancia(s) mejorada(s){ui.RESET}")
        if cant > 0:
            muestra = paso["mejoras"][:6]
            txt = ", ".join(
                f"{u}->{v}: {'∞' if viejo >= INF else viejo}→{nuevo}"
                for u, v, viejo, nuevo in muestra
            )
            extra = f" ... (+{cant - 6} más)" if cant > 6 else ""
            print(f"      {ui.GRIS}Ejemplos: {txt}{extra}{ui.RESET}")


def _demo_ciclo_negativo():
    ui.imprimir_banner("SIMULACIÓN EDUCATIVA: DETECCIÓN DE CICLO NEGATIVO (INCISO F)", None, ui.MAGENTA)
    print("  El grafo original del práctico NO tiene ciclos negativos.")
    print("  Para demostrar cómo lo detecta Floyd-Warshall, simulamos temporalmente")
    print(f"  agregar el arco {ui.ROJO}B -> D (peso -1){ui.RESET} junto al arco existente {ui.MAGENTA}D -> B (peso -2){ui.RESET},")
    print("  creando el ciclo cerrado D -> B -> D con suma total = (-2) + (-1) = -3 < 0.\n")

    unidir_mod = list(ARCOS_UNIDIRECCIONALES) + [("B", "D", -1)]
    res_sim = ejecutar_floyd_warshall(VERTICES, ARISTAS_BIDIRECCIONALES, unidir_mod, registrar_pasos=False)

    print(f"  {ui.ROJO}{ui.NEGRITA}Resultado de la verificación diagonal D[i][i] < 0:{ui.RESET}")
    for v, val in res_sim["ciclos_negativos"]:
        print(f"    - Vértice {ui.AMARILLO}{v}{ui.RESET}: D[{v}][{v}] = {ui.ROJO}{val}{ui.RESET} (< 0 -> ¡Ciclo negativo detectado!)")
    print(f"\n  {ui.GRIS}(Nota: Esta simulación no modifica el grafo original del examen.){ui.RESET}")


def mostrar_submenu_punto2():
    while True:
        ui.limpiar_pantalla()
        ui.imprimir_banner("PUNTO 2: CAMINOS MÍNIMOS EN GRAFO PONDERADO (FLOYD-WARSHALL)", None, ui.CYAN)
        print(f"  Vértices ({len(VERTICES)})     : {', '.join(VERTICES)}")
        print(f"  Conexiones        : {ui.VERDE}15 bidireccionales (+){ui.RESET} y {ui.MAGENTA}5 unidireccionales (-){ui.RESET} [35 arcos dirigidos]")
        print(f"  Consultas examen  : {ui.AMARILLO}A) M -> J   |   B) O -> P   |   C) C -> K{ui.RESET}")
        print(f"  Algoritmo         : {ui.CYAN}Floyd-Warshall — Programación Dinámica O(V^3){ui.RESET}")
        print(f"{ui.GRIS}" + "-" * 78 + ui.RESET)
        print(f"    {ui.VERDE}a){ui.RESET} Ejecutar resolución COMPLETA del Punto 2 (Incisos A - F)")
        print(f"    {ui.VERDE}b){ui.RESET} Consultar distancia y camino mínimo entre CUALQUIER par de vértices")
        print(f"    {ui.VERDE}c){ui.RESET} Ver detalle del grafo cargado y matriz inicial D⁰")
        print(f"    {ui.MAGENTA}d){ui.RESET} Ver evolución paso a paso por iteración k (nodos intermedios A..P)")
        print(f"    {ui.CYAN}e){ui.RESET} Simulación educativa: ¿cómo detecta Floyd-Warshall un ciclo negativo?")
        print(f"    {ui.ROJO}v){ui.RESET} Volver al menú principal")
        print(f"{ui.CYAN}" + "=" * 78 + ui.RESET)

        op = input(f"  {ui.AMARILLO}Seleccione una opción [a-e / v para volver]: {ui.RESET}").strip().lower()
        if op == "a":
            ui.limpiar_pantalla()
            ejecutar_resolucion_completa()
        elif op == "b":
            ui.limpiar_pantalla()
            _consultar_par_personalizado()
        elif op == "c":
            ui.limpiar_pantalla()
            _ver_grafo_y_matriz_inicial()
        elif op == "d":
            ui.limpiar_pantalla()
            _ver_iteraciones_k()
        elif op == "e":
            ui.limpiar_pantalla()
            _demo_ciclo_negativo()
        elif op in ("v", "0", "volver", "s"):
            return
        else:
            print(f"\n  {ui.ROJO}[!] Opción '{op}' no válida. Intente nuevamente.{ui.RESET}")

        input(f"\n  {ui.GRIS}Presione ENTER para volver al menú del Punto 2...{ui.RESET}")

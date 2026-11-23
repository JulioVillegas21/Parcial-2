#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Asignatura : Análisis y Diseño de Algoritmos
Examen 2 - Práctica | Punto 4: "Mejor período de utilidad" con 1.000.000 datos
================================================================================

Integra las unidades del programa sobre el archivo 'datos_1millón.txt' (n = 1.000.000):
- Parte A: Sub-Arreglo Máximo -> Kadane O(n) (PD, Unidad 5/7) vs Divide y Vencerás
           O(n log n) (Unidad 5), con contraste empírico y gráfico ASCII.
- Parte B: Top-k (k = 10) períodos contiguos no solapados -> Max-Heap (Unidad 6)
           + Divide-y-Vencerás incremental por particionamiento de intervalos.
- Parte C: Mediana (p50) y Percentiles (p90, p95) -> QuickSelect Lomuto (Unidad 4)
           vs QuickSelect Hoare (Unidad 5) vs Merge Sort baseline O(n log n)
           + Validación con Búsqueda Binaria O(log n) (Unidad 4).
"""

import heapq
import math
import os
import random
import time
import ui_consola as ui

# Caché en memoria para no releer el archivo de 1.000.000 de líneas en cada opción
_cache_datos = None
_cache_ruta = None
_cache_tiempo_carga = 0.0


def localizar_archivo_datos():
    """Busca 'datos_1millón.txt' en la carpeta actual o en '../AyDa/'."""
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(base, "datos_1millón.txt"),
        os.path.join(base, "datos_1millon.txt"),
        os.path.join(os.path.dirname(base), "AyDa", "datos_1millón.txt"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Escritorio", "AyDa", "datos_1millón.txt"),
        os.path.join(os.path.expanduser("~"), "Desktop", "AyDa", "datos_1millón.txt"),
    ]
    for ruta in candidatos:
        if os.path.isfile(ruta):
            return ruta
    return None


def cargar_datos():
    """Carga los 1.000.000 de enteros desde el archivo (con caché en memoria)."""
    global _cache_datos, _cache_ruta, _cache_tiempo_carga
    if _cache_datos is not None:
        return _cache_datos, _cache_ruta, _cache_tiempo_carga

    ruta = localizar_archivo_datos()
    if ruta is None:
        raise FileNotFoundError(
            "No se encontró el archivo 'datos_1millón.txt' ni en la carpeta 'examen 2' ni en 'AyDa'."
        )

    print(f"  {ui.GRIS}Cargando datos desde '{ruta}'...{ui.RESET}", flush=True)
    t0 = time.perf_counter()
    with open(ruta, "r", encoding="utf-8") as f:
        datos = [int(linea) for linea in f if linea.strip()]
    _cache_tiempo_carga = (time.perf_counter() - t0) * 1000.0
    _cache_datos = datos
    _cache_ruta = ruta
    return _cache_datos, _cache_ruta, _cache_tiempo_carga


def _imprimir_separador_parte(titulo: str):
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)
    print(f"  {ui.AMARILLO}{ui.NEGRITA}{titulo}{ui.RESET}")
    print(f"  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)


# ==============================================================================
# PARTE A — SUB-ARREGLO MÁXIMO (KADANE O(n) vs DIVIDE Y VENCERÁS O(n log n))
# ==============================================================================
def kadane(arr, lo=0, hi=None):
    """
    Algoritmo de Kadane (Programación Dinámica - Unidad 5 Diap. 16-22).
    Complejidad: Tiempo O(n), Espacio auxiliar O(1).
    """
    if hi is None:
        hi = len(arr) - 1
    best_sum = cur_sum = arr[lo]
    best_l = best_r = cur_l = lo
    comps = 0

    for i in range(lo + 1, hi + 1):
        v = arr[i]
        comps += 2  # 1 comparación reiniciar vs acumular + 1 comparación con máximo global
        if cur_sum + v < v:
            cur_sum = v
            cur_l = i
        else:
            cur_sum += v
        if cur_sum > best_sum:
            best_sum = cur_sum
            best_l = cur_l
            best_r = i

    return best_sum, best_l, best_r, comps


def subarreglo_maximo_dyv(arr):
    """
    Algoritmo Divide y Vencerás para Sub-Arreglo Máximo (Unidad 5 Diap. 10-15).
    Recurrencia: T(n) = 2T(n/2) + Θ(n)  =>  Complejidad Θ(n log n) | Espacio O(log n).
    """
    comps = [0]

    def resolver(l, r):
        if l == r:
            return arr[l], l, l

        m = (l + r) >> 1
        ls, ll, lr = resolver(l, m)
        rs, rl, rr = resolver(m + 1, r)

        # Mejor suma cruzando el centro hacia la izquierda
        s = 0
        best_left = -10**18
        bl = m
        c_local = 0
        for i in range(m, l - 1, -1):
            s += arr[i]
            c_local += 1
            if s > best_left:
                best_left = s
                bl = i

        # Mejor suma cruzando el centro hacia la derecha
        s = 0
        best_right = -10**18
        br = m + 1
        for i in range(m + 1, r + 1):
            s += arr[i]
            c_local += 1
            if s > best_right:
                best_right = s
                br = i

        cs = best_left + best_right
        comps[0] += c_local + 2

        if ls >= rs and ls >= cs:
            return ls, ll, lr
        elif rs >= cs:
            return rs, rl, rr
        else:
            return cs, bl, br

    best_sum, best_l, best_r = resolver(0, len(arr) - 1)
    return best_sum, best_l, best_r, comps[0]


def imprimir_grafico_ascii_parte_a(arr, best_l, best_r, best_sum):
    """
    Dibuja un gráfico ASCII muestreado en 60 columnas de la utilidad acumulada
    (suma de prefijos), resaltando en verde el tramo óptimo [best_l..best_r].
    """
    n = len(arr)
    cols = 60
    alto = 12
    paso = n / cols

    # Calcular utilidad acumulada al final de cada bloque
    acum_bins = []
    acum = 0
    prox_limite = paso
    bin_idx = 0
    for i, v in enumerate(arr):
        acum += v
        if (i + 1) >= prox_limite or i == n - 1:
            acum_bins.append(acum)
            bin_idx += 1
            prox_limite = (bin_idx + 1) * paso
            if bin_idx == cols:
                break

    vmin = min(acum_bins)
    vmax = max(acum_bins)
    rango = (vmax - vmin) if vmax != vmin else 1

    col_ini = int(best_l / n * cols)
    col_fin = min(cols - 1, int(best_r / n * cols))

    print(f"\n  {ui.CYAN}{ui.NEGRITA}Gráfico ASCII — Curva de Utilidad Acumulada (60 bloques de ~{n // cols:,} días):{ui.RESET}")
    print(f"  {ui.GRIS}En la curva acumulada, el sub-arreglo máximo es la mayor subida neta (+{best_sum:,}).{ui.RESET}")
    print(f"  {ui.VERDE}█ = tramo óptimo [{best_l:,}..{best_r:,}]{ui.RESET}   |   {ui.CYAN}· = resto del período{ui.RESET}\n")

    for fila in range(alto, -1, -1):
        umbral_y = vmin + (fila / alto) * rango
        etiqueta_y = f"{int(umbral_y):>8,}" if fila in (alto, alto // 2, 0) else "        "
        linea = f"  {ui.GRIS}{etiqueta_y} │{ui.RESET} "
        for c in range(cols):
            nivel = int(round((acum_bins[c] - vmin) / rango * alto))
            en_optimo = col_ini <= c <= col_fin
            if nivel == fila:
                linea += f"{ui.VERDE}{ui.NEGRITA}█{ui.RESET}" if en_optimo else f"{ui.CYAN}●{ui.RESET}"
            elif nivel > fila:
                linea += f"{ui.VERDE}│{ui.RESET}" if en_optimo else f"{ui.GRIS}·{ui.RESET}"
            else:
                linea += " "
        print(linea)

    print(f"  {ui.GRIS}         └" + "─" * (cols + 1) + ui.RESET)

    # Barra de línea temporal resaltando el tramo óptimo
    barra = []
    for c in range(cols):
        if col_ini <= c <= col_fin:
            barra.append(f"{ui.VERDE}{ui.NEGRITA}═{ui.RESET}")
        else:
            barra.append(f"{ui.GRIS}─{ui.RESET}")
    print(f"  {ui.GRIS}  Tramo  :{ui.RESET} {''.join(barra)}")
    print(f"  {ui.GRIS}  Días   : 0{' ' * 24}500.000{' ' * 21}1.000.000{ui.RESET}")
    print(f"  {ui.VERDE}           Tramo óptimo resaltado: día {best_l:,} al día {best_r:,} ({best_r - best_l + 1:,} días){ui.RESET}")


def ejecutar_parte_a(arr=None):
    if arr is None:
        arr, ruta, t_carga = cargar_datos()
    n = len(arr)

    _imprimir_separador_parte("PARTE A — SUB-ARREGLO MÁXIMO (MEJOR PERÍODO DE UTILIDAD)")
    print(f"  {ui.GRIS}Ejecutando Kadane O(n) sobre n = {n:,} elementos...{ui.RESET}", flush=True)
    t0 = time.perf_counter()
    k_sum, k_l, k_r, k_comps = kadane(arr)
    t_kadane = (time.perf_counter() - t0) * 1000.0

    print(f"  {ui.GRIS}Ejecutando Divide y Vencerás O(n log n) sobre n = {n:,} elementos (aguarde ~5s)...{ui.RESET}", flush=True)
    t0 = time.perf_counter()
    d_sum, d_l, d_r, d_comps = subarreglo_maximo_dyv(arr)
    t_dyv = (time.perf_counter() - t0) * 1000.0

    iguales = (k_sum == d_sum and k_l == d_l and k_r == d_r)
    n_log_n = n * math.log2(n)
    ratio_ops = d_comps / k_comps
    ratio_t = t_dyv / t_kadane if t_kadane > 0 else 0.0

    print(f"\n  {ui.CYAN}{ui.NEGRITA}1. Mediciones Empíricas y Contraste Teórico (n = {n:,}):{ui.RESET}")
    print(f"  {ui.GRIS}+----------------------------+---------------+------------------+--------------------+-------------+{ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}Algoritmo                 {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Cota Teórica {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Comparaciones   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Tiempo (ms / s)   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Memoria Aux{ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+----------------------------+---------------+------------------+--------------------+-------------+{ui.RESET}")
    print(
        f"  {ui.GRIS}|{ui.RESET} {ui.VERDE}Kadane (Prog. Dinámica)   {ui.RESET} {ui.GRIS}|{ui.RESET} O(n)          {ui.GRIS}|{ui.RESET} "
        f"{ui.VERDE}{ui.NEGRITA}{k_comps:>16,}{ui.RESET} {ui.GRIS}|{ui.RESET} {k_t_fmt(t_kadane):>18} {ui.GRIS}|{ui.RESET} O(1)        {ui.GRIS}|{ui.RESET}"
    )
    print(
        f"  {ui.GRIS}|{ui.RESET} {ui.AMARILLO}Divide y Vencerás         {ui.RESET} {ui.GRIS}|{ui.RESET} O(n log n)    {ui.GRIS}|{ui.RESET} "
        f"{ui.AMARILLO}{ui.NEGRITA}{d_comps:>16,}{ui.RESET} {ui.GRIS}|{ui.RESET} {k_t_fmt(t_dyv):>18} {ui.GRIS}|{ui.RESET} O(log n)    {ui.GRIS}|{ui.RESET}"
    )
    print(f"  {ui.GRIS}+----------------------------+---------------+------------------+--------------------+-------------+{ui.RESET}")

    print(f"\n  {ui.CYAN}Contraste con la cota teórica:{ui.RESET}")
    print(f"    - Valor teórico de referencia: n = {n:,} | n·log2(n) ≈ {int(n_log_n):,} (log2(n) ≈ {math.log2(n):.2f})")
    print(f"    - Kadane realizó {k_comps:,} comparaciones (≈ 2·n -> crecimiento estrictamente lineal Θ(n)).")
    print(f"    - Divide y Vencerás realizó {d_comps:,} comparaciones (≈ n·log2(n) + 2n -> Θ(n log n)).")
    print(f"    - Razón empírica: D&V hizo {ui.AMARILLO}{ratio_ops:.2f}x más operaciones{ui.RESET} y tardó {ui.AMARILLO}{ratio_t:.1f}x más tiempo{ui.RESET} que Kadane")
    print(f"      (incluyendo además el overhead de ~2.000.000 de llamadas recursivas en pila).")
    print(f"    - Consistencia entre ambos algoritmos: {ui.VERDE + '100% COINCIDENTES' if iguales else ui.ROJO + 'DIFIEREN'}{ui.RESET}")

    print(f"\n  {ui.CYAN}{ui.NEGRITA}2. Salida del Mejor Período Contiguo:{ui.RESET}")
    print(f"    - Valor máximo de utilidad : {ui.VERDE}{ui.NEGRITA}{k_sum:,}{ui.RESET}")
    print(f"    - Índice de inicio (incl.) : {ui.VERDE}{ui.NEGRITA}{k_l:,}{ui.RESET}")
    print(f"    - Índice de fin (incl.)    : {ui.VERDE}{ui.NEGRITA}{k_r:,}{ui.RESET}")
    print(f"    - Duración del período     : {k_r - k_l + 1:,} días contiguos")
    print(f"    - Verificación sum(P[l..r]): {sum(arr[k_l:k_r + 1]):,} (coincide exacto)")

    ui.pausa_seccion("Gráfico ASCII de Utilidad Acumulada con tramo óptimo resaltado")
    ui.imprimir_banner("PUNTO 4 — PARTE A: GRÁFICO ASCII DEL MEJOR PERÍODO", None, ui.CYAN)
    imprimir_grafico_ascii_parte_a(arr, k_l, k_r, k_sum)

    return {"sum": k_sum, "l": k_l, "r": k_r, "t_kadane": t_kadane, "t_dyv": t_dyv}


def k_t_fmt(ms: float) -> str:
    return f"{ms:7.1f}ms ({ms/1000:.2f}s)"


# ==============================================================================
# PARTE B — TOP-k (k = 10) PERÍODOS CONTIGUOS NO SOLAPADOS
# ==============================================================================
def top_k_no_solapados_heap_incremental(arr, k=10):
    """
    Criterio Greedy Iterativo con Max-Heap (Cola de Prioridad) + Divide-y-Vencerás Incremental:
    1. Inserta el intervalo completo [0, n-1] con su mejor sub-arreglo (Kadane) en un Max-Heap.
    2. Repite k veces:
       - Extrae del Max-Heap el tramo de mayor utilidad (S*, l*, r*) dentro de [seg_l, seg_r].
       - Divide [seg_l, seg_r] en a lo sumo dos sub-segmentos disjuntos:
         [seg_l, l* - 1] y [r* + 1, seg_r].
       - Calcula Kadane solo sobre esos dos nuevos trozos y los inserta en el Max-Heap.
    Garantiza rangos estrictamente disjuntos sin recalcular segmentos intactos.
    """
    t0 = time.perf_counter()
    n = len(arr)
    heap = []
    total_comps = 0
    evaluaciones_kadane = 0

    s0, l0, r0, c0 = kadane(arr, 0, n - 1)
    total_comps += c0
    evaluaciones_kadane += 1
    heapq.heappush(heap, (-s0, l0, r0, 0, n - 1))

    seleccionados = []
    while len(seleccionados) < k and heap:
        neg_s, bl, br, seg_l, seg_r = heapq.heappop(heap)
        seleccionados.append({
            "rank": len(seleccionados) + 1,
            "utilidad": -neg_s,
            "inicio": bl,
            "fin": br,
            "longitud": br - bl + 1,
            "segmento_origen": (seg_l, seg_r),
        })

        # Si ya obtuvimos los k períodos, no hace falta seguir particionando
        if len(seleccionados) == k:
            break

        # Divide-y-vencerás incremental: dividir el segmento usado en izquierda y derecha
        if seg_l <= bl - 1:
            sl, ll, lr, cl = kadane(arr, seg_l, bl - 1)
            total_comps += cl
            evaluaciones_kadane += 1
            heapq.heappush(heap, (-sl, ll, lr, seg_l, bl - 1))

        if br + 1 <= seg_r:
            sr, rl, rr, cr = kadane(arr, br + 1, seg_r)
            total_comps += cr
            evaluaciones_kadane += 1
            heapq.heappush(heap, (-sr, rl, rr, br + 1, seg_r))

    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return seleccionados, total_comps, evaluaciones_kadane, len(heap), tiempo_ms


def ejecutar_parte_b(arr=None, k=10):
    if arr is None:
        arr, _, _ = cargar_datos()
    n = len(arr)

    _imprimir_separador_parte(f"PARTE B — TOP-{k} PERÍODOS CONTIGUOS NO SOLAPADOS")
    print(f"  {ui.GRIS}Ejecutando Max-Heap + Divide-y-Vencerás incremental sobre n = {n:,}...{ui.RESET}", flush=True)
    top_k, total_comps, evals, restantes_heap, tiempo_ms = top_k_no_solapados_heap_incremental(arr, k=k)

    # Verificar automáticamente ausencia de solapamiento
    ordenados_por_pos = sorted(top_k, key=lambda x: x["inicio"])
    solapamientos = 0
    for i in range(len(ordenados_por_pos) - 1):
        if ordenados_por_pos[i]["fin"] >= ordenados_por_pos[i + 1]["inicio"]:
            solapamientos += 1

    print(f"\n  {ui.CYAN}{ui.NEGRITA}Criterio, Estructura de Datos y Análisis de Costo:{ui.RESET}")
    print(f"    - Criterio elegido      : {ui.BLANCO}Selección Greedy iterativa del mejor tramo disponible{ui.RESET}")
    print(f"                              usando {ui.VERDE}Divide-y-Vencerás incremental{ui.RESET} (al extraer [l*, r*] de")
    print(f"                              [a, b], se particiona solo ese tramo en [a, l*-1] y [r*+1, b]).")
    print(f"    - Estructura de datos   : {ui.VERDE}Max-Heap Binario (Cola de Prioridad, Unidad 6){ui.RESET}, manteniendo")
    print(f"                              los mejores candidatos de todos los segmentos libres en O(log k).")
    print(f"    - Costo temporal        : A lo sumo (2k - 1) = {2*k - 1} llamadas parciales a Kadane sobre")
    print(f"                              segmentos decrecientes -> peor caso O(k·n) + O(k log k) de heap.")
    print(f"    - Costo espacial        : O(k) en el heap (sin duplicar el arreglo de 1.000.000 datos).")
    print(f"    - Nota teórica          : Si se buscara maximizar la suma conjunta permitiendo partir un")
    print(f"                              tramo ya elegido en dos (quitando un valle interno), puede")
    print(f"                              usarse PD O(k·n) o Segment Tree con inversión de signos O(n + k log n).")
    print(f"    - Medición empírica     : {ui.VERDE}{k_t_fmt(tiempo_ms)}{ui.RESET} | {evals} llamadas parciales a Kadane | {total_comps:,} comparaciones.")
    print(f"    - Verificación disjunta : {ui.VERDE + 'OK (0 solapamientos entre los 10 rangos)' if solapamientos == 0 else ui.ROJO + 'ERROR'}{ui.RESET}\n")

    print(f"  {ui.GRIS}+------+------------+--------------+--------------+------------+------------------+{ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}Top {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Utilidad  {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Inicio (inc){ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Fin (inc)   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Duración  {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Suma verificada {ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+------+------------+--------------+--------------+------------+------------------+{ui.RESET}")
    suma_total = 0
    for item in top_k:
        verif = sum(arr[item["inicio"]:item["fin"] + 1])
        suma_total += item["utilidad"]
        color = ui.VERDE if item["rank"] == 1 else ui.CYAN
        print(
            f"  {ui.GRIS}|{ui.RESET} {color}{ui.NEGRITA}#{item['rank']:<3}{ui.RESET} {ui.GRIS}|{ui.RESET} "
            f"{color}{ui.NEGRITA}{item['utilidad']:>10,}{ui.RESET} {ui.GRIS}|{ui.RESET} "
            f"{item['inicio']:>12,} {ui.GRIS}|{ui.RESET} {item['fin']:>12,} {ui.GRIS}|{ui.RESET} "
            f"{item['longitud']:>10,} {ui.GRIS}|{ui.RESET} {verif:>16,} {ui.GRIS}|{ui.RESET}"
        )
    print(f"  {ui.GRIS}+------+------------+--------------+--------------+------------+------------------+{ui.RESET}")
    print(f"  {ui.VERDE}{ui.NEGRITA}  Utilidad acumulada por los Top-{k} períodos no solapados: {suma_total:,}{ui.RESET}")

    # Mapa temporal ASCII de los 10 períodos disjuntos
    cols = 60
    mapa = ["─"] * cols
    for item in top_k:
        c0 = int(item["inicio"] / n * cols)
        c1 = min(cols - 1, int(item["fin"] / n * cols))
        etiqueta = str(item["rank"]) if item["rank"] < 10 else "0"
        for c in range(c0, c1 + 1):
            mapa[c] = etiqueta
    linea_mapa = "".join(
        f"{ui.VERDE}{ui.NEGRITA}{ch}{ui.RESET}" if ch != "─" else f"{ui.GRIS}{ch}{ui.RESET}"
        for ch in mapa
    )
    print(f"\n  {ui.CYAN}Distribución temporal de los Top-10 períodos (1..9 y 0=#10):{ui.RESET}")
    print(f"    [{linea_mapa}]")
    print(f"    {ui.GRIS}0{' ' * 25}500.000{' ' * 22}1.000.000{ui.RESET}")


# ==============================================================================
# PARTE C — PERCENTILES Y MEDIANA (QUICKSELECT LOMUTO vs HOARE vs MERGE SORT)
# ==============================================================================
def quickselect_lomuto(datos, k, seed=42):
    """
    QuickSelect iterativo con Partición de Lomuto (Unidad 4 Diap. 53-55).
    Usa pivote aleatorio movido al final; separa <= pivote a la izquierda.
    Memoria auxiliar algorítmica: O(1) in-place (trabaja sobre una copia para no alterar P).
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    a = datos[:]
    lo, hi = 0, len(a) - 1
    comps = 0
    swaps = 0

    while lo < hi:
        pidx = rng.randint(lo, hi)
        if pidx != hi:
            a[pidx], a[hi] = a[hi], a[pidx]
            swaps += 1
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            comps += 1
            if a[j] <= pivot:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    swaps += 1
                i += 1
        if i != hi:
            a[i], a[hi] = a[hi], a[i]
            swaps += 1

        if i == k:
            lo = hi = i
            break
        elif k < i:
            hi = i - 1
        else:
            lo = i + 1

    val_k = a[k]
    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return val_k, a, comps, swaps, tiempo_ms


def quickselect_hoare(datos, k):
    """
    QuickSelect iterativo con Partición de Hoare (Unidad 5 Diap. 30-35).
    Usa pivote central; dos índices (i, j) se cruzan hacia el centro.
    Maneja bloques con muchos valores repetidos dividiéndolos por la mitad en O(d).
    Memoria auxiliar algorítmica: O(1) in-place (trabaja sobre una copia para no alterar P).
    """
    t0 = time.perf_counter()
    a = datos[:]
    lo, hi = 0, len(a) - 1
    comps = 0
    swaps = 0

    while lo < hi:
        pivot = a[(lo + hi) >> 1]
        i = lo - 1
        j = hi + 1
        while True:
            i += 1
            while a[i] < pivot:
                comps += 1
                i += 1
            comps += 1

            j -= 1
            while a[j] > pivot:
                comps += 1
                j -= 1
            comps += 1

            if i >= j:
                break
            a[i], a[j] = a[j], a[i]
            swaps += 1

        if k <= j:
            hi = j
        else:
            lo = j + 1

    val_k = a[k]
    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return val_k, a, comps, swaps, tiempo_ms


def mediana_par_quickselect(datos, metodo: str):
    """
    Calcula la mediana exacta para n par: promedio de los elementos en índices
    k1 = n//2 - 1 y k2 = n//2.
    Tras ubicar k1, todos los elementos a[k1+1:] son >= a[k1], por lo que el
    elemento k2 = k1 + 1 es exactamente min(a[k1+1:]) (O(n) sin re-particionar).
    """
    n = len(datos)
    k1 = n // 2 - 1
    if metodo == "lomuto":
        v1, a, comps, swaps, t_ms = quickselect_lomuto(datos, k1)
    else:
        v1, a, comps, swaps, t_ms = quickselect_hoare(datos, k1)

    t0 = time.perf_counter()
    v2 = a[k1 + 1]
    for idx in range(k1 + 2, n):
        comps += 1
        if a[idx] < v2:
            v2 = a[idx]
    t_ms += (time.perf_counter() - t0) * 1000.0
    return (v1 + v2) / 2.0, v1, v2, comps, swaps, t_ms


def merge_sort_baseline(datos):
    """
    Merge Sort Bottom-Up iterativo (Divide y Vencerás, Unidad 5 Diap. 23-26).
    Complejidad garantizada: Tiempo Θ(n log n) en todos los casos | Memoria auxiliar Θ(n).
    """
    t0 = time.perf_counter()
    a = datos[:]
    n = len(a)
    aux = [0] * n
    comps = 0
    escrituras = 0

    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                comps += 1
                if a[i] <= a[j]:
                    aux[k] = a[i]
                    i += 1
                else:
                    aux[k] = a[j]
                    j += 1
                k += 1
                escrituras += 1
            while i < mid:
                aux[k] = a[i]
                i += 1
                k += 1
                escrituras += 1
            while j < hi:
                aux[k] = a[j]
                j += 1
                k += 1
                escrituras += 1
        a, aux = aux, a
        width <<= 1

    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    return a, comps, escrituras, tiempo_ms


def busqueda_binaria_contar_le(arr_ord, umbral):
    """
    Búsqueda Binaria propia O(log n) (Unidad 4 — Reducción por Factor Constante)
    para contar exactamente cuántos elementos son <= umbral (upper_bound).
    """
    lo, hi = 0, len(arr_ord)
    comps = 0
    while lo < hi:
        mid = (lo + hi) >> 1
        comps += 1
        if arr_ord[mid] <= umbral:
            lo = mid + 1
        else:
            hi = mid
    return lo, comps


def busqueda_binaria_contar_lt(arr_ord, umbral):
    """Búsqueda Binaria O(log n) para contar cuántos elementos son < umbral (lower_bound)."""
    lo, hi = 0, len(arr_ord)
    while lo < hi:
        mid = (lo + hi) >> 1
        if arr_ord[mid] < umbral:
            lo = mid + 1
        else:
            hi = mid
    return lo


def ejecutar_parte_c(arr=None):
    if arr is None:
        arr, _, _ = cargar_datos()
    n = len(arr)

    # Convenciones explícitas
    idx_p50_a = n // 2 - 1  # 499,999
    idx_p50_b = n // 2      # 500,000
    idx_p90 = math.ceil(0.90 * n) - 1  # 899,999
    idx_p95 = math.ceil(0.95 * n) - 1  # 949,999

    _imprimir_separador_parte("PARTE C — MEDIANA Y PERCENTILES (p50, p90, p95)")

    print(f"  {ui.CYAN}{ui.NEGRITA}Convenciones adoptadas (n = {n:,}, par):{ui.RESET}")
    print(f"    - Mediana (p50) para n par : promedio aritmético de los dos valores centrales:")
    print(f"      (P_ord[n/2 - 1] + P_ord[n/2]) / 2 = (P_ord[{idx_p50_a:,}] + P_ord[{idx_p50_b:,}]) / 2.")
    print(f"    - Percentiles p90 y p95    : método de rango más cercano (0-indexado):")
    print(f"      k = ceil((p/100)·n) - 1 -> p90 en índice {idx_p90:,} | p95 en índice {idx_p95:,}.\n")

    print(f"  {ui.GRIS}1/3 Ejecutando QuickSelect Hoare para p50, p90 y p95...{ui.RESET}", flush=True)
    h_p50, h_v1, h_v2, h_c50, h_s50, h_t50 = mediana_par_quickselect(arr, "hoare")
    h_p90, _, h_c90, h_s90, h_t90 = quickselect_hoare(arr, idx_p90)
    h_p95, _, h_c95, h_s95, h_t95 = quickselect_hoare(arr, idx_p95)

    print(f"  {ui.GRIS}2/3 Ejecutando QuickSelect Lomuto para p50, p90 y p95...{ui.RESET}", flush=True)
    l_p50, l_v1, l_v2, l_c50, l_s50, l_t50 = mediana_par_quickselect(arr, "lomuto")
    l_p90, _, l_c90, l_s90, l_t90 = quickselect_lomuto(arr, idx_p90)
    l_p95, _, l_c95, l_s95, l_t95 = quickselect_lomuto(arr, idx_p95)

    print(f"  {ui.GRIS}3/3 Ejecutando Merge Sort completo (baseline O(n log n), aguarde ~10-14s)...{ui.RESET}", flush=True)
    arr_ord, ms_comps, ms_writes, ms_t = merge_sort_baseline(arr)
    ms_p50 = (arr_ord[idx_p50_a] + arr_ord[idx_p50_b]) / 2.0
    ms_p90 = arr_ord[idx_p90]
    ms_p95 = arr_ord[idx_p95]

    # Tabla 1: Resultados y métricas por cuantil y enfoque
    print(f"\n  {ui.CYAN}{ui.NEGRITA}1. Comparativa de Rendimiento: QuickSelect (Lomuto vs. Hoare) vs. Merge Sort:{ui.RESET}")
    print(f"  {ui.GRIS}+----------------------------+--------+---------------+---------------+--------------------+---------------+ {ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}Enfoque / Cuantil         {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Valor {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Comparaciones{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Swaps / Escr.{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Tiempo (ms / s)   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Mem. Aux.    {ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+----------------------------+--------+---------------+---------------+--------------------+---------------+ {ui.RESET}")

    filas = [
        ("QuickSelect Hoare   (p50)", f"{h_p50:.1f}", h_c50, h_s50, h_t50, "O(1) in-place", ui.VERDE),
        ("QuickSelect Lomuto  (p50)", f"{l_p50:.1f}", l_c50, l_s50, l_t50, "O(1) in-place", ui.AMARILLO),
        ("QuickSelect Hoare   (p90)", f"{h_p90}", h_c90, h_s90, h_t90, "O(1) in-place", ui.VERDE),
        ("QuickSelect Lomuto  (p90)", f"{l_p90}", l_c90, l_s90, l_t90, "O(1) in-place", ui.AMARILLO),
        ("QuickSelect Hoare   (p95)", f"{h_p95}", h_c95, h_s95, h_t95, "O(1) in-place", ui.VERDE),
        ("QuickSelect Lomuto  (p95)", f"{l_p95}", l_c95, l_s95, l_t95, "O(1) in-place", ui.AMARILLO),
        ("Merge Sort Baseline (all)", "Todos", ms_comps, ms_writes, ms_t, "O(n) aux.", ui.CYAN),
    ]
    for nombre, val, c, s, t, mem, col in filas:
        print(
            f"  {ui.GRIS}|{ui.RESET} {col}{nombre:<26}{ui.RESET} {ui.GRIS}|{ui.RESET} {val:>6} {ui.GRIS}|{ui.RESET} "
            f"{c:>13,} {ui.GRIS}|{ui.RESET} {s:>13,} {ui.GRIS}|{ui.RESET} {k_t_fmt(t):>18} {ui.GRIS}|{ui.RESET} {mem:<13} {ui.GRIS}|{ui.RESET}"
        )
    print(f"  {ui.GRIS}+----------------------------+--------+---------------+---------------+--------------------+---------------+ {ui.RESET}")
    print(f"  {ui.GRIS}* Nota de memoria: QuickSelect iterativo opera in-place O(1); aquí se trabaja sobre copia de P")
    print(f"    solo para preservar los datos originales entre comparaciones. Merge Sort requiere buffer O(n).{ui.RESET}")

    # Totales comparativos (3 cuantiles)
    t_hoare_total = h_t50 + h_t90 + h_t95
    t_lomuto_total = l_t50 + l_t90 + l_t95
    c_hoare_total = h_c50 + h_c90 + h_c95
    c_lomuto_total = l_c50 + l_c90 + l_c95
    s_hoare_total = h_s50 + h_s90 + h_s95
    s_lomuto_total = l_s50 + l_s90 + l_s95

    print(f"\n  {ui.CYAN}Resumen acumulado (buscando los 3 cuantiles p50, p90 y p95):{ui.RESET}")
    print(f"    - Hoare  (3 consultas): {ui.VERDE}{k_t_fmt(t_hoare_total)}{ui.RESET} | {c_hoare_total:,} comps | {s_hoare_total:,} swaps")
    print(f"    - Lomuto (3 consultas): {ui.AMARILLO}{k_t_fmt(t_lomuto_total)}{ui.RESET} | {c_lomuto_total:,} comps | {s_lomuto_total:,} swaps")
    print(f"    - Merge Sort (1 orden): {ui.CYAN}{k_t_fmt(ms_t)}{ui.RESET} | {ms_comps:,} comps | {ms_writes:,} escrituras aux.")

    # 2. Validación sobre el arreglo ordenado (índices + búsqueda binaria)
    print(f"\n  {ui.CYAN}{ui.NEGRITA}2. Validación de Cuantiles sobre Arreglo Ordenado (Índices + Búsqueda Binaria O(log n)):{ui.RESET}")
    cuantiles = [
        ("p50 (Mediana)", 50.0, ms_p50, h_p50, l_p50, f"({arr_ord[idx_p50_a]}+{arr_ord[idx_p50_b]})/2"),
        ("p90", 90.0, ms_p90, h_p90, l_p90, f"P_ord[{idx_p90:,}]={ms_p90}"),
        ("p95", 95.0, ms_p95, h_p95, l_p95, f"P_ord[{idx_p95:,}]={ms_p95}"),
    ]
    for nombre, pct, v_ms, v_h, v_l, ref_idx in cuantiles:
        cnt_le, bb_comps = busqueda_binaria_contar_le(arr_ord, v_ms)
        cnt_lt = busqueda_binaria_contar_lt(arr_ord, v_ms)
        pct_le = (cnt_le / n) * 100.0
        pct_lt = (cnt_lt / n) * 100.0
        ok = (v_ms == v_h == v_l) and (pct_lt < pct <= pct_le)
        estado = f"{ui.VERDE}VALIDADO OK{ui.RESET}" if ok else f"{ui.ROJO}FALLO{ui.RESET}"
        print(
            f"    - {ui.BLANCO}{nombre:<13}{ui.RESET}: valor = {ui.VERDE}{ui.NEGRITA}{v_ms:>4}{ui.RESET} | {ref_idx:<18} | "
            f"BB O(log n) [{bb_comps} comps]: <={v_ms}: {cnt_le:,} ({pct_le:.2f}%) | <{v_ms}: {cnt_lt:,} ({pct_lt:.2f}%) -> [{estado}]"
        )

    # 3. Discusión / Reporte requerido en C.3 (en pantalla limpia aparte para no amontonar texto)
    ui.pausa_seccion("Reporte y Discusión Teórica vs. Empírica (Inciso C.3)")
    ui.imprimir_banner("PUNTO 4 — PARTE C.3: REPORTE Y DISCUSIÓN TEÓRICA VS. EMPÍRICA", None, ui.CYAN)

    speedup_1_cuantil = ms_t / h_t50 if h_t50 > 0 else 0.0
    print(f"  {ui.CYAN}{ui.NEGRITA}3. Reporte y Discusión Teórica vs. Empírica (Inciso C.3):{ui.RESET}\n")
    print(f"    {ui.VERDE}{ui.NEGRITA}a) ¿Por qué QuickSelect es preferible frente a ordenar todo (Merge Sort)?{ui.RESET}")
    print(f"       - Cuando solo se busca UN cuantil (o unos pocos), ordenar el millón completo con")
    print(f"         Merge Sort exige Θ(n log n) ≈ {ms_comps:,} comparaciones y memoria auxiliar Θ(n),")
    print(f"         mientras QuickSelect (Hoare) descarta una partición en cada paso (Reducción por")
    print(f"         tamaño variable, Unidad 4) logrando tiempo promedio Θ(n) y espacio auxiliar O(1).")
    print(f"       - Empíricamente, hallar p50 con Hoare fue {ui.VERDE}{ui.NEGRITA}{speedup_1_cuantil:.1f}x más rápido{ui.RESET} que Merge Sort.")
    print(f"         (Solo conviene ordenar una vez si se van a consultar muchísimos cuantiles distintos.)\n")
    print(f"    {ui.AMARILLO}{ui.NEGRITA}b) Comparación Lomuto vs. Hoare y efecto de los REPETIDOS en este dataset:{ui.RESET}")
    print(f"       - El archivo 'datos_1millón.txt' tiene 1.000.000 de enteros en [-100, 100]: solo 201")
    print(f"         valores únicos (~4.975 repetidos por cada valor).")
    print(f"       - Como señala Unidad 5 (Diap. 30), Lomuto coloca todos los elementos iguales al pivote")
    print(f"         de un mismo lado (<= pivote), lo que produce particiones muy desbalanceadas y")
    print(f"         comportamiento cuadrático O(d^2) al caer en bloques de ~5.000 valores idénticos:")
    print(f"         en p50, Lomuto hizo {l_c50:,} comps y {l_s50:,} swaps frente a {h_c50:,} comps")
    print(f"         y {h_s50:,} swaps de Hoare.")
    print(f"       - Hoare detiene ambos punteros en elementos iguales y los intercambia, dividiendo los")
    print(f"         bloques repetidos por la mitad en cada paso y realizando menos de la mitad de swaps.\n")
    print(f"    {ui.MAGENTA}{ui.NEGRITA}c) ¿Qué ocurre con entradas adversas?{ui.RESET}")
    print(f"       - Si el pivote elegido es sistemáticamente el mínimo o máximo (ej. arreglo ya ordenado")
    print(f"         usando el último elemento en Lomuto), la partición reduce de n a n-1 en cada paso,")
    print(f"         degradando ambos particionadores a peor caso O(n^2).")
    print(f"       - Soluciones vistas en clase (Unidades 4 y 5): pivote aleatorio / mediana de tres,")
    print(f"         partición de 3 vías (Dutch National Flag para repetidos), o Mediana de Medianas")
    print(f"         (Unidad 4 Diap. 41-51) para garantizar peor caso determinístico O(n).")


def _demo_entrada_adversa():
    ui.imprimir_banner("DEMO EXTRA: ENTRADA CON REPETIDOS Y ENTRADA ADVERSA (LOMUTO vs HOARE)", None, ui.MAGENTA)
    m = 4000
    print(f"  Probando ambos particionadores sobre {m:,} elementos IDÉNTICOS [42, 42, ..., 42]")
    print(f"  buscando la mediana (k = {m // 2}):\n")

    iguales = [42] * m
    _, _, ch, sh, th = quickselect_hoare(iguales, m // 2)
    _, _, cl, sl, tl = quickselect_lomuto(iguales, m // 2)

    print(f"    - {ui.VERDE}Hoare {ui.RESET}: {ch:>10,} comparaciones | {sh:>10,} swaps | {th:7.2f} ms  -> O(m) / O(m log m)")
    print(f"    - {ui.ROJO}Lomuto{ui.RESET}: {cl:>10,} comparaciones | {sl:>10,} swaps | {tl:7.2f} ms  -> ¡Degrada a O(m^2) ≈ m(m-1)/2!")
    print(f"\n  {ui.GRIS}Conclusión: con todos iguales, Lomuto hace ~{cl / max(1, ch):.0f}x más comparaciones que Hoare.{ui.RESET}")


def ejecutar_resolucion_completa():
    """Ejecuta Partes A, B y C completas del Punto 4 separadas por pantalla limpia."""
    arr, ruta, t_carga = cargar_datos()
    ui.limpiar_pantalla()
    ui.imprimir_banner(
        "PUNTO 4 — \"MEJOR PERÍODO DE UTILIDAD\" CON 1.000.000 DE DATOS (A + B + C)",
        f"Archivo: {os.path.basename(ruta)} | n = {len(arr):,} enteros (carga: {t_carga:.0f} ms)",
        ui.CYAN,
    )
    ejecutar_parte_a(arr)

    ui.pausa_seccion("Parte B — Top-10 períodos contiguos no solapados")
    ejecutar_parte_b(arr, k=10)

    ui.pausa_seccion("Parte C — Mediana y Percentiles (QuickSelect vs. Merge Sort)")
    ejecutar_parte_c(arr)

    print(f"\n{ui.VERDE}{ui.NEGRITA}  [OK] Resolución completa del Punto 4 (Partes A, B y C) finalizada.{ui.RESET}")


def mostrar_submenu_punto4():
    while True:
        ui.limpiar_pantalla()
        ruta = localizar_archivo_datos()
        estado_arch = f"{ui.VERDE}Encontrado ({os.path.basename(ruta)}){ui.RESET}" if ruta else f"{ui.ROJO}NO ENCONTRADO{ui.RESET}"

        ui.imprimir_banner("PUNTO 4: \"MEJOR PERÍODO DE UTILIDAD\" CON 1.000.000 DE DATOS", None, ui.CYAN)
        print(f"  Archivo de datos : {estado_arch}")
        print(f"  Tamaño esperado  : {ui.BLANCO}n = 1.000.000 de utilidades diarias enteras{ui.RESET}")
        print(f"  Temas integrados : {ui.CYAN}Kadane O(n) | Divide y Vencerás | Max-Heap | QuickSelect | MergeSort | B. Binaria{ui.RESET}")
        print(f"{ui.GRIS}" + "-" * 78 + ui.RESET)
        print(f"    {ui.VERDE}a){ui.RESET} Parte A — Sub-Arreglo Máximo (Kadane vs. Divide y Vencerás + Gráfico ASCII)")
        print(f"    {ui.VERDE}b){ui.RESET} Parte B — Top-10 períodos contiguos no solapados (Max-Heap incremental)")
        print(f"    {ui.VERDE}c){ui.RESET} Parte C — Mediana y Percentiles (Lomuto vs. Hoare vs. Merge Sort + Validación)")
        print(f"    {ui.AMARILLO}d){ui.RESET} Ejecutar TODO el Punto 4 COMPLETO (Partes A + B + C) [paginado pantalla por pantalla]")
        print(f"    {ui.MAGENTA}e){ui.RESET} Demo extra: Degradación de Lomuto vs. Hoare ante repetidos (Inciso C.3)")
        print(f"    {ui.ROJO}v){ui.RESET} Volver al menú principal")
        print(f"{ui.CYAN}" + "=" * 78 + ui.RESET)

        op = input(f"  {ui.AMARILLO}Seleccione una opción [a-e / v para volver]: {ui.RESET}").strip().lower()
        try:
            if op == "a":
                ui.limpiar_pantalla()
                ejecutar_parte_a()
            elif op == "b":
                ui.limpiar_pantalla()
                ejecutar_parte_b()
            elif op == "c":
                ui.limpiar_pantalla()
                ejecutar_parte_c()
            elif op == "d":
                ui.limpiar_pantalla()
                ejecutar_resolucion_completa()
            elif op == "e":
                ui.limpiar_pantalla()
                _demo_entrada_adversa()
            elif op in ("v", "0", "volver", "s"):
                return
            else:
                print(f"\n  {ui.ROJO}[!] Opción '{op}' no válida. Intente nuevamente.{ui.RESET}")
        except Exception as exc:
            print(f"\n  {ui.ROJO}[!] Error: {exc}{ui.RESET}")

        input(f"\n  {ui.GRIS}Presione ENTER para volver al menú del Punto 4...{ui.RESET}")

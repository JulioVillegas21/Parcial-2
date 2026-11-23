#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
UNIVERSIDAD NACIONAL DE VILLA MERCEDES (UNViMe)
Asignatura : Análisis y Diseño de Algoritmos
Examen 2 - Práctica | Punto 1: Corrector Ortográfico (Distancia de Levenshtein)
================================================================================

Implementa Programación Dinámica (Tabulación Bottom-Up, Unidad 7) para calcular
la distancia de Levenshtein, reconstruir el camino óptimo desde (m, n) hasta (0, 0),
detallar las operaciones exactas en orden y ofrecer búsqueda optimizada con BK-Tree.
"""

import unicodedata
from collections import deque
import ui_consola as ui

PALABRA_OBJETIVO_DEFECTO = "programaceón"
UMBRAL_DISTANCIA = 3

DICCIONARIO_DEFECTO = [
    "programación",
    "programador",
    "programaciónes",
    "programaciónal",
    "programación web",
    "probabilístico",
]

# Por defecto se normalizan tildes (ó == o) para coincidir con el ejemplo del práctico
# donde "programador" tiene distancia = 3. Se puede alternar desde el submenú.
_ignorar_tildes = True


def normalizar_caracter(ch: str, ignorar_tildes: bool) -> str:
    """Normaliza a minúscula y opcionalmente quita tildes (conservando 'ñ')."""
    ch = ch.lower()
    if not ignorar_tildes or ch == "ñ":
        return ch
    descompuesto = unicodedata.normalize("NFD", ch)
    for c in descompuesto:
        if unicodedata.category(c) != "Mn":
            return c
    return ch


def son_equivalentes(a: str, b: str, ignorar_tildes: bool) -> bool:
    if len(a) != len(b):
        return False
    return all(
        normalizar_caracter(ca, ignorar_tildes) == normalizar_caracter(cb, ignorar_tildes)
        for ca, cb in zip(a, b)
    )


def calcular_levenshtein(origen: str, destino: str, ignorar_tildes: bool = True) -> dict:
    """
    Calcula la matriz completa de Levenshtein por Programación Dinámica O(m * n),
    reconstruye el camino óptimo desde (m, n) hasta (0, 0) y extrae exactamente
    las operaciones realizadas y su orden cronológico.
    """
    m = len(origen)
    n = len(destino)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Casos base
    for i in range(m + 1):
        dp[i][0] = i  # i eliminaciones
    for j in range(n + 1):
        dp[0][j] = j  # j inserciones

    # Inciso F: rellenar cada celda aplicando Inserción, Eliminación y Sustitución
    for i in range(1, m + 1):
        c_orig = normalizar_caracter(origen[i - 1], ignorar_tildes)
        for j in range(1, n + 1):
            c_dest = normalizar_caracter(destino[j - 1], ignorar_tildes)
            costo_sust = 0 if c_orig == c_dest else 1

            insercion = dp[i][j - 1] + 1
            eliminacion = dp[i - 1][j] + 1
            sustitucion = dp[i - 1][j - 1] + costo_sust

            dp[i][j] = min(insercion, eliminacion, sustitucion)

    # Inciso H: reconstruir el camino óptimo desde (m, n) hasta (0, 0)
    camino_desde_final = []
    pasos_invertidos = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            c_orig = normalizar_caracter(origen[i - 1], ignorar_tildes)
            c_dest = normalizar_caracter(destino[j - 1], ignorar_tildes)
            costo_sust = 0 if c_orig == c_dest else 1
            if dp[i][j] == dp[i - 1][j - 1] + costo_sust:
                tipo = "SIN_CAMBIO" if costo_sust == 0 else "SUSTITUCION"
                paso = {
                    "fila": i,
                    "col": j,
                    "costo": dp[i][j],
                    "tipo": tipo,
                    "char_origen": origen[i - 1],
                    "char_destino": destino[j - 1],
                }
                camino_desde_final.append(paso)
                pasos_invertidos.append(paso)
                i -= 1
                j -= 1
                continue

        if i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            paso = {
                "fila": i,
                "col": j,
                "costo": dp[i][j],
                "tipo": "ELIMINACION",
                "char_origen": origen[i - 1],
                "char_destino": "",
            }
            camino_desde_final.append(paso)
            pasos_invertidos.append(paso)
            i -= 1
        else:
            paso = {
                "fila": i,
                "col": j,
                "costo": dp[i][j],
                "tipo": "INSERCION",
                "char_origen": "",
                "char_destino": destino[j - 1],
            }
            camino_desde_final.append(paso)
            pasos_invertidos.append(paso)
            j -= 1

    camino_desde_final.append({
        "fila": 0,
        "col": 0,
        "costo": 0,
        "tipo": "INICIO",
        "char_origen": "",
        "char_destino": "",
    })

    # Inciso I: secuencia exacta de operaciones en orden cronológico
    pasos_invertidos.reverse()
    texto_actual = list(origen)
    cursor = 0
    operaciones_en_orden = []

    for paso in pasos_invertidos:
        tipo = paso["tipo"]
        if tipo == "SIN_CAMBIO":
            if paso["char_origen"] != paso["char_destino"]:
                texto_actual[cursor] = paso["char_destino"]
                desc = (
                    f"Equivalencia sin tilde (costo +0): "
                    f"'{paso['char_origen']}' == '{paso['char_destino']}' en pos {cursor + 1}"
                )
            else:
                desc = f"Coincide '{paso['char_origen']}' en pos {cursor + 1} (costo +0)"
            cursor += 1
            estado = "".join(texto_actual)
        elif tipo == "SUSTITUCION":
            texto_actual[cursor] = paso["char_destino"]
            desc = (
                f"SUSTITUCIÓN: reemplazar '{paso['char_origen']}' por "
                f"'{paso['char_destino']}' en pos {cursor + 1} (costo +1)"
            )
            cursor += 1
            estado = "".join(texto_actual)
        elif tipo == "ELIMINACION":
            texto_actual.pop(cursor)
            desc = f"ELIMINACIÓN: borrar '{paso['char_origen']}' en pos {cursor + 1} (costo +1)"
            estado = "".join(texto_actual)
        else:  # INSERCION
            texto_actual.insert(cursor, paso["char_destino"])
            desc = f"INSERCIÓN: insertar '{paso['char_destino']}' en pos {cursor + 1} (costo +1)"
            cursor += 1
            estado = "".join(texto_actual)

        op_info = dict(paso)
        op_info["descripcion"] = desc
        op_info["estado"] = estado
        operaciones_en_orden.append(op_info)

    return {
        "origen": origen,
        "destino": destino,
        "matriz": dp,
        "distancia": dp[m][n],
        "camino_desde_final": camino_desde_final,
        "operaciones_en_orden": operaciones_en_orden,
        "ignorar_tildes": ignorar_tildes,
    }


def calcular_distancia_rapida(origen: str, destino: str, ignorar_tildes: bool = True) -> int:
    """Versión optimizada en espacio O(min(m, n)) usada internamente por BK-Tree."""
    m, n = len(origen), len(destino)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        c_orig = normalizar_caracter(origen[i - 1], ignorar_tildes)
        for j in range(1, n + 1):
            c_dest = normalizar_caracter(destino[j - 1], ignorar_tildes)
            costo = 0 if c_orig == c_dest else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + costo)
        prev = curr
    return prev[n]


class BKTree:
    """
    Árbol BK (Burkhard-Keller Tree) para búsqueda optimizada de palabras similares
    usando la desigualdad triangular de la distancia de Levenshtein (Unidad 7 - Diap. 36).
    """

    def __init__(self, ignorar_tildes: bool = True):
        self.raiz = None
        self.ignorar_tildes = ignorar_tildes

    def insertar(self, palabra: str):
        if self.raiz is None:
            self.raiz = {"palabra": palabra, "hijos": {}}
            return
        actual = self.raiz
        while True:
            d = calcular_distancia_rapida(actual["palabra"], palabra, self.ignorar_tildes)
            if d == 0:
                return
            if d in actual["hijos"]:
                actual = actual["hijos"][d]
            else:
                actual["hijos"][d] = {"palabra": palabra, "hijos": {}}
                return

    def buscar(self, consulta: str, tolerancia: int):
        resultados = []
        nodos_visitados = 0
        if self.raiz is None:
            return resultados, nodos_visitados

        cola = deque([self.raiz])
        while cola:
            actual = cola.popleft()
            nodos_visitados += 1
            d = calcular_distancia_rapida(consulta, actual["palabra"], self.ignorar_tildes)
            if d <= tolerancia:
                resultados.append((actual["palabra"], d))
            min_d = d - tolerancia
            max_d = d + tolerancia
            for dist_arista, hijo in actual["hijos"].items():
                if min_d <= dist_arista <= max_d:
                    cola.append(hijo)

        resultados.sort(key=lambda x: (x[1], x[0].lower()))
        return resultados, nodos_visitados

    def imprimir(self):
        if self.raiz is None:
            print(f"  {ui.GRIS}(BK-Tree vacío){ui.RESET}")
            return
        self._imprimir_nodo(self.raiz, "  ", True, None)

    def _imprimir_nodo(self, nodo, prefijo: str, es_ultimo: bool, dist_arista):
        conector = "└── " if es_ultimo else "├── "
        if dist_arista is None:
            etiqueta = f"{ui.CYAN}{ui.NEGRITA}(raíz) {nodo['palabra']}{ui.RESET}"
        else:
            etiqueta = f"{ui.AMARILLO}[d={dist_arista}]{ui.RESET} {ui.BLANCO}{nodo['palabra']}{ui.RESET}"
        print(f"{ui.GRIS}{prefijo}{conector}{ui.RESET}{etiqueta}")
        hijos = sorted(nodo["hijos"].items(), key=lambda kv: kv[0])
        for idx, (d, hijo) in enumerate(hijos):
            ultimo = idx == len(hijos) - 1
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            self._imprimir_nodo(hijo, nuevo_prefijo, ultimo, d)


def imprimir_matriz(res: dict):
    """Imprime la matriz completa de Levenshtein con verde y '*' en el camino óptimo."""
    origen = res["origen"]
    destino = res["destino"]
    dp = res["matriz"]
    en_camino = {(p["fila"], p["col"]) for p in res["camino_desde_final"]}

    encabezado_cols = "".join(
        f"{('`' + ch + '`') if ch == ' ' else ch:>3} " for ch in destino
    )
    print(f"        {ui.CYAN}|  \"\" {encabezado_cols}{ui.RESET}")
    print(f"  {ui.GRIS}------+-----" + "----" * len(destino) + ui.RESET)

    for i in range(len(origen) + 1):
        etiqueta = '""' if i == 0 else ("' '" if origen[i - 1] == " " else origen[i - 1])
        fila_str = f"  {ui.CYAN}{i:>2} {etiqueta:>2}{ui.RESET} {ui.GRIS}|{ui.RESET} "
        for j in range(len(destino) + 1):
            if (i, j) in en_camino:
                fila_str += f"{ui.VERDE}{ui.NEGRITA}{dp[i][j]:>3}*{ui.RESET}"
            else:
                fila_str += f"{dp[i][j]:>3} "
        print(fila_str)


def imprimir_traza_celdas(res: dict):
    """Muestra los 3 costos (Inserción, Eliminación, Sustitución) para cada celda (Inciso F)."""
    origen = res["origen"]
    destino = res["destino"]
    dp = res["matriz"]
    ignorar = res["ignorar_tildes"]

    print(f"      {ui.CYAN}Celda  | Orig -> Dest | Ins  | Elim | Sust | Min{ui.RESET}")
    print(f"      {ui.GRIS}-------+--------------+------+------+------+-----{ui.RESET}")
    for i in range(1, len(origen) + 1):
        c_orig = normalizar_caracter(origen[i - 1], ignorar)
        for j in range(1, len(destino) + 1):
            c_dest = normalizar_caracter(destino[j - 1], ignorar)
            costo_sust = 0 if c_orig == c_dest else 1
            ins = dp[i][j - 1] + 1
            elim = dp[i - 1][j] + 1
            sust = dp[i - 1][j - 1] + costo_sust
            print(
                f"      ({i:>2},{j:>2}) |  '{origen[i-1]}' -> '{destino[j-1]}'  "
                f"| {ins:>4} | {elim:>4} | {sust:>4} | {ui.VERDE}{dp[i][j]:>3}{ui.RESET}"
            )


def imprimir_detalle_completo(res: dict, numero: int, mostrar_traza_celdas: bool = False):
    """Muestra los incisos E, F, G, H, I completos y bien distinguidos para un par de palabras."""
    print(f"  {ui.CYAN}{ui.NEGRITA}" + "=" * 74 + ui.RESET)
    print(f"  {ui.CYAN}{ui.NEGRITA}PALABRA #{numero}: \"{res['origen']}\"  -->  \"{res['destino']}\"{ui.RESET}")
    print(f"  {ui.CYAN}{ui.NEGRITA}" + "=" * 74 + ui.RESET)

    # [INCISO E] Matriz completa
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}>>> INCISO E — Construcción de la matriz completa ({len(res['origen'])+1}x{len(res['destino'])+1}){ui.RESET}")
    print(f"  {ui.GRIS}    (Las celdas marcadas con {ui.VERDE}*{ui.GRIS} pertenecen al camino óptimo){ui.RESET}")
    imprimir_matriz(res)

    # [INCISO F] Reglas aplicadas al rellenar cada celda
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}>>> INCISO F — Regla de relleno aplicada en cada celda (i, j):{ui.RESET}")
    print(f"      1. Inserción   : dp[i, j-1] + 1")
    print(f"      2. Eliminación : dp[i-1, j] + 1")
    print(f"      3. Sustitución : dp[i-1, j-1] + costo (0 si coinciden, 1 si difieren)")
    if mostrar_traza_celdas:
        print()
        imprimir_traza_celdas(res)
    else:
        print(f"      {ui.GRIS}(Para ver la tabla de cálculo celda por celda, use la opción b del submenú){ui.RESET}")

    # [INCISO G] Distancia mínima
    pasa = res["distancia"] <= UMBRAL_DISTANCIA
    color_dist = ui.VERDE if pasa else ui.ROJO
    estado_umbral = f"Seleccionada: <= {UMBRAL_DISTANCIA}" if pasa else f"Descartada: > {UMBRAL_DISTANCIA}"
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}>>> INCISO G — Distancia mínima obtenida:{ui.RESET}")
    print(f"      dp[{len(res['origen'])}, {len(res['destino'])}] = {color_dist}{ui.NEGRITA}{res['distancia']}{ui.RESET}  ({color_dist}{estado_umbral}{ui.RESET})")

    # [INCISO H] Camino óptimo desde (m, n) hasta (0, 0)
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}>>> INCISO H — Reconstrucción del camino óptimo desde ({len(res['origen'])},{len(res['destino'])}) hasta (0,0):{ui.RESET}")
    partes = [f"{ui.VERDE}({p['fila']},{p['col']}){ui.RESET}[={p['costo']}]" for p in res["camino_desde_final"]]
    for idx in range(0, len(partes), 6):
        linea = f" {ui.GRIS}->{ui.RESET} ".join(partes[idx:idx + 6])
        sufijo = f" {ui.GRIS}->{ui.RESET}" if idx + 6 < len(partes) else ""
        print(f"      {linea}{sufijo}")

    # [INCISO I] Operaciones exactas en orden
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}>>> INCISO I — Operaciones exactas realizadas y en qué orden:{ui.RESET}")
    print(f"      Transformando \"{res['origen']}\"  -->  \"{res['destino']}\":")
    paso_num = 0
    cant_sust = cant_ins = cant_elim = 0
    for op in res["operaciones_en_orden"]:
        if op["tipo"] != "SIN_CAMBIO":
            paso_num += 1
            if op["tipo"] == "SUSTITUCION":
                cant_sust += 1
            elif op["tipo"] == "INSERCION":
                cant_ins += 1
            elif op["tipo"] == "ELIMINACION":
                cant_elim += 1
            print(f"      {ui.AMARILLO}{ui.NEGRITA}Paso {paso_num}:{ui.RESET} {ui.BLANCO}{op['descripcion']}{ui.RESET}")
            print(f"              {ui.GRIS}Estado resultante:{ui.RESET} {ui.CYAN}\"{op['estado']}\"{ui.RESET}")
        elif op["char_origen"] != op["char_destino"]:
            print(f"      {ui.GRIS}(Nota): {op['descripcion']} -> \"{op['estado']}\"{ui.RESET}")

    if paso_num == 0:
        print(f"      {ui.VERDE}Ninguna operación de edición necesaria (las palabras coinciden).{ui.RESET}")
    else:
        print(
            f"      {ui.MAGENTA}Resumen:{ui.RESET} {paso_num} edición(es) total(es) -> "
            f"{cant_sust} Sustitución(es), {cant_ins} Inserción(es), {cant_elim} Eliminación(es)."
        )


def _imprimir_separador_inciso(letra: str, titulo: str):
    print(f"\n  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)
    print(f"  {ui.AMARILLO}{ui.NEGRITA}INCISO {letra} — {titulo}{ui.RESET}")
    print(f"  {ui.AMARILLO}{ui.NEGRITA}" + "-" * 74 + ui.RESET)


def ejecutar_resolucion_completa(
    palabra_origen: str = PALABRA_OBJETIVO_DEFECTO,
    diccionario=None,
    mostrar_todas_matrices: bool = True,
    ignorar_tildes=None,
):
    """Ejecuta todos los incisos A hasta I del Punto 1 bien diferenciados."""
    if diccionario is None:
        diccionario = DICCIONARIO_DEFECTO
    if ignorar_tildes is None:
        ignorar_tildes = _ignorar_tildes

    ui.imprimir_banner(f"PUNTO 1 — RESOLUCIÓN COMPLETA (INCISOS A - I) | Palabra: \"{palabra_origen}\"", None, ui.CYAN)
    modo_txt = (
        "Normalizado SIN distinguir tildes (ó = o)"
        if ignorar_tildes
        else "Exacto DISTINGUIENDO tildes (ó != o)"
    )
    print(f"  {ui.CYAN}Modo de comparación activo:{ui.RESET} {ui.BLANCO}{ui.NEGRITA}{modo_txt}{ui.RESET}")

    existe = any(son_equivalentes(palabra_origen, p, ignorar_tildes) for p in diccionario)
    if existe:
        print(f"\n  {ui.VERDE}{ui.NEGRITA}[OK] La palabra \"{palabra_origen}\" EXISTE en el diccionario (reconocida, distancia = 0).{ui.RESET}")

    resultados = [calcular_levenshtein(palabra_origen, p, ignorar_tildes) for p in diccionario]

    # =========================================================================
    # INCISO A: Calcular todas las distancias
    # =========================================================================
    _imprimir_separador_inciso("A", "Calcular todas las distancias (Levenshtein contra el diccionario)")
    print(f"  {ui.GRIS}+----+--------------------+-----------+--------------+--------------------+{ui.RESET}")
    print(f"  {ui.GRIS}|{ui.RESET} {ui.BLANCO}N°{ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Palabra           {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Longitud {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}Distancia   {ui.RESET} {ui.GRIS}|{ui.RESET} {ui.BLANCO}¿Distancia <= {UMBRAL_DISTANCIA}?  {ui.RESET} {ui.GRIS}|{ui.RESET}")
    print(f"  {ui.GRIS}+----+--------------------+-----------+--------------+--------------------+{ui.RESET}")
    for idx, r in enumerate(resultados, 1):
        pasa = r["distancia"] <= UMBRAL_DISTANCIA
        color_est = ui.VERDE if pasa else ui.ROJO
        estado = "SÍ (seleccionada)" if pasa else "NO (descartada)"
        print(
            f"  {ui.GRIS}|{ui.RESET} {idx:>2} {ui.GRIS}|{ui.RESET} {r['destino']:<18} {ui.GRIS}|{ui.RESET} "
            f"{len(r['destino']):>9} {ui.GRIS}|{ui.RESET} {color_est}{ui.NEGRITA}{r['distancia']:>12}{ui.RESET} {ui.GRIS}|{ui.RESET} "
            f"{color_est}{estado:<18}{ui.RESET} {ui.GRIS}|{ui.RESET}"
        )
    print(f"  {ui.GRIS}+----+--------------------+-----------+--------------+--------------------+{ui.RESET}")

    if palabra_origen.lower() == PALABRA_OBJETIVO_DEFECTO.lower():
        d_norm = calcular_distancia_rapida(palabra_origen, "programador", True)
        d_exact = calcular_distancia_rapida(palabra_origen, "programador", False)
        print(f"  {ui.CYAN}* Referencia sobre tildes en \"programador\": sin tildes = {d_norm} | con tildes = {d_exact}.{ui.RESET}")

    # =========================================================================
    # INCISO B: Seleccionar las palabras con distancia <= 3
    # =========================================================================
    filtradas = [(idx, r) for idx, r in enumerate(resultados) if r["distancia"] <= UMBRAL_DISTANCIA]
    _imprimir_separador_inciso("B", f"Seleccionar las palabras con distancia <= {UMBRAL_DISTANCIA}")
    if not filtradas:
        print(f"    {ui.ROJO}No se encontraron palabras con distancia <= {UMBRAL_DISTANCIA}.{ui.RESET}")
    else:
        for _, r in filtradas:
            print(f"    - {ui.VERDE}{r['destino']}{ui.RESET} (distancia = {ui.NEGRITA}{r['distancia']}{ui.RESET})")

    # =========================================================================
    # INCISO C: Ordenarlas por distancia
    # =========================================================================
    seleccionadas = [
        r for _, r in sorted(filtradas, key=lambda par: (par[1]["distancia"], par[0]))
    ]
    _imprimir_separador_inciso("C", "Ordenar las palabras seleccionadas por distancia (ascendente)")
    if not seleccionadas:
        print(f"    {ui.ROJO}(Sin elementos para ordenar){ui.RESET}")
    else:
        for pos, r in enumerate(seleccionadas, 1):
            print(f"    {pos}. {ui.VERDE}{r['destino']}{ui.RESET} (distancia = {ui.NEGRITA}{r['distancia']}{ui.RESET})")

    # =========================================================================
    # INCISO D: Simular la salida del corrector
    # =========================================================================
    _imprimir_separador_inciso("D", "Simular la salida del corrector ortográfico")
    print(f"  {ui.VERDE}+--------------------------------------------------+ {ui.RESET}")
    if existe:
        print(f"  {ui.VERDE}| La palabra \"{palabra_origen}\" está escrita correctamente.{ui.RESET}")
    elif not seleccionadas:
        print(f"  {ui.ROJO}| No se encontraron sugerencias para \"{palabra_origen}\".{ui.RESET}")
    else:
        print(f"  {ui.VERDE}|{ui.RESET} Palabra ingresada: {ui.AMARILLO}\"{palabra_origen}\"{ui.RESET}")
        print(f"  {ui.VERDE}|{ui.RESET} {ui.BLANCO}{ui.NEGRITA}¿Quisiste decir?{ui.RESET}")
        for idx, r in enumerate(seleccionadas, 1):
            print(f"  {ui.VERDE}|{ui.RESET}     {ui.VERDE}{ui.NEGRITA}{idx}. {r['destino']} (distancia = {r['distancia']}){ui.RESET}")
    print(f"  {ui.VERDE}+--------------------------------------------------+ {ui.RESET}")

    # =========================================================================
    # INCISOS E, F, G, H e I: Detalle completo por palabra (1 palabra por pantalla)
    # =========================================================================
    if mostrar_todas_matrices:
        if ui.pausa_seccion("Matrices y operaciones (Incisos E - I, palabra por palabra)", permitir_saltar=True):
            return

        for idx, r in enumerate(resultados, 1):
            ui.imprimir_banner(
                f"INCISOS E, F, G, H e I — PALABRA {idx} DE {len(resultados)}",
                f"Transformación: \"{r['origen']}\"  -->  \"{r['destino']}\"",
                ui.MAGENTA,
            )
            imprimir_detalle_completo(r, idx, mostrar_traza_celdas=False)
            if idx < len(resultados):
                sig = resultados[idx]["destino"]
                if ui.pausa_seccion(f"Palabra {idx + 1}/{len(resultados)}: '{sig}'", permitir_saltar=True):
                    break

        print(f"\n{ui.VERDE}{ui.NEGRITA}  [OK] Recorrido completo de los Incisos A hasta I finalizado.{ui.RESET}")


def _inspeccionar_una_palabra():
    print(f"\n  {ui.CYAN}Seleccione la palabra del diccionario a inspeccionar:{ui.RESET}")
    for idx, p in enumerate(DICCIONARIO_DEFECTO, 1):
        print(f"    {ui.VERDE}{idx}){ui.RESET} {p}")
    sel = input(f"  {ui.AMARILLO}Número [1-{len(DICCIONARIO_DEFECTO)}]: {ui.RESET}").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(DICCIONARIO_DEFECTO)):
        print(f"  {ui.ROJO}[!] Selección inválida.{ui.RESET}")
        return
    idx = int(sel)
    traza = (
        input(f"  {ui.AMARILLO}¿Mostrar también la tabla celda por celda (Inserción/Eliminación/Sustitución)? [s/n]: {ui.RESET}")
        .strip()
        .lower()
        == "s"
    )
    res = calcular_levenshtein(PALABRA_OBJETIVO_DEFECTO, DICCIONARIO_DEFECTO[idx - 1], _ignorar_tildes)
    ui.limpiar_pantalla()
    imprimir_detalle_completo(res, idx, mostrar_traza_celdas=traza)


def _probar_otra_palabra():
    ui.imprimir_banner("PUNTO 1 — PROBAR CORRECTOR CON OTRA PALABRA", None, ui.CYAN)
    palabra = input(f"  {ui.AMARILLO}Ingrese la palabra a corregir: {ui.RESET}").strip()
    if not palabra:
        print(f"  {ui.ROJO}[!] No se ingresó ninguna palabra.{ui.RESET}")
        return
    ver_mat = (
        input(f"  {ui.AMARILLO}¿Mostrar las matrices completas para las {len(DICCIONARIO_DEFECTO)} palabras? [s/n]: {ui.RESET}")
        .strip()
        .lower()
        == "s"
    )
    ui.limpiar_pantalla()
    ejecutar_resolucion_completa(palabra, DICCIONARIO_DEFECTO, ver_mat, _ignorar_tildes)


def _probar_bktree():
    ui.imprimir_banner("BÚSQUEDA OPTIMIZADA CON BK-TREE (UNIDAD 7 - DIAPOSITIVA 36)", None, ui.MAGENTA)
    arbol = BKTree(_ignorar_tildes)
    for p in DICCIONARIO_DEFECTO:
        arbol.insertar(p)

    print(f"\n  {ui.CYAN}Estructura del BK-Tree construido con el diccionario:{ui.RESET}\n")
    arbol.imprimir()
    print()

    consulta = input(f"  {ui.AMARILLO}Palabra a buscar [Enter para \"{PALABRA_OBJETIVO_DEFECTO}\"]: {ui.RESET}").strip()
    if not consulta:
        consulta = PALABRA_OBJETIVO_DEFECTO

    sugerencias, visitados = arbol.buscar(consulta, UMBRAL_DISTANCIA)
    print(f"\n  {ui.CYAN}Resultados con tolerancia <= {UMBRAL_DISTANCIA}:{ui.RESET}")
    print(f"    - Nodos visitados en BK-Tree   : {ui.VERDE}{ui.NEGRITA}{visitados}{ui.RESET} de {len(DICCIONARIO_DEFECTO)}")
    print(f"    - Comparaciones búsqueda lineal: {len(DICCIONARIO_DEFECTO)}")
    print(f"\n  {ui.BLANCO}{ui.NEGRITA}¿Quisiste decir?{ui.RESET}")
    if not sugerencias:
        print(f"    {ui.ROJO}(Sin sugerencias con distancia <= {UMBRAL_DISTANCIA}){ui.RESET}")
    else:
        for idx, (pal, dist) in enumerate(sugerencias, 1):
            print(f"      {ui.VERDE}{idx}. {pal} (distancia = {dist}){ui.RESET}")


def mostrar_submenu_punto1():
    global _ignorar_tildes
    while True:
        ui.limpiar_pantalla()
        ui.imprimir_banner("PUNTO 1: CORRECTOR ORTOGRÁFICO (DISTANCIA DE LEVENSHTEIN - PD)", None, ui.CYAN)
        print(f"  Palabra objetivo : {ui.AMARILLO}{ui.NEGRITA}\"{PALABRA_OBJETIVO_DEFECTO}\"{ui.RESET}")
        print(f"  Diccionario ({len(DICCIONARIO_DEFECTO)})  : {', '.join(DICCIONARIO_DEFECTO)}")
        print(f"  Umbral           : {ui.VERDE}distancia <= {UMBRAL_DISTANCIA}{ui.RESET}")
        modo_txt = (
            "SIN distinguir tildes (ó = o)  -> 'programador' da distancia = 3"
            if _ignorar_tildes
            else "DISTINGUIENDO tildes (ó != o)  -> 'programador' da distancia = 4"
        )
        print(f"  Modo actual      : {ui.CYAN}{ui.NEGRITA}{modo_txt}{ui.RESET}")

        # Cartel informativo sobre la diferencia al distinguir o no tildes
        print(f"\n{ui.AMARILLO}  +" + "-" * 74 + "+")
        print(f"  | {ui.NEGRITA}[!] AVISO — COMPARACIÓN CON TILDES VS. SIN TILDES:{ui.RESET}{ui.AMARILLO}                       |")
        print("  | Distinguir o no las tildes cambia el resultado de 'programador':         |")
        print("  |   * SIN distinguir tildes (ó = o): distancia = 3 (entra en <= 3,         |")
        print("  |     coincide con el ejemplo impreso en la hoja del parcial).             |")
        print("  |   * DISTINGUIENDO tildes (ó != o): distancia = 4 (cuenta ó -> o como     |")
        print("  |     1 sustitución extra y queda descartada del filtro <= 3).             |")
        print("  | Podés alternar entre ambos modos en cualquier momento con la opción e).  |")
        print("  +" + "-" * 74 + f"+{ui.RESET}")

        print(f"\n{ui.GRIS}" + "-" * 78 + ui.RESET)
        print(f"    {ui.VERDE}a){ui.RESET} Ejecutar resolución COMPLETA (Incisos A - I para todas las palabras)")
        print(f"    {ui.VERDE}b){ui.RESET} Inspeccionar en detalle UNA palabra (incluye tabla de relleno F)")
        print(f"    {ui.VERDE}c){ui.RESET} Probar el corrector con OTRA palabra ingresada por teclado")
        print(f"    {ui.MAGENTA}d){ui.RESET} Probar búsqueda optimizada con BK-Tree (Unidad 7 - Diap. 36)")
        print(f"    {ui.CYAN}e){ui.RESET} Cambiar modo de tildes (Normalizado ó = o  <->  Exacto ó != o)")
        print(f"    {ui.ROJO}v){ui.RESET} Volver al menú principal")
        print(f"{ui.CYAN}" + "=" * 78 + ui.RESET)

        op = input(f"  {ui.AMARILLO}Seleccione una opción [a-e / v para volver]: {ui.RESET}").strip().lower()
        if op == "a":
            ui.limpiar_pantalla()
            ejecutar_resolucion_completa(PALABRA_OBJETIVO_DEFECTO, DICCIONARIO_DEFECTO, True, _ignorar_tildes)
        elif op == "b":
            ui.limpiar_pantalla()
            _inspeccionar_una_palabra()
        elif op == "c":
            ui.limpiar_pantalla()
            _probar_otra_palabra()
        elif op == "d":
            ui.limpiar_pantalla()
            _probar_bktree()
        elif op == "e":
            _ignorar_tildes = not _ignorar_tildes
            continue
        elif op in ("v", "0", "volver", "s"):
            return
        else:
            print(f"\n  {ui.ROJO}[!] Opción '{op}' no válida. Intente nuevamente.{ui.RESET}")

        input(f"\n  {ui.GRIS}Presione ENTER para volver al menú del Punto 1...{ui.RESET}")

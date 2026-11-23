@echo off
chcp 65001 >nul
title UNViMe - Analisis y Diseno de Algoritmos - Examen 2 - Practica
cd /d "%~dp0"
if exist "C:\Users\julio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "C:\Users\julio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" examen2_ayda.py
) else (
    python examen2_ayda.py
)
pause

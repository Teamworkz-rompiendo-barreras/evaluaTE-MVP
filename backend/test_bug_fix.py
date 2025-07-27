#!/usr/bin/env python3
"""
Script para probar que el bug de logs de juegos y CV está solucionado
"""

import os
import json
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_report import generar_informe

def test_bug_fix():
    """
    Prueba que el informe no mencione limitaciones de datos
    """
    print("🔧 PRUEBA DE SOLUCIÓN DEL BUG")
    print("=" * 50)
    
    # Crear un perfil con datos mínimos (simulando el caso problemático)
    perfil_minimo = """
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: Usuario de Prueba
- ID: test_user_123

HABILIDADES SOFT EVALUADAS:
- Comunicación: 85% (Nivel: alto, Confianza: 90%)
- Trabajo en equipo: 78% (Nivel: medio, Confianza: 85%)
- Resolución de problemas: 92% (Nivel: alto, Confianza: 95%)

ANÁLISIS DETALLADO DEL CV:
El candidato no ha proporcionado un CV para análisis. Se realizará la evaluación basada en las habilidades soft evaluadas y preferencias laborales.

PREFERENCIAS LABORALES:
El candidato no ha especificado preferencias laborales detalladas. Se realizará la evaluación basada en las habilidades soft evaluadas.

JUEGOS COMPLETADOS:
El candidato no ha completado juegos de evaluación. La evaluación se basa en las habilidades soft proporcionadas.

LOGS DE JUEGOS:
No se dispone de logs detallados de juegos. La evaluación se basa en los resultados de habilidades soft proporcionados.
"""
    
    print("📝 Perfil de prueba creado (con datos mínimos)")
    print()
    
    try:
        print("🤖 Generando informe con datos mínimos...")
        print("⏳ Esto puede tomar varios minutos...")
        
        informe = generar_informe(perfil_minimo)
        
        print("✅ Informe generado exitosamente!")
        print()
        
        # Verificar que el informe NO contenga frases problemáticas
        frases_problematicas = [
            "ausencia de logs de juegos",
            "falta de un análisis completo de su CV",
            "no puede acceder a los log",
            "no puede acceder al CV",
            "representan una barrera",
            "No se proporcionó análisis de CV",
            "No hay logs de juegos disponibles",
            "Ningún juego completado"
        ]
        
        print("🔍 Verificando que el informe NO contenga frases problemáticas...")
        print()
        
        frases_encontradas = []
        for frase in frases_problematicas:
            if frase.lower() in informe.lower():
                frases_encontradas.append(frase)
        
        if frases_encontradas:
            print("❌ PROBLEMA: Se encontraron frases problemáticas en el informe:")
            for frase in frases_encontradas:
                print(f"   • '{frase}'")
            print()
            print("🔧 El bug NO está completamente solucionado")
            return False
        else:
            print("✅ ÉXITO: No se encontraron frases problemáticas en el informe")
            print()
        
        # Verificar que el informe sea profesional y completo
        palabras = len(informe.split())
        lineas = len(informe.split('\n'))
        
        print("📊 Análisis del informe generado:")
        print(f"   • Palabras: {palabras:,}")
        print(f"   • Líneas: {lineas:,}")
        print(f"   • Caracteres: {len(informe):,}")
        print()
        
        # Verificar que contenga secciones importantes
        secciones_importantes = [
            "resumen ejecutivo",
            "análisis",
            "recomendaciones",
            "conclusiones"
        ]
        
        secciones_encontradas = []
        for seccion in secciones_importantes:
            if seccion.lower() in informe.lower():
                secciones_encontradas.append(seccion)
        
        print("📋 Secciones importantes encontradas:")
        for seccion in secciones_encontradas:
            print(f"   ✅ {seccion.title()}")
        
        if len(secciones_encontradas) >= 2:
            print()
            print("✅ El informe contiene las secciones necesarias")
        else:
            print()
            print("⚠️ El informe podría necesitar más secciones")
        
        # Guardar el informe para revisión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        informe_filename = f"test_bug_fix_{timestamp}.md"
        
        with open(informe_filename, 'w', encoding='utf-8') as f:
            f.write(f"# PRUEBA DE SOLUCIÓN DEL BUG\n\n")
            f.write(f"**Fecha de prueba:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"**Objetivo:** Verificar que el informe no mencione limitaciones de datos\n\n")
            f.write("---\n\n")
            f.write(informe)
        
        print(f"💾 Informe guardado como: {informe_filename}")
        print()
        
        # Mostrar vista previa del informe
        print("📖 Vista previa del informe (primeras 10 líneas):")
        print("-" * 50)
        lineas_preview = informe.split('\n')[:10]
        for linea in lineas_preview:
            print(linea)
        
        if len(informe.split('\n')) > 10:
            print("...")
        
        print()
        print("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        print("✅ El bug está solucionado - el informe es profesional y no menciona limitaciones de datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bug_fix()
    if success:
        print("\n✅ RESULTADO: Bug solucionado correctamente")
    else:
        print("\n❌ RESULTADO: Bug aún presente") 
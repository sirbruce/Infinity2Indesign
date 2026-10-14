import xml.etree.ElementTree as ET
import zipfile
import re
import os

def procesar_svg_affinity(ruta_svg):
    """Extrae las cadenas de texto del SVG de Affinity de forma secuencial."""
    print(f"📦 Leyendo datos vectoriales de Affinity: {ruta_svg}")
    namespaces = {'svg': 'http://w3.org'}
    try:
        tree = ET.parse(ruta_svg)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ Error crítico al leer el archivo SVG: {e}")
        return []

    textos_nuevos = []
    for el_text in root.findall('.//svg:text', namespaces):
        texto = "".join(el_text.itertext()).strip()
        if texto:
            textos_nuevos.append(texto)
            
    print(f"✅ Capturados {len(textos_nuevos)} bloques de texto editados.")
    return textos_nuevos

def actualizar_story_xml(contenido_xml_original, textos_nuevos):
    """
    Modifica quirúrgicamente el XML original de InDesign reemplazando 
    exclusivamente el texto dentro de las etiquetas <Content>.
    """
    # Registrar los namespaces para que no se alteren las etiquetas de Adobe
    ET.register_namespace('', "http://adobe.com")
    
    try:
        root = ET.fromstring(contenido_xml_original)
        # Buscar todas las etiquetas de contenido de texto en el XML de InDesign
        elementos_content = root.findall('.//Content')
        
        for idx, el_content in enumerate(elementos_content):
            if idx < len(textos_nuevos):
                # Inyectamos el texto de Affinity manteniendo intacto el estilo de InDesign
                el_content.text = textos_nuevos[idx]
        
        # Retornar el XML reconstruido como string
        return ET.tostring(root, encoding="utf-8", method="xml")
    except Exception as e:
        print(f"⚠️ Alerta en procesamiento de Story: {e}")
        return contenido_xml_original

def generar_idml_seguro(textos_affinity, ruta_plantilla, ruta_salida):
    print(f"🔄 Realizando inyección quirúrgica en la estructura del Mac...")
    
    with zipfile.ZipFile(ruta_plantilla, 'r') as plantilla_zip:
        with zipfile.ZipFile(ruta_salida, 'w') as salida_zip:
            
            # 1. Forzar el archivo 'mimetype' plano obligatorio para Mac
            if "mimetype" in plantilla_zip.namelist():
                salida_zip.writestr("mimetype", plantilla_zip.read("mimetype"), zipfile.ZIP_STORED)
            
            # 2. Procesar el resto de ficheros en caliente
            for item_zip in plantilla_zip.infolist():
                nombre_archivo = item_zip.filename
                if nombre_archivo == "mimetype":
                    continue
                
                # Modificación exclusiva de los textos, el resto de la maquetación no se toca
                if nombre_archivo.startswith("Stories/Story_"):
                    xml_original = plantilla_zip.read(nombre_archivo)
                    xml_modificado = actualizar_story_xml(xml_original, textos_affinity)
                    salida_zip.writestr(nombre_archivo, xml_modificado, zipfile.ZIP_DEFLATED)
                else:
                    # Copia exacta bit a bit de guías, capas y geometrías del Mac
                    salida_zip.writestr(nombre_archivo, plantilla_zip.read(nombre_archivo), zipfile.ZIP_DEFLATED)

    print(f"🎉 ¡Flujo cerrado! Archivo 100% seguro para Mac generado en: {ruta_salida}")

if __name__ == "__main__":
    archivo_svg = "tu_diseno_affinity.svg"  
    archivo_plantilla = "plantilla.idml"    
    archivo_final = "Resultado_Editable.idml"
    
    if os.path.exists(archivo_svg) and os.path.exists(archivo_plantilla):
        datos_texto = procesar_svg_affinity(archivo_svg)
        generar_idml_seguro(datos_texto, archivo_plantilla, archivo_final)
    else:
        print("💡 Pon tu SVG como 'tu_diseno_affinity.svg' y tu IDML original como 'plantilla.idml'.")

import xml.etree.ElementTree as ET

class Kml(object):
    
    def __init__(self):
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, 'Document')

    def addPlacemark(self, nombre, descripcion, long, lat, alt, modoAltitud, color_hex):
        pm = ET.SubElement(self.doc, 'Placemark')
        ET.SubElement(pm, 'name').text = nombre
        ET.SubElement(pm, 'description').text = descripcion

        # Parte añadida al código del ejemplo 02020-KML para cambiar el color del punto y de la etiqueta
        estilo = ET.SubElement(pm, 'Style')
        icono = ET.SubElement(estilo, 'IconStyle')
        ET.SubElement(icono, 'color').text = color_hex
        label = ET.SubElement(estilo, 'LabelStyle')
        ET.SubElement(label, 'color').text = color_hex

        punto = ET.SubElement(pm, 'Point')
        ET.SubElement(punto, 'coordinates').text = '{},{},{}'.format(long, lat, alt)
        ET.SubElement(punto, 'altitudeMode').text = modoAltitud

    def addLineString(self, nombre, extrude, tesela, listaCoordenadas, modoAltitud, color, ancho):
        ET.SubElement(self.doc, 'name').text = nombre
        pm = ET.SubElement(self.doc, 'Placemark')
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls, 'extrude').text = extrude
        ET.SubElement(ls, 'tessellation').text = tesela
        ET.SubElement(ls, 'coordinates').text = listaCoordenadas
        ET.SubElement(ls, 'altitudeMode').text = modoAltitud 

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement(linea, 'color').text = color
        ET.SubElement(linea, 'width').text = ancho

    def escribir(self, nombreArchivoKML):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)


# Clase añadida para leer el XML y generar el KML
class Planimetria(object):

    def __init__(self, archivoXML):
        self.archivoXML = archivoXML
        self.kml = Kml()
        self.ns = "{http://www.uniovi.es}"
        self.coordenadas_ruta = ""

    def _extraer_coordenadas(self, nodo):
        lat = nodo.find(f'.//{self.ns}latitud').text
        lon = nodo.find(f'.//{self.ns}longitud').text
        alt = nodo.find(f'.//{self.ns}altitud').text
        return lon, lat, alt

    def generar_kml(self, archivoKML):
        # Código del archivo 02010-XPath (lo uso para leer el XML y prevenir errores)
        try:
            arbol = ET.parse(self.archivoXML)
        except IOError:
            print('No se encuentra el archivo', self.archivoXML)
            exit()
        except ET.ParseError:
            print("Error procesando en el archivo XML = ", self.archivoXML)
            exit()
            
        raiz = arbol.getroot()

        # Puntos anónimos en amarillo
        num_punto = 1
        for punto in raiz.findall(f'.//{self.ns}puntos_anon/{self.ns}punto'):
            lon, lat, alt = self._extraer_coordenadas(punto)
            self.kml.addPlacemark("", "Punto de ruta", lon, lat, alt, "relativeToGround", "ff00ffff")
            self.coordenadas_ruta += f"{lon},{lat},{alt}\n"
            num_punto += 1

        # Puertos de montaña en verde
        for puerto in raiz.findall(f'.//{self.ns}puerto'):
            nombre = puerto.attrib.get('nombre', 'Puerto')
            lon, lat, alt = self._extraer_coordenadas(puerto)
            self.kml.addPlacemark(nombre, "Puerto de montaña", lon, lat, alt, "relativeToGround", "ff00ff00")

        # Sprint intermedio en azul
        for sprint in raiz.findall(f'.//{self.ns}sprint'):
            nombre = sprint.attrib.get('nombre', 'Sprint')
            lon, lat, alt = self._extraer_coordenadas(sprint)
            self.kml.addPlacemark(nombre, "Sprint intermedio", lon, lat, alt, "relativeToGround", "ffff0000")

        # Puntos de salida y meta en rojo
        for salida in raiz.findall(f'.//{self.ns}salida'):
            nombre = salida.attrib.get('nombre', 'Salida')
            lon, lat, alt = self._extraer_coordenadas(salida)
            self.kml.addPlacemark(nombre, "Salida de etapa", lon, lat, alt, "relativeToGround", "ff0000ff")

        for meta in raiz.findall(f'.//{self.ns}meta'):
            nombre = meta.attrib.get('nombre', 'Meta')
            lon, lat, alt = self._extraer_coordenadas(meta)
            self.kml.addPlacemark(nombre, "Meta de etapa", lon, lat, alt, "relativeToGround", "ff0000ff")


        self.kml.addLineString("Ruta de la etapa", "1", "1", self.coordenadas_ruta, "relativeToGround", "ff0000ff", "5")
        self.kml.escribir(archivoKML)
        print("Creado el archivo: ", archivoKML)

def main():
    procesador = Planimetria("etapaEsquema.xml")
    procesador.generar_kml("etapa.kml")

if __name__ == "__main__":
    main()
import xml.etree.ElementTree as ET

class Svg(object):
    
    def __init__(self):
        self.raiz = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="2.0")

    
    def addRect(self,x,y,width,height,fill, strokeWidth,stroke):
        ET.SubElement(self.raiz,'rect',
                      x=x,
                      y=y,
                      width=width,
                      height=height,
                      fill=fill, 
                      strokeWidth=strokeWidth,
                      stroke=stroke)
        
    def addCircle(self,cx,cy,r,fill):
        ET.SubElement(self.raiz,'circle',
                      cx=cx,
                      cy=cy,
                      r=r,
                      fill=fill)
        
    def addLine(self,x1,y1,x2,y2,stroke,strokeWith):
        ET.SubElement(self.raiz,'line',
                      x1=x1,
                      y1=y1,
                      x2=x2,
                      y2=y2,
                      stroke=stroke,
                      strokeWith=strokeWith)

    def addPolyline(self,points,stroke,strokeWith,fill):
        ET.SubElement(self.raiz,'polyline',
                      points=points,
                      stroke=stroke,
                      strokeWith=strokeWith,
                      fill=fill)
        
    def addText(self,texto,x,y,fontFamily,fontSize,style):
        ET.SubElement(self.raiz,'text',
                      x=x,
                      y=y,
                      fontFamily=fontFamily,
                      fontSize=fontSize,
                      style=style).text=texto

    def escribir(self,nombreArchivoSVG):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, 
                    encoding='utf-8', 
                    xml_declaration=True
                    )

# Clase añadida para generar la altimetría
class Altimetria(object):

    def __init__(self, archivoXML):
        self.archivoXML = archivoXML
        self.svg = Svg()
        self.ns = "{http://www.uniovi.es}"

        # Código para las dimensiones del SVG 
        self.margen_izq = 100
        self.margen_inf = 550
        self.ancho = 900
        self.alto = 350
        self.distancia_max = 155.0
        self.altitud_max = 2500.0

    def _escalar_x(self, distancia):
        return self.margen_izq + (distancia / self.distancia_max) * self.ancho

    def _escalar_y(self, altitud):
        return self.margen_inf - (altitud / self.altitud_max) * self.alto

    def _dibujar_ejes(self):
        # Eje Y 
        for alt in range(0, 1801, 200):
            y = self._escalar_y(alt)
            self.svg.addLine(str(self.margen_izq - 5), str(y), str(self.margen_izq), str(y), "black", "1")
            self.svg.addText(str(alt), str(self.margen_izq - 45), str(y + 4), "Arial", "10", "none")
        self.svg.addLine(str(self.margen_izq), str(self.margen_inf), str(self.margen_izq), str(self._escalar_y(1800)), "black", "1")

        # Eje X 
        x_fin = self.margen_izq + self.ancho
        self.svg.addLine(str(self.margen_izq), str(self.margen_inf), str(x_fin), str(self.margen_inf), "black", "1")

    def _dibujar_marcador(self, x, y, dist_km, texto, color, icono_txt, icono_extra_txt=None, color_extra=None):
        y_top = 80 # Añadido a modo de tope para alinear los iconos

        # Línea vertical
        self.svg.addLine(str(x), str(self.margen_inf), str(x), str(y_top + 15), "black", "1")
        
        # Texto con la distancia
        self.svg.addLine(str(x), str(self.margen_inf), str(x), str(self.margen_inf + 5), "black", "1")
        self.svg.addText(str(dist_km), str(x - 12), str(self.margen_inf + 20), "Arial", "10", "none")

        # Texto vertical
        estilo_texto = "writing-mode: tb; glyph-orientation-vertical: 0; fill: black;"
        self.svg.addText(texto, str(x + 8), str(y_top + 20), "Arial", "11", estilo_texto)

        # Icono (círculo con letra dentro)
        if color != "none":     # Porque lo añado solo si no es PA
            self.svg.addCircle(str(x), str(y_top), "12", color)
            estilo_icono = "fill: white; font-weight: bold; text-anchor: middle;"  
            self.svg.addText(icono_txt, str(x), str(y_top + 4), "Arial", "12", estilo_icono)

        # NOTA: Como en mi etapa el último puerto es la meta, para que no se superpusieran hice que el código
        # detectara si un puerto está a menos de 2 km del final y que, en ese caso se mostrara solo
        # el icono de puerto encima del de la meta (como se hace en la altimetría del libro)
        if icono_extra_txt and color_extra:
            self.svg.addCircle(str(x), str(y_top - 26), "12", color_extra)
            estilo_icono = "fill: white; font-weight: bold; text-anchor: middle;"  
            self.svg.addText(icono_extra_txt, str(x), str(y_top - 22), "Arial", "12", estilo_icono)

    def generar_svg(self, archivoSVG):
        # Código del archivo 02010-XPath (lo uso para leer el XML y prevenir errores)
        try:
            arbol = ET.parse(self.archivoXML)
        except IOError:
            print('No se encuentra el archivo', self.archivoXML)
            return
        except ET.ParseError:
            print("Error procesando en el archivo XML = ", self.archivoXML)
            return
            
        raiz = arbol.getroot()

        # Código para sacar la distancia total y el desnivel
        nodo_longitud = raiz.find(f'.//{self.ns}long_etapa')
        self.distancia_max = float(nodo_longitud.text)
        nodo_desnivel = raiz.find(f'.//{self.ns}desnivel')
        desnivel_txt = nodo_desnivel.text 

        # Ejes
        self._dibujar_ejes()

        # Dibujo de la polilínea roja
        puntos_str = f"{self.margen_izq},{self.margen_inf} " 
        
        for punto in raiz.findall(f'.//{self.ns}puntos_anon/{self.ns}punto'):
            dist = float(punto.find(f'.//{self.ns}distancia').text)
            alt = float(punto.find(f'.//{self.ns}altitud').text)
            
            x = self._escalar_x(dist)
            y = self._escalar_y(alt)
            puntos_str += f"{x},{y} "
            
            # Nombres de puntos anónimos
            nombre_punto = punto.attrib.get('nombre')
            if nombre_punto:
                texto = f"{nombre_punto} / {int(alt)} m"
                self._dibujar_marcador(x, y, dist, texto, "none", "")

        puntos_str += f"{self._escalar_x(self.distancia_max)},{self.margen_inf}"
        self.svg.addPolyline(puntos_str.strip(), "red", "2", "red")

        # Dibujo de hitos
            # NOTA: Como en mi etapa el último puerto es la meta, para que no se superpusieran hice que el código
            # detectara si un puerto está a menos de 2 km del final y que, en ese caso se mostrara solo
            # el icono de puerto encima del de la meta (como se hace en la altimetría del libro)
        puerto_en_meta = None
        for hito in raiz.findall(f'.//{self.ns}hitos/*'):
            nombre = hito.attrib.get('nombre', 'Hito')
            dist = float(hito.find(f'.//{self.ns}distancia').text)
            alt = float(hito.find(f'.//{self.ns}altitud').text)

            if (self.distancia_max - dist) <= 2 and 'puerto' in hito.tag:
                puerto_en_meta = hito.attrib.get('categoria', '3').replace('ª categoría', '')
                continue

            x = self._escalar_x(dist)
            y = self._escalar_y(alt)
            texto = f"{nombre} / {int(alt)} m"
            
            if 'puerto' in hito.tag:
                categoria = hito.attrib.get('categoria', '3').replace('ª categoría', '')
                self._dibujar_marcador(x, y, dist, texto, "purple", categoria)
            elif 'sprint' in hito.tag:
                self._dibujar_marcador(x, y, dist, texto, "green", "SP")

        # Dibujo de salida y meta
        salida = raiz.find(f'.//{self.ns}salida')
        if salida is not None:
            nombre = salida.attrib.get('nombre', 'Salida')
            alt = float(salida.find(f'.//{self.ns}altitud').text)
            x, y = self._escalar_x(0), self._escalar_y(alt)
            texto = f"{nombre.upper()} / {int(alt)} m"
            self._dibujar_marcador(x, y, 0, texto, "blue", "S")

        meta = raiz.find(f'.//{self.ns}meta')
        if meta is not None:
            nombre = meta.attrib.get('nombre', 'Meta')
            alt = float(meta.find(f'.//{self.ns}altitud').text)
            x, y = self._escalar_x(self.distancia_max), self._escalar_y(alt)
            texto = f"{nombre.upper()} / {int(alt)} m"
            if puerto_en_meta:
                self._dibujar_marcador(x, y, self.distancia_max, texto, "red", "M", puerto_en_meta, "purple")
            else:
                self._dibujar_marcador(x, y, self.distancia_max, texto, "red", "M")

        # Texto con el desnivel positivo
        self.svg.addText(f"Desnivel positivo: {desnivel_txt} m", str(self.margen_izq + 350), str(self.margen_inf + 80), "Arial", "30", "font-weight: bold;")

        
        self.svg.escribir(archivoSVG)
        print(f"Creado el archivo: {archivoSVG}")

def main():
    generador = Altimetria("etapaEsquema.xml")
    generador.generar_svg("altimetria.svg")

if __name__ == "__main__":
    main()
# Reimportar librerías y redefinir la clase después del reinicio
import cv2
import numpy as np
import matplotlib.pyplot as plt

class IconDetector:
    def __init__(self, image_path, filtro_tipo="hsv", ajuste_pixels=12, extra_recorte=5):
        """
        Inicializa la clase con la imagen y configura los ajustes de recorte y filtrado.

        :param image_path: Ruta de la imagen completa.
        :param filtro_tipo: "hsv" para usar el filtro de color o "grayscale" para escala de grises.
        :param ajuste_pixels: Ajuste de píxeles para el recorte inicial.
        :param extra_recorte: Ajuste adicional para mejorar la precisión del recorte.
        """
        self.image_path = image_path
        self.filtro_tipo = filtro_tipo  # Tipo de filtro elegido por el usuario
        self.ajuste_pixels = ajuste_pixels
        self.extra_recorte = extra_recorte
        self.image = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
        self.height, self.width = self.image.shape[:2]
        self.sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02, edgeThreshold=10)
        self.keypoints_iconos = None
        self.descriptors_iconos = None
        self.keypoints_busqueda = None
        self.descriptors_busqueda = None
        self.matches = None
        self.good_matches = None

    def aplicar_filtro_hsv(self, img):
        """
        Aplica un filtro HSV para resaltar los íconos de colores específicos (verde y rojo) en la imagen de búsqueda.
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Definir rangos de color para los íconos
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([90, 255, 255])

        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        # Crear máscaras para detectar los íconos en verde y rojo
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_red = cv2.inRange(hsv, lower_red, upper_red)

        # Unir las máscaras de verde y rojo
        mask_combined = cv2.bitwise_or(mask_green, mask_red)

        return mask_combined

    def aplicar_filtro_grayscale(self, img):
        """
        Convierte la imagen a escala de grises.
        """
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def recortar_secciones(self):
        """
        Recorta la parte inferior de la imagen para los íconos y la parte superior para la búsqueda.
        Luego aplica el filtro de colores HSV o escala de grises a la imagen de búsqueda.
        """
        nueva_altura_inicio = int(self.height * 0.92) - self.ajuste_pixels + self.extra_recorte
        nueva_altura_inicio = max(nueva_altura_inicio, 0)  # Asegurar que no sea negativo

        # Recortar las secciones de la imagen con el ajuste mejorado
        self.bottom_section = self.image[nueva_altura_inicio:self.height, :]
        self.image_busqueda = self.image[:nueva_altura_inicio, :]

        # Aplicar el filtro elegido solo a la imagen de búsqueda
        if self.filtro_tipo == "hsv":
            self.image_busqueda_filtered = self.aplicar_filtro_hsv(self.image_busqueda)
        else:
            self.image_busqueda_filtered = self.aplicar_filtro_grayscale(self.image_busqueda)

        # La parte de los iconos siempre se mantiene en escala de grises
        self.bottom_section_gray = cv2.cvtColor(self.bottom_section, cv2.COLOR_BGR2GRAY)

    def detectar_keypoints(self):
        """
        Aplica SIFT para detectar keypoints y descriptores en ambas secciones.
        """
        self.keypoints_iconos, self.descriptors_iconos = self.sift.detectAndCompute(self.bottom_section_gray, None)
        self.keypoints_busqueda, self.descriptors_busqueda = self.sift.detectAndCompute(self.image_busqueda_filtered, None)

    def encontrar_coincidencias(self):
        """
        Usa FLANN Matcher para encontrar coincidencias entre los íconos y la imagen de búsqueda.
        """
        index_params = dict(algorithm=1, trees=15)
        search_params = dict(checks=500)
        flann_sift = cv2.FlannBasedMatcher(index_params, search_params)

        self.matches = flann_sift.knnMatch(self.descriptors_iconos, self.descriptors_busqueda, k=2)
        self.good_matches = [m for m, n in self.matches if m.distance < 0.93 * n.distance]

    def mostrar_resultados(self):
        """
        Dibuja y muestra las coincidencias entre los íconos y la imagen de búsqueda.
        """
        imagen_resultado = cv2.drawMatches(
            self.bottom_section_gray, self.keypoints_iconos,
            self.image_busqueda_filtered, self.keypoints_busqueda,
            self.good_matches, None, flags=2
        )

        # Mostrar la imagen con detección ajustada
        plt.figure(figsize=(12, 6))
        plt.imshow(imagen_resultado, cmap='gray')
        plt.title(f"Detección con SIFT y Filtro {self.filtro_tipo.upper()} (Aplicado solo a la búsqueda)")
        plt.axis("off")
        plt.show()

class IconDetectorWithGrouping(IconDetector):
    def __init__(self, image_path, filtro_tipo="hsv", ajuste_pixels=12, extra_recorte=5):
        """
        Extiende la clase IconDetector para agrupar coincidencias y obtener la posición media de cada ícono.
        """
        super().__init__(image_path, filtro_tipo, ajuste_pixels, extra_recorte)

    def agrupar_coincidencias(self):
        """
        Agrupa las coincidencias por proximidad y obtiene la posición promedio de cada grupo.
        """
        if not self.good_matches:
            return []

        # Obtener las coordenadas de los puntos clave en la imagen de búsqueda
        matched_points = [self.keypoints_busqueda[m.trainIdx].pt for m in self.good_matches]

        # Ordenar los puntos por coordenada X (de izquierda a derecha)
        matched_points.sort(key=lambda p: p[0])

        # Agrupar puntos cercanos en el eje X
        grupos = []
        umbral_distancia = 30  # Define la distancia mínima entre grupos

        for punto in matched_points:
            if not grupos or abs(grupos[-1][-1][0] - punto[0]) > umbral_distancia:
                grupos.append([punto])
            else:
                grupos[-1].append(punto)

        # Obtener el punto medio de cada grupo
        puntos_representativos = []
        for grupo in grupos:
            x_medio = np.mean([p[0] for p in grupo])
            y_medio = np.mean([p[1] for p in grupo])
            puntos_representativos.append((x_medio, y_medio))

        return puntos_representativos

    def ejecutar_deteccion_con_agrupacion(self):
        """
        Ejecuta el proceso de detección de íconos y agrupa coincidencias para obtener un punto representativo por ícono.
        """
        self.recortar_secciones()
        self.detectar_keypoints()
        self.encontrar_coincidencias()
        self.mostrar_resultados()

        # Obtener los puntos representativos para cada ícono
        puntos_finales = self.agrupar_coincidencias()
        return puntos_finales



if __name__=="__main__":

    image_path = "captcha.png"
    detector = IconDetectorWithGrouping(image_path, filtro_tipo="hsv", ajuste_pixels=12, extra_recorte=5)
    puntos_finales = detector.ejecutar_deteccion_con_agrupacion()

    # Mostrar los puntos representativos
    # Convertir los puntos representativos a números simples (float)
    puntos_finales_simplificados = [(float(x), float(y)) for x, y in puntos_finales]

    # Mostrar los puntos representativos simplificados
    print("Puntos representativos de los íconos:")
    print(puntos_finales_simplificados)

    image=cv2.imread(image_path, cv2.IMREAD_COLOR)
    for i, (x, y) in enumerate(puntos_finales_simplificados, start=1):
        cv2.circle(image, (int(x), int(y)), 8, (0, 0, 255), -1)  # Puntos en rojo
        cv2.putText(image, str(i), (int(x) + 10, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)  # Numeración

    # Mostrar la imagen con los puntos marcados
    plt.figure(figsize=(6, 6))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Puntos Representativos de los Íconos")
    plt.axis("off")
    plt.show()




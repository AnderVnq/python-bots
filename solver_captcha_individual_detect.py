import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

class IconDetector:
    def __init__(self, image_path, filtro_tipo="hsv", ajuste_pixels=12, extra_recorte=5, icon_size=30, spacing=10):
        self.image_path = image_path
        self.filtro_tipo = filtro_tipo  
        self.ajuste_pixels = ajuste_pixels
        self.extra_recorte = extra_recorte
        self.icon_size = icon_size  
        self.spacing = spacing  
        self.image = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
        self.height, self.width = self.image.shape[:2]
        self.sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02, edgeThreshold=10)
        self.iconos_recortados = []
        self.keypoints_iconos = []
        self.descriptors_iconos = []
        self.keypoints_busqueda = None
        self.descriptors_busqueda = None
        self.matches_por_icono = []
        self.puntos_coincidencia = []

    def aplicar_filtro_hsv(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([90, 255, 255])
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        return cv2.bitwise_or(mask_green, mask_red)

    def aplicar_filtro_grayscale(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def recortar_secciones(self):
        nueva_altura_inicio = int(self.height * 0.92) - self.ajuste_pixels + self.extra_recorte
        nueva_altura_inicio = max(nueva_altura_inicio, 0)

        self.bottom_section = self.image[nueva_altura_inicio:self.height, :]
        self.image_busqueda = self.image[:nueva_altura_inicio, :]

        if self.filtro_tipo == "hsv":
            self.image_busqueda_filtered = self.aplicar_filtro_hsv(self.image_busqueda)
        else:
            self.image_busqueda_filtered = self.aplicar_filtro_grayscale(self.image_busqueda)

        self.bottom_section_gray = cv2.cvtColor(self.bottom_section, cv2.COLOR_BGR2GRAY)

        num_iconos = (self.width // (self.icon_size + self.spacing))  

        for i in range(num_iconos):
            x_inicio = i * (self.icon_size + self.spacing)
            x_fin = x_inicio + self.icon_size
            if x_fin <= self.width:
                icono = self.bottom_section[:, x_inicio:x_fin]  
                icono_gray = self.aplicar_filtro_grayscale(icono)  # Convertir a escala de grises
                self.iconos_recortados.append((icono_gray, x_inicio))  

    def detectar_keypoints(self):
        self.keypoints_iconos = []
        self.descriptors_iconos = []

        for icono, _ in self.iconos_recortados:
            keypoints, descriptors = self.sift.detectAndCompute(icono, None)
            self.keypoints_iconos.append(keypoints)
            self.descriptors_iconos.append(descriptors)

        self.keypoints_busqueda, self.descriptors_busqueda = self.sift.detectAndCompute(self.image_busqueda_filtered, None)

    def encontrar_coincidencias(self):
        index_params = dict(algorithm=1, trees=15)
        search_params = dict(checks=500)
        flann_sift = cv2.FlannBasedMatcher(index_params, search_params)

        self.matches_por_icono = []
        self.puntos_coincidencia = []

        for descriptors in self.descriptors_iconos:
            if descriptors is not None and self.descriptors_busqueda is not None:
                matches = flann_sift.knnMatch(descriptors, self.descriptors_busqueda, k=2)
                good_matches = [m for m, n in matches if m.distance < 0.93 * n.distance]
                self.matches_por_icono.append(good_matches)

                puntos = [self.keypoints_busqueda[m.trainIdx].pt for m in good_matches]
                self.puntos_coincidencia.append(puntos)

    def encontrar_area_mas_densa(self, puntos):
        """
        Encuentra la región de 30x30 px con más coincidencias dentro del área.
        """
        if not puntos:
            return None

        tree = KDTree(puntos)
        mejor_punto = None
        max_densidad = 0

        for punto in puntos:
            vecinos = tree.query_ball_point(punto, 15)  # Radio de 15 px (30x30 es total)
            if len(vecinos) > max_densidad:
                max_densidad = len(vecinos)
                mejor_punto = punto

        return mejor_punto

    def mostrar_resultado_final(self):
        imagen_resultado = self.image.copy()
        puntos_finales_simplificados = []

        for i, (puntos, (icono, x_offset)) in enumerate(zip(self.puntos_coincidencia, self.iconos_recortados)):
            mejor_punto = self.encontrar_area_mas_densa(puntos)
            if mejor_punto:
                x_medio = int(mejor_punto[0])
                y_medio = int(mejor_punto[1])
                puntos_finales_simplificados.append((x_medio, y_medio))

                cv2.circle(imagen_resultado, (x_medio, y_medio), 8, (0, 0, 255), -1)
                cv2.putText(imagen_resultado, str(i + 1), (x_medio + 10, y_medio - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        print("Puntos representativos de los íconos en orden:")
        print(puntos_finales_simplificados)

        # plt.figure(figsize=(6, 6))
        # plt.imshow(cv2.cvtColor(imagen_resultado, cv2.COLOR_BGR2RGB))
        # plt.title("Puntos Representativos de los Íconos")
        # plt.axis("off")
        # plt.show()
        return puntos_finales_simplificados

    def mostrar_coincidencias_por_icono(self):
        for i, (keypoints_icono, good_matches, (icono, x_offset)) in enumerate(zip(self.keypoints_iconos, self.matches_por_icono, self.iconos_recortados)):
            if good_matches:
                pass
                imagen_resultado = cv2.drawMatches(
                    icono, keypoints_icono,
                    self.image_busqueda_filtered, self.keypoints_busqueda,
                    good_matches, None, flags=2
                )

                # plt.figure(figsize=(12, 6))
                # plt.imshow(imagen_resultado, cmap='gray')
                # plt.title(f"Coincidencias del Ícono {i + 1}")
                # plt.axis("off")
                # plt.show()


if __name__ == "__main__":
    image_path = "captcha3.png"
    detector = IconDetector(image_path, filtro_tipo="grey", ajuste_pixels=12, extra_recorte=5, icon_size=30, spacing=10)
    detector.recortar_secciones()
    detector.detectar_keypoints()
    detector.encontrar_coincidencias()
    detector.mostrar_coincidencias_por_icono()  
    puntos=detector.mostrar_resultado_final()  
    print(puntos)

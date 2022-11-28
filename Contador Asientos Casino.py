import cv2
import numpy as np
import math

def CalcularAsientosLibres(contorno, perimetro, numAsientosMesa):
    # Se eliminan los detalles menores de la imagen usando approxPolyDP con un epsilon de 10%
    epsilonGrande = 0.1*perimetro
    approxGrande = cv2.approxPolyDP(contorno, epsilonGrande, True)

    # Se dibuja un contorno verde
    cv2.imshow('Mesas', cv2.drawContours(
        frame, [approxGrande], -1, (0, 124, 0), 3, cv2.LINE_AA))

    # Se calcula el area libre del contorno de mesa entregado
    areaTotal = cv2.contourArea(approxGrande)
    areaOcupada = cv2.contourArea(contorno)
    if(areaTotal == 0):
        return 0
    return int(
        round(numAsientosMesa - ((areaOcupada / areaTotal)*numAsientosMesa)))


def main(args):

    # VARIABLES
    minPerimetro = args.minperimetro   # Min para que un cuadrilatero sea reconocido como mesa
    numAsientosMesa = args.asientos  # numero de asientos por cada mesa

    # ENTRADA VIDEO con buffer de 1 frame
    if (args.camera is not None and type(args.camera) is int and args.camera >= 0 ):
        nCamera = args.camera
    else:
        nCamera = 0
    cap = cv2.VideoCapture(nCamera)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        # Lectura de imagen
        ret, frame = cap.read()

        if ret == True:

            # ENCONTRANDO CONTORNOS DE LA IMAGEN
            # cambiar imagen de color a gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # volver la imagen gris a una binaria
            _, th = cv2.threshold(gray, 140, 240, cv2.THRESH_BINARY)

            # pasar de binaria a rgb para poder dibujarle colores encima
            frame = cv2.cvtColor(th, cv2.COLOR_BGRA2RGB)

            # encontrar los contornos de la imagen binaria
            contornos, hierarchy = cv2.findContours(
                th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # muestra la imagen binaria
            cv2.imshow('Binaria', th)

            # CONTANDO OBJETOS
            totalMesasVacias = 0
            totalMesasOcupadas = 0
            asientosLibres = 0

            for c in contornos:
                # el largo del perimetro correspondiente al contorno
                perimetro = cv2.arcLength(c, True)

                # el perimetro del contorno debe ser mayor al minimo definido
                if perimetro > minPerimetro:

                    # se define un epsilon pequeño para ver si la mesa esta ocupada, este epsilon pequeño toma en cuenta los detalles que deforman el contorno
                    approx = cv2.approxPolyDP(c, 0.02*perimetro, True)

                    # si la mesa esta vacia se obtienen 4 vertices
                    if len(approx) == 4:
                        cv2.imshow('Mesas', cv2.drawContours(
                            frame, [approx], -1, (255, 0, 0), 2, cv2.LINE_AA))
                        totalMesasVacias += 1
                        asientosLibres += numAsientosMesa

                    # si no esta vacia se obtienen más de 4 vertices
                    elif len(approx) > 4:
                        cv2.imshow('Mesas', cv2.drawContours(
                            frame, [approx], -1, (203, 244, 8), 2, cv2.LINE_AA))
                        totalMesasOcupadas += 1
                        asientosLibres += CalcularAsientosLibres(
                            c, perimetro, numAsientosMesa)

            # Se asignan a un string los contadores obtenidos
            mesasV = 'Mesas Vacias: ' + str(totalMesasVacias)
            mesasO = 'Mesas Ocupadas: ' + str(totalMesasOcupadas)

            nAsientosT = (totalMesasVacias + totalMesasOcupadas) * numAsientosMesa
            asientosT = 'Asientos totales: ' + str(nAsientosT)

            asientosL = 'Asientos Libres: ' + str(asientosLibres)
            asientosO = 'Asientos Ocupados: ' + str(nAsientosT-asientosLibres)

            # Se muestran los contadores en pantalla
            cv2.imshow('Conteo', cv2.putText(frame, mesasV, (10, 150),
                                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2))
            cv2.imshow('Conteo', cv2.putText(frame, mesasO, (10, 100),
                                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (203, 244, 8), 2))
            cv2.imshow('Conteo', cv2.putText(frame, asientosO, (250, 100),
                                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (21, 174, 127), 2))
            cv2.imshow('Conteo', cv2.putText(frame, asientosL, (250, 150),
                                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (21, 174, 127), 2))
            cv2.imshow('Conteo', cv2.putText(frame, asientosT, (250, 200),
                                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (21, 174, 127), 2))

            # Esc para salir
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

    # mostrar ultimo resultado del conteo
    print("Mesas vacias: " + str(totalMesasVacias))
    print("Mesas ocupadas: " + str(totalMesasOcupadas))
    print(str(asientosLibres) + " asientos libres de un total de " +
        str(nAsientosE)+" asientos existentes.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Contador de asientos topdown')
    parser.add_argument('-c','--camera', const=0, type=int, required=False, help='Numero de la camara a tomar como entrada')
    parser.add_argument('-mp','--minperimetro', const=200, type=int, required=False, help='Minimo de perimetro para que un cuadrilatero sea reconocido como mesa, default 200')
    parser.add_argument('-a','--asientos', const=4, type=int, required=False, help='Numero de asientos por mesa, default 4')
    args = parser.parse_args()
    
    main(args)

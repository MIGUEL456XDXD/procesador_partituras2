import json

from partituras.modelo.compositor import Compositor

from partituras.modelo.errores import (
    ArchivoNoEncontrado,
    ArchivoCorrupto,
)


class LectorPartituras:

    def __init__(self, ruta_archivo):

        self.ruta_archivo = ruta_archivo

    def cargar(self):

        try:

            with open(
                self.ruta_archivo,
                "r",
                encoding="utf-8"
            ) as archivo:

                datos = json.load(archivo)

            return datos["partituras"]

        except FileNotFoundError as e:

            raise ArchivoNoEncontrado(
                f"No se encontró: {self.ruta_archivo}"
            ) from e

        except json.JSONDecodeError as e:

            raise ArchivoCorrupto(
                f"JSON corrupto: {self.ruta_archivo}"
            ) from e

    def procesar_con(self, compositor: Compositor):

        partituras = self.cargar()

        def procesar(partitura):

            try:

                transformada = compositor.transformar(partitura)

                revertida = compositor.revertir(transformada)

                return {
                    "original": partitura,
                    "transformada": transformada,
                    "revertida": revertida,
                    "exito": True,
                    "errores": [],
                }

            except ExceptionGroup as eg:

                return {
                    "original": partitura,
                    "transformada": None,
                    "revertida": None,
                    "exito": False,
                    "errores": [
                        str(error)
                        for error in eg.exceptions
                    ],
                }

        return [
            procesar(partitura)
            for partitura in partituras
        ]
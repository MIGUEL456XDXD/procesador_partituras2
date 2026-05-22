from abc import ABC, abstractmethod

from partituras.modelo.errores import (
    ContieneNumero,
    ContieneCaracterInvalido,
    SinNotas,
    EspacioMultiple,
    EspacioBordes,
)

NOTAS = ["do", "re", "mi", "fa", "sol", "la", "si"]

FRECUENCIAS = {
    "do": 261,
    "re": 293,
    "mi": 329,
    "fa": 349,
    "sol": 392,
    "la": 440,
    "si": 493,
}


class ReglaTransformacion(ABC):

    def __init__(self, token):
        self.token = token

    @abstractmethod
    def transformar(self, partitura):
        pass

    @abstractmethod
    def revertir(self, partitura):
        pass

    @abstractmethod
    def partitura_valida(self, partitura):
        pass

    def encontrar_numeros_partitura(self, partitura):

        return [
            (i, c)
            for i, c in enumerate(partitura)
            if c.isdigit()
        ]

    def encontrar_caracteres_invalidos(self, partitura):

        return [
            (i, c)
            for i, c in enumerate(partitura)
            if ord(c) > 127
        ]


class ReglaTransposicion(ReglaTransformacion):

    def partitura_valida(self, partitura):

        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)

        if numeros:

            mensaje = ", ".join(
                [f"{c} en posición {i}" for i, c in numeros]
            )

            errores.append(
                ContieneNumero(mensaje)
            )

        caracteres = self.encontrar_caracteres_invalidos(partitura)

        if caracteres:

            mensaje = ", ".join(
                [f"{c} en posición {i}" for i, c in caracteres]
            )

            errores.append(
                ContieneCaracterInvalido(mensaje)
            )

        partitura = partitura.lower()

        tokens = partitura.split()

        permitidos = set(NOTAS + ["|", "-"])

        invalidos = [
            token
            for token in tokens
            if token not in permitidos
        ]

        if invalidos:

            errores.append(
                ContieneCaracterInvalido(
                    f"Tokens inválidos: {invalidos}"
                )
            )

        tiene_notas = any(
            token in NOTAS
            for token in tokens
        )

        if not tiene_notas:

            errores.append(
                SinNotas(
                    "La partitura no contiene notas"
                )
            )

        if errores:

            raise ExceptionGroup(
                "Errores de validación",
                errores
            )

    def transformar(self, partitura):

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        tokens = partitura.split()

        resultado = [
            self._transponer(token)
            if token in NOTAS
            else token
            for token in tokens
        ]

        return " ".join(resultado)

    def revertir(self, partitura):

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        tokens = partitura.split()

        resultado = [
            self._revertir(token)
            if token in NOTAS
            else token
            for token in tokens
        ]

        return " ".join(resultado)

    def _transponer(self, nota):

        indice = NOTAS.index(nota)

        nuevo = (indice + self.token) % len(NOTAS)

        return NOTAS[nuevo]

    def _revertir(self, nota):

        indice = NOTAS.index(nota)

        nuevo = (indice - self.token) % len(NOTAS)

        return NOTAS[nuevo]


class ReglaFrecuencia(ReglaTransformacion):

    def partitura_valida(self, partitura):

        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)

        if numeros:

            mensaje = ", ".join(
                [f"{c} en posición {i}" for i, c in numeros]
            )

            errores.append(
                ContieneNumero(mensaje)
            )

        caracteres = self.encontrar_caracteres_invalidos(partitura)

        if caracteres:

            mensaje = ", ".join(
                [f"{c} en posición {i}" for i, c in caracteres]
            )

            errores.append(
                ContieneCaracterInvalido(mensaje)
            )

        if partitura != partitura.strip():

            errores.append(
                EspacioBordes(
                    "Hay espacios al inicio o al final"
                )
            )

        if "  " in partitura:

            errores.append(
                EspacioMultiple(
                    "Hay múltiples espacios"
                )
            )

        partitura = partitura.lower()

        tokens = partitura.split()

        invalidos = [
            token
            for token in tokens
            if token not in NOTAS
        ]

        if invalidos:

            errores.append(
                ContieneCaracterInvalido(
                    f"Notas inválidas: {invalidos}"
                )
            )

        if not tokens:

            errores.append(
                SinNotas(
                    "La partitura está vacía"
                )
            )

        if errores:

            raise ExceptionGroup(
                "Errores de validación",
                errores
            )

    def transformar(self, partitura):

        self.partitura_valida(partitura)

        partitura = partitura.lower()

        tokens = partitura.split()

        resultado = [
            str(FRECUENCIAS[token] * self.token)
            for token in tokens
        ]

        return " ".join(resultado)

    def revertir(self, partitura):

        valores = partitura.split()

        frecuencias = [
            int(valor) // self.token
            for valor in valores
        ]

        resultado = []

        for frecuencia in frecuencias:

            for nota, valor in FRECUENCIAS.items():

                if frecuencia == valor:

                    resultado.append(nota)

        return " ".join(resultado)


class Compositor:

    def __init__(self, interprete):

        self.interprete = interprete

    def transformar(self, partitura):

        return self.interprete.transformar(partitura)

    def revertir(self, partitura):

        return self.interprete.revertir(partitura)
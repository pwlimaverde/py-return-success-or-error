"""API pública da feature Fibonacci.

O consumidor importa daqui — contrato do service, erros e a função de
registro — sem conhecer a estrutura interna de camadas.
"""

from features.fibonacci.domain.errors import EntradaInvalida, FibonacciError
from features.fibonacci.domain.services import FibonacciService
from features.fibonacci.register import add_fibonacci_feature

__all__ = [
    'EntradaInvalida',
    'FibonacciError',
    'FibonacciService',
    'add_fibonacci_feature',
]

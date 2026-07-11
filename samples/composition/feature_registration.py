"""Agregador fino de features.

Adicionar uma feature ao app = uma linha aqui. Cada feature expõe seu
``add_xxx_feature`` pela API pública do pacote (``features.xxx``).
"""

from composition.container import Container
from features.check_connection import add_check_connection_feature
from features.fibonacci import add_fibonacci_feature
from features.sales_report import add_sales_report_feature


def add_features(container: Container) -> Container:
    """Registra todas as features da aplicação."""
    add_check_connection_feature(container)
    add_fibonacci_feature(container)
    add_sales_report_feature(container)
    return container

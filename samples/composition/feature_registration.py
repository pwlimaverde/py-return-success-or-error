"""Agregador fino de features (≙ FeatureRegistration.cs).

Adicionar uma feature ao app = uma linha aqui.
"""

from composition.container import Container
from features.check_connection.register import add_check_connection_feature
from features.fibonacci.register import add_fibonacci_feature
from features.sales_report.register import add_sales_report_feature


def add_features(container: Container) -> Container:
    """Registra todas as features da aplicação."""
    add_check_connection_feature(container)
    add_fibonacci_feature(container)
    add_sales_report_feature(container)
    return container

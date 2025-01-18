from queue import Queue
from threading import Thread
from typing import TypeVar

from py_return_success_or_error.core.return_success_or_error import (
    ReturnSuccessOrError,
)
from py_return_success_or_error.interfaces.parameters_return_result import (
    ParametersReturnResult,
)

TypeUsecase = TypeVar('TypeUsecase')
TypeParameters = TypeVar('TypeParameters', bound=ParametersReturnResult)


class ThreadMixin():

    def __call__(self, params):
        # Implementação do método __call__
        pass  # pragma: no cover

    def runNewThread(
            self, parameters: TypeParameters
    ) -> ReturnSuccessOrError[TypeUsecase]:
        result_queue: Queue[ReturnSuccessOrError[TypeUsecase]] = Queue()

        def targetFunction(params):
            result = self(params)
            result_queue.put(result)

        thread = Thread(target=targetFunction, args=(parameters,))
        thread.start()
        thread.join()
        result = result_queue.get()
        return result

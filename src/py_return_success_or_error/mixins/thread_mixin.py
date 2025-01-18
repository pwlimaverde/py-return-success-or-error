from py_return_success_or_error.imports import (
    ParametersReturnResult,
    Queue,
    ReturnSuccessOrError,
    Thread,
    TypeVar,
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

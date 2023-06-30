import functools

def catch_exceptions(on_exception=None):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(self, *args, **kwargs):
            try:
                return job_func(self, *args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())

                if on_exception is not None:
                    on_exception(self)
        return wrapper
    return catch_exceptions_decorator
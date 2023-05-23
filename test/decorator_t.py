class T(object):
    def __init__(self):
        self.num = 1919810

    def decorator(self, commit: int=0):
        def foo(func):
            def bar(*args, **kwargs):
                if commit:
                    return self.num
                return func(*args, **kwargs)
            return bar
        return foo

    @staticmethod
    @decorator(T,commit=1)
    def printf(num):
        print(num)
        return num + 1


if __name__ == '__main__':
    T = T()
    T.printf(2333)

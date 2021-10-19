class SCacheton:
    """
    Static class for caching classes and vars by hashable arguments
    """
    cachetons = {}
    cachevars = {}

    @staticmethod
    def get(cls, *args, **kwargs):
        """
        Get class cached by args/kwargs
        If it does not exist, creates new with *args,**kwargs
        All cached data will be freed with cleanup()

        You must not to store Tensor in SCacheton, use per-device cache vars
        """
        cls_multitons = SCacheton.cachetons.get(cls, None)
        if cls_multitons is None:
            cls_multitons = SCacheton.cachetons[cls] = {}

        key = (args, tuple(kwargs.items()) )

        data = cls_multitons.get(key, None)
        if data is None:
            data = cls_multitons[key] = cls(*args, **kwargs)

        return data

    @staticmethod
    def set_var(key, value):
        """
        Set data cached by key
        All cached data will be freed with cleanup()

        You must not to store Tensor in SCacheton, use per-device cache vars
        """
        SCacheton.cachevars[key] = value

    @staticmethod
    def get_var(key):
        """
        Get data cached by key
        All cached data will be freed with cleanup()

        You must not to store Tensor in SCacheton, use per-device cache vars
        """
        return SCacheton.cachevars.get(key, None)

    @staticmethod
    def cleanup():
        """
        Free all cached objects
        """
        SCacheton.cachetons = {}
        SCacheton.cachevars = {}
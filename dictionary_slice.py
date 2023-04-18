import itertools

#class DictionarySlice:
class DictionarySlice:
    """A class to provide slicing functionality for dictionaries.

    Attributes:
        _dict (dict): The original dictionary that needs to be sliced.
        closed_interval (bool): If set to True, includes the last element in the slice.
    """

    def __init__(self, d_items: {}, closed_interval=False) -> None:
        """Initializes the DictionarySlice class with a given dictionary and closed_interval parameter.

        Args:
            d_items (dict): The dictionary to be sliced.
            closed_interval (bool, optional): If set to True, includes the last element in the slice.
                                             Defaults to False.
        """
        self._dict = d_items
        self.closed_interval = closed_interval

    def __len__(self) -> {}:
        """Returns the length of the sliced dictionary.

        Returns:
            int: Length of the sliced dictionary.
        """
        return len(self.dict_slice)

    def __getitem__(self, key: None) -> {}:
        """Returns a sliced dictionary based on the given key.

        Args:
            key (None, int, or slice): The key used to slice the dictionary.

        Returns:
            dict: The sliced dictionary.
        """
        if isinstance(key, type(None)):
            self.dict_slice = self._dict
        if isinstance(key, int):
            if key < 0:
                key = len(self._dict) + key
            keys_iter = itertools.islice(self._dict.keys(), key, key + 1)
            self.dict_slice = {f: self._dict[f] for f in keys_iter}
        if isinstance(key, slice):
            start = key.start
            stop = key.stop
            step = key.step
            keys_iter = itertools.islice(self._dict.keys(), start, stop, step)
            self.dict_slice = {f: self._dict[f] for f in keys_iter}
            if self.closed_interval is True:
                final_element = itertools.islice(self._dict.keys(), stop, stop + 1)
                self.dict_slice.update({f: self._dict[f] for f in final_element})
        return self.dict_slice

    def __enter__(self):
        """Allows the class to be used as a context manager.

        Returns:
            DictionarySlice: An instance of the DictionarySlice class.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handles the exit from the context manager.

        Args:
            exc_type (type, optional): The type of exception raised. Defaults to None.
            exc_val (BaseException, optional): The instance of the exception raised. Defaults to None.
            exc_tb (traceback, optional): A traceback object encapsulating the call stack. Defaults to None.
        """
        pass

if __name__ == "__main__":
    import pickle
    from time import perf_counter
    print("Executing z_scratch.py ...")
    ctrl_dict = {}
    with open("control.pickle", "rb") as f:
        ctrl_dict = pickle.load(f)
    ds_start = perf_counter()
    with DictionarySlice(ctrl_dict, closed_interval=True) as slicer:
        sweep_controls = slicer[45_123:46_369:3]
    ds_stop = perf_counter()
    print(f"Time to initialize sweep_controls from {len(ctrl_dict)} elements\
    in ctrl_dict = {round(ds_stop-ds_start, 6)} seconds")
    print(f'{len(sweep_controls) = }')

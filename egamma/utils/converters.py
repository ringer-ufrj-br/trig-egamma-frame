from tqdm import tqdm
from ringer.schema import Schema
from collections import OrderedDict


def npy_dict_to_tfrecord(
        data_array: dict[str, any],
        filepath: str,
        progressbar: bool = False) -> Schema:
    """
    Converts a numpy dictionary to a TFRecord file

    Parameters
    ----------
    data_array : dict[str, any]
        A dictionary containing arrays with the data
    filepath : str
        Where to save the file
    progressbar : bool, optional
        If a progress bar should be shown, by default False

    Returns
    -------
    Schema
        Data schema inferred from the numpy dictionary

    Examples
    --------
    ```python
    import numpy as np
    data = {
        "features": np.random.rand(100, 10),
        "target": np.random.randint(0, 2, 100)
    }
    schema = arr_to_tfrecord(data, "path/to/file.tfrecord")
    schema.to_json("path/to/schema.json")
    ```
    """
    import tensorflow as tf
    schema = Schema.from_numpy_dict(data_array)
    rows = len(data_array[list(data_array.keys())[0]])
    iterator = tqdm(range(rows)) if progressbar else range(rows)

    with tf.io.TFRecordWriter(filepath) as writer:
        for row in iterator:
            row_dict = OrderedDict()
            for key, value in data_array.items():
                row_dict[key] = value[row]
            example = schema.get_tf_example(row_dict)
            writer.write(example.SerializeToString())

    return schema

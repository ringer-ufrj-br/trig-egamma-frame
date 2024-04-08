import tensorflow as tf
from collections import UserDict
from typing import Any, Dict
import pandas as pd
import numpy as np
import json
import os


class Schema(UserDict):
    """
    Class that represents data schemas.
    It was made mainly to help with dealing with different schemas
    between different python packages.
    It is a mapping and inherits from collections.UserDict

    Attributes
    ----------
    data : Dict
        Data attribute from collections.UserDict
    """

    __BYTE_LIST_TYPES = ('string', 'bytes')
    __FLOAT_LIST_TYPES = ('float', 'double')
    __INT_LIST_TYPES = ('int', 'bool', 'uint')

    def __init__(self, schema: Dict[str, str] = {}):
        super().__init__(schema)

    def __repr__(self):
        repr_str = '{\n'
        for key, value in self.data.items():
            repr_str += f'{key}: {value}\n'
        repr_str += '}'
        return repr_str

    def _get_parsing_feature(self, type_str: str) -> tf.io.FixedLenFeature:
        if type_str in self.__BYTE_LIST_TYPES:
            return tf.io.FixedLenFeature([], tf.string)
        elif type_str in self.__FLOAT_LIST_TYPES:
            return tf.io.FixedLenFeature([], tf.float32)
        elif type_str in self.__INT_LIST_TYPES:
            return tf.io.FixedLenFeature([], tf.int64)
        else:
            raise TypeError(f'Type {type_str} is not supported')

    @property
    def tfrecord_parse_schema(self):
        parser_description = {
            field_name: self._get_parsing_feature(field_type)
            for (field_name, field_type) in self.data.items()
        }
        return parser_description

    @tfrecord_parse_schema.setter
    def tfrecord_parse_schema(self, value: Any):
        raise ValueError('Can\'t set tfrecord_parse_schema')

    def __get_feature(self, type_str: str, value: Any) -> tf.train.Feature:
        """
        Given a value and its type, returns the corresponding
        tensroflow.train.Feature object
        *Internal use only*

        Parameters
        ----------
        type_str : str
            One of the supported value types
        value : Any
            Feature value

        Returns
        -------
        tensorflow.train.Feature
            Built feature object

        Raises
        ------
        TypeError
            Raised if the given type_str is not supported
        """
        if type_str in self.__BYTE_LIST_TYPES:
            return tf.train.Feature(
                bytes_list=tf.train.BytesList(value=[value])
            )
        elif type_str in self.__FLOAT_LIST_TYPES:
            return tf.train.Feature(
                float_list=tf.train.FloatList(value=[value])
            )
        elif type_str in self.__INT_LIST_TYPES:
            return tf.train.Feature(
                int64_list=tf.train.Int64List(value=[value])
            )
        else:
            raise TypeError(f'Type {type_str} is not supported')

    def get_tf_example(self, data: Dict[str, Any]) -> tf.train.Example:
        """
        Returns a tensorflow.train.Example object containing the data
        given.

        Parameters
        ----------
        data : Dict[str, Any]
            Data to use to build the example
            (key, value) pairs are expected as (field_name, field_value)

        Returns
        -------
        tensorflow.train.Example
            Built example object
        """
        feature = {feature_name: self.__get_feature(
            feature_type, value=data[feature_name]
        ) for feature_name, feature_type in self.data.items()
        }
        example = tf.train.Example(features=tf.train.Features(feature=feature))
        return example

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        """
        Creates a Schema instance infering data types from pandas.DataFrame

        Parameters
        ----------
        df: pandas.DataFrame
            DataFrame to infer data

        Returns
        -------
        Schema
            Inferred Schema
        """
        dtypes = df.dtypes.astype(str).str.lower()
        dtypes[dtypes.str.startswith('int')] = 'int'
        dtypes[dtypes.str.startswith('uint')] = 'int'
        dtypes[dtypes.str.startswith('float')] = 'float'
        dtypes[dtypes.str.startswith('boolean')] = 'int'
        dtypes[dtypes.str.startswith('object')] = 'string'
        dtypes[dtypes.str.startswith('string')] = 'string'
        return cls(dtypes.to_dict())

    @classmethod
    def from_numpy_dict(cls, np_dict: Dict[str, np.ndarray]):
        """
        Creates a Schema instance infering data types from a numpy dictionary.
        A numpy dictionary is a dict where each key pair is a numpy array
        representing a column.
        This data type is specially useful when working with ROOT.RDataFrame

        Parameters
        ----------
        np_dict: Dict[str, np.ndarray]
            Dictionary containing the data

        Returns
        -------
        Schema
            Inferred Schema
        """
        dtypes = dict()
        for key, value in np_dict.items():
            if value.dtype.kind in ('i', 'u'):
                dtypes[key] = 'int'
            elif value.dtype.kind == 'f':
                dtypes[key] = 'float'
            elif value.dtype.kind == 'b':
                dtypes[key] = 'int'
            else:
                dtypes[key] = 'string'
        return cls(dtypes)

    @classmethod
    def from_json(cls, json_path: str):
        """
        Creates a Schema instance from a json string

        Parameters
        ----------
        json_path: str
            String containing the path to the json file

        Returns
        -------
        Schema
            Built Schema

        Example
        -------
        ```python
        schema = Schema.from_json('schema.json')
        ```
        """
        with open(json_path, 'r') as file:
            schema = json.load(file)
        return cls(schema)

    def to_json(self, json_path: str, exist_ok: bool = False) -> bool:
        """
        Saves the schema to a json file

        Parameters
        ----------
        json_path : str
            Where to save the schema
        exist_ok : bool, optional
            If file should be overwritten, by default False

        Returns
        -------
        bool
            Always True
        """
        if not exist_ok and os.path.exists(json_path):
            raise FileExistsError(f'File {json_path} already exists')
        with open(json_path, 'w') as file:
            json.dump(self.data, file, indent=4)
        return True

"""
Module to handle dataset files and directories
A dataset is a direcroty that is structured as follows:
```
dataset_dir
│
└── table1
    │
    └── filename.root
    └── filename2.root
    └── ...
└── table2
    │
    └── filename.root
    └── filename2.root
    └── ...
```
there could be multiple directories representing tables and all of them
are joinable thorugh the id column.
This is possible by exploting the AddFriend method from ROOT.
If both trees have the same id column, and their files are ordered equally,
they can be joined.
"""

import os
import ROOT
from typing import Iterable, List

from egamma.utils.root import get_tchain


def dump_dataset_rdf(
        dataset_dir: str,
        rdf: ROOT.RDataFrame,
        table_name: str,
        filename: str,
        column_list: Iterable[str] = None):
    """
    Dumps a RDataFrame to a ROOT file in a dataset_dir
    following the dataset file hierarchy rules.

    Parameters
    ----------
    dataset_dir : str
        Path to the dataset dir
    rdf : ROOT.RDataFrame
        RDF to save
    table_name : str
        Name of the table the dataframe represents
    filename : str
        Name of the file to save the rdf
    column_list : Iterable[str], optional
        Iterable of columns to save, by default saves all columns
    """
    options = ROOT.RDF.RSnapshotOptions()
    options.fCompressionLevel = 9
    output_dir = os.path.join(dataset_dir, table_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not filename.endswith(".root"):
        filename += ".root"
    df_path = os.path.join(
        output_dir, filename)
    if not column_list:
        column_list = rdf.GetColumnNames()
    else:
        column_list = list(column_list)
    rdf.Snapshot(
        table_name,
        df_path,
        column_list,
        options)


def dataset_rdf_exists(dataset_dir: str, table_name: str) -> bool:
    """
    Checks if the given table exists in the dataset_dir

    Parameters
    ----------
    dataset_dir : str
        Path to the dataset dir
    table_name : str
        Name of the table to check

    Returns
    -------
    bool
        True if the table exists, False otherwise
    """
    return os.path.exists(os.path.join(dataset_dir, table_name))


def get_dataset_rdf(
        dataset_dir: str,
        table_names: List[str]) -> ROOT.RDataFrame:
    base_table = table_names[0]
    base_table_path = os.path.join(dataset_dir, base_table)
    base_chain = get_tchain(base_table_path, base_table,
                            title=base_table, sorted=True)
    for extra_table in table_names[1:]:
        if not dataset_rdf_exists(dataset_dir, extra_table):
            raise ValueError(
                f"Table {extra_table} does not exist in {dataset_dir}"
            )
        table_path = os.path.join(dataset_dir, extra_table)
        extra_chain = get_tchain(table_path, extra_table,
                                 title=extra_table, sorted=True)
        base_chain.AddFriend(extra_chain)
    rdf = ROOT.RDataFrame(base_chain)
    return rdf

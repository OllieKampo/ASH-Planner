from ast import parse
import pandas
import glob
import argparse
import numpy
import xlsxwriter

parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-out", "--output_path", required=True, type=str)
args: argparse.Namespace = parser.parse_args()

## A dictionary of workbooks:
##  - Mapping: workbook name x worksheet name -> data frame
excel_workbooks: dict[str, dict[str, pandas.DataFrame]] = {}

for path in args.input_paths:
    ## https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#excelfile-class
    for excel_file_name in glob.glob(f"{path}/*.xlsx"):
        with pandas.ExcelFile(excel_file_name) as excel_file:
            excel_workbooks[excel_file_name] = pandas.read_excel(excel_file)

## Open a new output excel file to save the collated data to
## https://xlsxwriter.readthedocs.io/working_with_pandas.html
writer = pandas.ExcelWriter(args.output_path, engine="xlsxwriter") # pylint: disable=abstract-class-instantiated

workbook: xlsxwriter.Workbook = writer.book
worksheet = workbook.add_worksheet("Cat Plan Comparison")

## Get the aggregates for each problem and planning type
## Gather the files into sets which we want to compare between each other:
##      - Aggregates are generated seperately for each set,
##      - The problem and planning type are always used
for problem in cli_args.problems:
    for planning_type in cli_args.planning_type:
        pass

## Collate and compare the data
## https://pbpython.com/excel-file-combine.html
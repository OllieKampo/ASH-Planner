from collections import defaultdict
import os
from typing import Optional
import pandas
import glob
import argparse
import numpy
import xlsxwriter
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ranksums.html
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html#scipy.stats.mannwhitneyu
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html#scipy.stats.kruskal
from scipy.stats import ranksums, mannwhitneyu, kruskal

## Setup argument parser
parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-out", "--output_path", required=True, type=str)
parser.add_argument("-compare", "--compare_data_sets", nargs="+", type=str)
cli_args: argparse.Namespace = parser.parse_args()

## Gather the configurations we want to compare into tuples (each defines a unique set) which we want to compare between each other;
##      - Aggregates are generated seperately for each set,
##      - The problem and planning type are always used.
configuration_headers: list[str] = ["Problem", "Planning_Type", "Mode_Type"]

def extract_configuration(excel_file_name: str) -> Optional[list[str]]:
    raw_config: str = os.path.basename(excel_file_name).strip("ASH_Excel_").strip(".xlsx")
    problem: str = raw_config[:3]
    terms: list[str] = raw_config[3:].split("_")
    planning_type: str = terms[0]
    if terms[0] == "hcl":
        return (problem, planning_type)
    return (problem, planning_type, planning_mode)
    # if terms[1] != "offline":
    #     strategy = find_strategy()
    #     bound_type
    #     bounds = find_bounds()
    
    # mode = find_mode()
    # sgoal_ach_type
    # is_conc
    # preach_type
    # blend_direction
    # blend_type
    # blend_quantity
    # method
    
    return None

## A dictionary of data sets;
##  - Mapping: workbook name x worksheet name -> data frame
data_sets: dict[tuple[str, ...], dict[str, pandas.DataFrame]] = defaultdict(dict)

## Iterate over all directory paths and all excel files within them
for path in cli_args.input_paths:
    for excel_file_name in glob.glob(f"{path}/*.xlsx"):
        
        configuration = excel_file_name
        configuration: Optional[list[str]] = extract_configuration(excel_file_name)
        if configuration is None:
            continue
        
        ## Open each excel workbook and extract its data
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#excelfile-class
        print(f"Opening excel file {excel_file_name} :: Configuration {configuration}")
        with pandas.ExcelFile(excel_file_name, engine="openpyxl") as excel_file:
            ## Read globals and concatenated plans;
            ##      - Globals is not nicely formatted so some extra work is needed to extract it.
            data_sets[configuration].update(pandas.read_excel(excel_file, ["Globals"], usecols="A:Y"))
            data_sets[configuration].update(pandas.read_excel(excel_file, ["Cat Plans"]))

for configuration, data_set in data_sets.items():
    print(f"Extracting data for {configuration}")
    
    ## Get rid of old index data
    data_set["Globals"] = data_set["Globals"].drop(["Unnamed: 0", "RU"], axis="columns")
    
    ## Clean up the globals sheet
    null_rows: pandas.Series = data_set["Globals"].isnull().all(axis=1)
    null_rows_index: pandas.Int64Index = data_set["Globals"].index[null_rows]
    last_data_row: int = null_rows_index.values[0]
    data_set["Globals"] = data_set["Globals"][:last_data_row]
    
    ## Convert the data types to those pandas thinks is best
    data_set["Globals"] = data_set["Globals"].convert_dtypes()
    
    ## Some of the early classical planning files don't have the time score, so add it where necessary
    if "TI_SCORE" not in data_set["Globals"]:
        data_set["Globals"].insert(data_set["Globals"].columns.get_loc("AME_PA_SCORE") + 1,
                                   "TI_SCORE", data_set["Globals"]["HA_SCORE"])

## Open a new output excel file to save the collated data to
## https://xlsxwriter.readthedocs.io/working_with_pandas.html
writer = pandas.ExcelWriter(cli_args.output_path, engine="xlsxwriter") # pylint: disable=abstract-class-instantiated

workbook: xlsxwriter.Workbook = writer.book
# worksheet = workbook.add_worksheet("Globals Comparison")
# worksheet = workbook.add_worksheet("Cat Plan Comparison")

## Add a column to table for each comparison level
globals_: list[pandas.DataFrame] = []
# cat_plans: list[pandas.DataFrame] = []

## For each data set, add a row to the dataframe with column entries for each comparison level for that set
for configuration, data_set in data_sets.items():
    data_set_globals_quantiles: pandas.DataFrame = data_set["Globals"].quantile([0.0, 0.25, 0.50, 0.75, 1.0])
    data_set_globals_quantiles = data_set_globals_quantiles.append((data_set_globals_quantiles.loc[0.75] - data_set_globals_quantiles.loc[0.25]).rename("IQR"))
    data_set_globals_quantiles = data_set_globals_quantiles.append((data_set_globals_quantiles.loc[1.0] - data_set_globals_quantiles.loc[0.0]).rename("Range"))
    
    for index, level_name in enumerate(configuration_headers):
        data_set_globals_quantiles.insert(0, level_name, configuration[index])
        # data_set_cat_plans[level_name] = configuration[index]
    
    print(data_set_globals_quantiles)
    
    globals_.append(data_set_globals_quantiles)
    # cat_plans.append(data_set_cat_plans)

collated_globals: pandas.DataFrame = pandas.concat(globals_)

## Use IQR as the representation of the distribution, then use a non-parametric test like mann-whitney to evalute statistical significance, since we are not sure that it is gaussian/normal.
## https://www.simplypsychology.org/p-value.html#:~:text=A%20p%2Dvalue%20less%20than,and%20accept%20the%20alternative%20hypothesis.
## https://blog.minitab.com/en/understanding-statistics/what-can-you-say-when-your-p-value-is-greater-than-005
## Is statistically significant if p > 0.5.
## If the p-value is less than 0.05, we reject the null hypothesis that there's no difference between the median and conclude that a significant difference does exist. If the p-value is larger than 0.05, we cannot conclude that a significant difference exists. 
## A p-value less than 0.05 (typically ≤ 0.05) is statistically significant and indicates strong evidence against the null hypothesis. Therefore, we reject the null hypothesis, and accept the alternative hypothesis.
## A p-value higher than 0.05 (> 0.05) is not statistically significant and indicates strong evidence for the null hypothesis. This means we retain the null hypothesis and reject the alternative hypothesis.
## If the p-value is statistically significant, the values in one sample are more likely to be larger than the values in the other sample, this means there is significant differences between the data sets.



## Collate and compare the data
## https://pbpython.com/excel-file-combine.html
collated_globals.to_excel(writer, sheet_name="Globals Comparison")
# cat_plans.to_excel(writer, sheet_name="Cat Plan Comparison")

writer.save()
from collections import defaultdict
import itertools
import os
from typing import Optional, Sequence, Union
import pandas
import glob
import argparse
import numpy
import tqdm
import xlsxwriter
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ranksums.html
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html#scipy.stats.mannwhitneyu
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html#scipy.stats.kruskal
## https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html#scipy.stats.friedmanchisquare
## Problem with friedmanchisquare is that affect of one measurement not being seperable may make two that are statistically significant seem like they are not.
from scipy.stats import ranksums, mannwhitneyu, wilcoxon, kruskal, friedmanchisquare

__statistics_sets: list[str] = ["Globals Comparison",
                                "Score Ranksums"]

## Special action for storing arguments of parameters that can have a different values for each abstraction level in the hierarchy
def mapping_argument_factory(key_choices: Optional[list[str]] = None, allow_multiple_values: bool = True) -> type:
    
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Sequence[str], option_string: Optional[str] = None):
        _values: dict[str, str] = {}
        try:
            for key_value in values:
                key, value = key_value.split('=', 1)
                if (self.__class__.key_choices is not None
                    and key not in self.__class__.key_choices):
                    error_string: str = f"Error during parsing filter argument '{option_string}' for key-value mapping {key_value}, key {key} not allowed."
                    print(error_string)
                    raise RuntimeError(error_string)
                if ',' in value:
                    if not self.__class__.allow_multiple_values:
                        error_string: str = f"Error during parsing filter argument '{option_string}' for key-value mapping {key_value}, multiple values are not allowed."
                        print(error_string)
                        raise RuntimeError(error_string)
                    _values[key] = value.split(',')
                else:
                    if self.__class__.allow_multiple_values:
                        _values[key] = [value]
                    else: _values[key] = value
        except ValueError as error:
            print(f"Error during parsing filter argument '{option_string}' for key-value mapping {key_value}, {error}.")
            raise error
        setattr(namespace, self.dest, _values)
    
    return type("StoreMappingArgument", (argparse.Action,), {"__call__" : __call__,
                                                             "key_choices" : key_choices.copy() if key_choices is not None else None,
                                                             "allow_multiple_values" : allow_multiple_values})

## Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-filter", nargs="+", default=None, action=mapping_argument_factory(), type=str,
                    metavar="header=value_1,value_2,[...]value_n")
parser.add_argument("-out", "--output_path", required=True, type=str)
parser.add_argument("-combine", "--combine_on", nargs="*", default=[], type=str)
parser.add_argument("-group", "--group_by", nargs="*", default=["problem"], type=str)
parser.add_argument("-diff", "--compare_only_different", nargs="*", default=["achievement_type"], type=str)
parser.add_argument("-same", "--compare_only_same", nargs="*", default=["problem", "planning_type", "planning_mode", "search_mode"], type=str)
parser.add_argument("-send_to_dsv", nargs="+", default=None, action=mapping_argument_factory(key_choices=__statistics_sets, allow_multiple_values=False), type=str,
                    metavar="statistics_set=file_path")
cli_args: argparse.Namespace = parser.parse_args()

def get_option_list(option_list: list[str]) -> str:
    if option_list:
        return "\n\t".join(option_list)
    return "None"

print("\n\t=============================",
        "\t Command line options given:",
        "\t=============================",
      sep="\n", end="\n\n")

print("Input paths:\n\t" + get_option_list(cli_args.input_paths), end="\n\n")
print("File filters:\n\t" + get_option_list((f"{key} : [{', '.join(value)}]" for key, value in cli_args.filter.items()) if cli_args.filter is not None else None), end="\n\n")
print("Output path: " + cli_args.output_path, end="\n\n")
print("Combine data sets on:\n\t" + get_option_list(cli_args.combine_on), end="\n\n")
print("Group and sort data sets by:\n\t" + get_option_list(cli_args.group_by), end="\n\n")
print("Compare only data sets with different:\n\t" + get_option_list(cli_args.compare_only_different), end="\n\n")
print("Compare only data sets with same:\n\t" + get_option_list(cli_args.compare_only_same), end="\n\n")
print("Send statistics to dsv file:\n\t" + get_option_list((f"{key} : {value}" for key, value in cli_args.send_to_dsv.items()) if cli_args.send_to_dsv is not None else None), end="\n\n")

print("Your original files will NOT be modified.")
input_: str = input("Proceed? [(y)/n]: ")
if input_ == "n": exit()
print()

## Gather the configurations we want to compare into tuples (each defines a unique set) which we want to compare between each other;
##      - Aggregates are generated seperately for each set.
configuration_headers: list[str] = ["problem",
                                    "planning_type",
                                    "planning_mode",
                                    "online_bounds",
                                    "search_mode",
                                    "achievement_type"]

for combine in cli_args.combine_on:
    configuration_headers.remove(combine)

def extract_configuration(excel_file_name: str) -> Optional[list[str]]:
    "Extract the data set configuration for a given excel file name."
    
    configuration_dict: dict[str, str] = {}
    raw_config: str = os.path.basename(excel_file_name).strip("ASH_Excel_").split(".")[0]
    terms: list[str] = raw_config.split("_")
    
    configuration_dict["problem"] = terms[0]
    configuration_dict["planning_type"] = terms[1]
    
    if configuration_dict["planning_type"] == "hcl":
        for header in configuration_headers:
            if header not in ["problem", "planning_type"]:
                configuration_dict[header] = "NONE"
        
    else:
        index: int = 1
        def get_term(matches: Optional[list[str]] = None) -> str:
            nonlocal index
            index += 1
            if index in range(len(terms)):
                term: str = terms[index]
                if (matches is None or term in matches):
                    return term
                else: index -= 1
            return "NONE"
        
        configuration_dict["planning_mode"] = get_term()
        if configuration_dict["planning_mode"] == "online":
            configuration_dict["strategy"] = get_term(["basic", "hasty", "steady", "jumpy", "impetuous", "relentless"])
            configuration_dict["bound_type"] = get_term(["abs", "per", "sl", "inct", "dift", "intt"])
            for rel_index, term in enumerate(terms[(index := index + 1):]):
                if not term.isdigit():
                    rel_index -= 1
                    break
            configuration_dict["online_bounds"] = str(tuple(int(bound) for bound in terms[index : index + rel_index + 1]))
            index += rel_index
        else: configuration_dict["online_bounds"] = "NONE"
        
        configuration_dict["search_mode"] = get_term()
        if configuration_dict["search_mode"] == "min":
            configuration_dict["search_mode"] = configuration_dict["search_mode"] + get_term()
        configuration_dict["achievement_type"] = get_term(["seqa", "sima"])
        if get_term(["conc"]) == "conc":
            configuration_dict["action_planning"] = "concurrent"
        else: configuration_dict["action_planning"] = "sequential"
        
        # if configuration_dict["planning_mode"] == "online":
        #     preach_type
        #     blend_direction
        #     blend_type
        #     blend_quantity
        #     online_method
    
    if (cli_args.filter is not None
        and not all((key not in cli_args.filter
                     or value in cli_args.filter[key])
                    for key, value in configuration_dict.items())):
        return None
    return tuple(value for key, value in configuration_dict.items()
                 if key in configuration_headers)

## A dictionary of data sets;
##  - Mapping: workbook name x worksheet name -> data frame
data_sets: dict[tuple[str, ...], dict[str, pandas.DataFrame]] = defaultdict(dict) ## TODO Need to take the average of the quantiles over data sets!!!

## Iterate over all directory paths and all excel files within them
files_loaded: int = 0
for path in cli_args.input_paths:
    for excel_file_name in glob.glob(f"{path}/*.xlsx"):
        
        configuration: Optional[list[str]] = extract_configuration(excel_file_name)
        if configuration is None:
            continue
        files_loaded += 1
        
        ## Open each excel workbook and extract its data
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#excelfile-class
        print(f"Opening excel file {excel_file_name} :: Matching Data Set Configuration {configuration}")
        with pandas.ExcelFile(excel_file_name, engine="openpyxl") as excel_file:
            ## Read globals and concatenated plans
            worksheets: dict[str, pandas.DataFrame] = pandas.read_excel(excel_file, ["Globals", "Cat Plans"])
            
            ## Globals is not nicely formatted so some extra work is needed to extract it
            null_rows: pandas.Series = worksheets["Globals"].isnull().all(axis=1)
            null_rows_index: pandas.Int64Index = worksheets["Globals"].index[null_rows]
            last_data_row: int = null_rows_index.values[0]
            worksheets["Globals"] = worksheets["Globals"][:last_data_row]
            
            ## Some of the early classical planning files don't have the time score in globals
            if "TI_SCORE" not in worksheets["Globals"]:
                worksheets["Globals"].insert(worksheets["Globals"].columns.get_loc("AME_PA_SCORE") + 1,
                                             "TI_SCORE", worksheets["Globals"]["HA_SCORE"])
            
            ## Set the order of the columns to be consistent????
            
            
            ## Calculate the percentage of the total time spent in grounding, solving, and overhead;
            ##      - These define the Relative complexity of;
            ##          - Grounding the logic program (complexity of representing the size of the problem),
            ##          - Solving the logic program (complexity of searching for a solution to the problem of minimal length),
            ##          - The overhead in terms of the time taken to make reactive decisions during search.
            time_types: list[str] = ["GT", "ST", "OT"]
            for time_type in reversed(time_types):
                worksheets["Cat Plans"].insert(worksheets["Cat Plans"].columns.get_loc("OT") + 1,
                                               f"{time_type}_POTT", worksheets["Cat Plans"][time_type] / worksheets["Cat Plans"]["TT"])
            
            for sheet_name in worksheets:
                ## Get rid of old index data
                worksheets[sheet_name] = worksheets[sheet_name].drop(["Unnamed: 0", "RU"], axis="columns")
                
                ## Convert the data types to those pandas thinks is best
                worksheets[sheet_name] = worksheets[sheet_name].convert_dtypes()
            
            if configuration not in data_sets:
                print(f"Creating new data set for configuration {configuration}")
                data_sets[configuration].update(worksheets)
            else:
                print(f"Combining with existing data set for configuration {configuration}")
                for sheet_name in worksheets:
                    data_sets[configuration][sheet_name] = data_sets[configuration][sheet_name].append(worksheets[sheet_name])

print(f"\nA total of {files_loaded} matching files were loaded.")
print(f"A total of {len(data_sets)} combined data sets were obtained.")
input_: str = input("Proceed? [(y)/n]: ")
if input_ == "n": exit()

## Open a new output excel file to save the collated data to
## https://xlsxwriter.readthedocs.io/working_with_pandas.html
writer = pandas.ExcelWriter(cli_args.output_path, engine="xlsxwriter") # pylint: disable=abstract-class-instantiated
out_workbook: xlsxwriter.Workbook = writer.book

## Add a column to table for each comparison level
out_worksheets: dict[str, list[pandas.DataFrame]] = defaultdict(list)

## For each data set, add a row to the dataframe with column entries for each comparison level for that set
print("\nProcessing raw data sets...")
for configuration, data_set in tqdm.tqdm(data_sets.items()):
    for sheet_name in data_set:
        data_raw: pandas.DataFrame = data_set[sheet_name]
        if sheet_name == "Cat Plans":
            data_quantiles: pandas.DataFrame = data_set[sheet_name].groupby("AL").quantile([0.0, 0.25, 0.50, 0.75, 1.0])
            data_quantiles.index = data_quantiles.index.set_levels(data_quantiles.index.levels[1].astype(str), level=1)
            data_quantiles = data_quantiles.rename_axis(["AL", "statistic"])
            
            ## Data quantiles is a multi-index, with the abstraction level (level 0) and the quantiles (level 1)
            ## https://pandas.pydata.org/docs/reference/api/pandas.MultiIndex.get_level_values.html
            for abstraction_level in data_quantiles.index.get_level_values("AL").unique():
                ## Need to use a tuple to get the index to .loc as Pandas interprets tuple entries as levels and list entries as items in a level
                ##      - DataFrame.loc[rowId,colId]
                ##      - https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html#advanced-indexing-with-hierarchical-index
                data_quantiles.loc[(abstraction_level, "IQR"),:] = (data_quantiles.loc[(abstraction_level, "0.75")] - data_quantiles.loc[(abstraction_level, "0.25")]).values
                data_quantiles.loc[(abstraction_level, "Range"),:] = (data_quantiles.loc[(abstraction_level, "1.0")] - data_quantiles.loc[(abstraction_level, "0.0")]).values
            data_quantiles = data_quantiles.sort_index()
            
        else:
            data_quantiles: pandas.DataFrame = data_set[sheet_name].quantile([0.0, 0.25, 0.50, 0.75, 1.0])
            data_quantiles = data_quantiles.rename_axis("statistic")
            data_quantiles = data_quantiles.append((data_quantiles.loc[0.75] - data_quantiles.loc[0.25]).rename("IQR"))
            data_quantiles = data_quantiles.append((data_quantiles.loc[1.0] - data_quantiles.loc[0.0]).rename("Range"))
        
        ## Insert columns into the sheet to define the configurations
        for index, level_name in enumerate(configuration_headers):
            data_quantiles.insert(index, level_name, configuration[index])
        data_quantiles = data_quantiles.set_index(configuration_headers, append=True)
        
        if sheet_name == "Cat Plans":
            data_quantiles = data_quantiles.reorder_levels(configuration_headers + ["AL", "statistic"])
        else: data_quantiles = data_quantiles.reorder_levels(configuration_headers + ["statistic"])
        data_quantiles = data_quantiles.sort_index(level=cli_args.group_by)
        
        out_worksheets[sheet_name].append(data_quantiles)

collated_globals: pandas.DataFrame = pandas.concat(out_worksheets["Globals"])
collated_cat_plans: pandas.DataFrame = pandas.concat(out_worksheets["Cat Plans"])

## Use IQR as the representation of the distribution, then use a non-parametric test like mann-whitney to evalute statistical significance, since we are not sure that it is gaussian/normal.
## https://www.simplypsychology.org/p-value.html#:~:text=A%20p%2Dvalue%20less%20than,and%20accept%20the%20alternative%20hypothesis.
## https://blog.minitab.com/en/understanding-statistics/what-can-you-say-when-your-p-value-is-greater-than-005
## Is statistically significant if p > 0.5.
## If the p-value is less than 0.05, we reject the null hypothesis that there's no difference between the median and conclude that a significant difference does exist. If the p-value is larger than 0.05, we cannot conclude that a significant difference exists. 
## A p-value less than 0.05 (typically ≤ 0.05) is statistically significant and indicates strong evidence against the null hypothesis. Therefore, we reject the null hypothesis, and accept the alternative hypothesis.
## A p-value higher than 0.05 (> 0.05) is not statistically significant and indicates strong evidence for the null hypothesis. This means we retain the null hypothesis and reject the alternative hypothesis.
## If the p-value is statistically significant, the values in one sample are more likely to be larger than the values in the other sample, this means there is significant differences between the data sets.

## The score statistics
compare_statistics: list[str] = ["QL_SCORE", "TI_SCORE", "GRADE"]

## Construct a dataframe including the medians for all combined configurations
rows_index = pandas.MultiIndex.from_tuples(data_sets.keys(), names=configuration_headers)
score_medians = pandas.DataFrame(index=rows_index, columns=compare_statistics)
score_IQR = pandas.DataFrame(index=rows_index, columns=compare_statistics)
score_IQR_percent = pandas.DataFrame(index=rows_index, columns=compare_statistics)
for configuration, data_set in data_sets.items():
    score_medians.loc[configuration,:] = collated_globals.loc[(*configuration, 0.5),compare_statistics]
    score_IQR.loc[configuration,:] = collated_globals.loc[(*configuration, "IQR"),compare_statistics]
    score_IQR_percent.loc[configuration,:] = (score_IQR.loc[configuration,:] / score_medians.loc[configuration,:])

## Construct a dataframe that acts as a matrix of all compared configurations;
##      - There is a multi-index on both the rows and columns to compare all pair-wise differences,
##      - Result sets that are combined are dropped from both rows and columns and are taken as the mean over all results in those sets.
columns_index = pandas.MultiIndex.from_tuples(((*configuration, statistic)
                                               for configuration in data_sets.keys()
                                               for statistic in compare_statistics),
                                              names=(configuration_headers + ["result"]))
score_ranksums = pandas.DataFrame(index=rows_index, columns=columns_index)
score_ranksums = score_ranksums.sort_index(level=cli_args.group_by)

print("\nProcessing ranksums...")
for row_configuration, column_configuration in itertools.permutations(data_sets.keys(), r=2):
    ignore: bool = False
    for index, level_name in enumerate(configuration_headers):
        if level_name in cli_args.compare_only_different:
            if row_configuration[index] == column_configuration[index]:
                ignore = True
                break
        if level_name in cli_args.compare_only_same:
            if row_configuration[index] != column_configuration[index]:
                ignore = True
                break
    if ignore: continue
    
    for statistic in compare_statistics:
        ranksum = ranksums(data_sets[row_configuration]["Globals"][statistic].values,
                           data_sets[column_configuration]["Globals"][statistic].values)
        score_ranksums.loc[row_configuration, (*column_configuration, statistic)] = ranksum.pvalue
    score_ranksums.reorder_levels(configuration_headers)

## Calculate fitness to exponential trends for step-wise



## Calculate sub-plan/refinement tree balancing; NAE of spread of matching child steps, expansion deviation and balance, balance score



## Calculate partial problem balancing; NAE of spread of division steps and variance in length of partial plans



## Collate and compare the data
## https://pbpython.com/excel-file-combine.html
collated_globals.to_excel(writer, sheet_name="Globals Comparison", merge_cells=False)
worksheet_globals = writer.sheets["Globals Comparison"]

## TODO The graph should probably be of the medians, with IQR as error bars
## TODO Put conditional formatting for scores with coloured bar
## Create a chart object
chart = out_workbook.add_chart({"type" : "column"})

## Get the dimensions of the dataframe
max_row, max_col = collated_globals.shape

index_levels: int = collated_globals.index.nlevels
last_index_cell: str = chr(ord('@') + index_levels)
ql_score: str = chr(ord('@') + (index_levels + collated_globals.columns.get_loc("QL_SCORE") + 1))
ti_score: str = chr(ord('@') + (index_levels + collated_globals.columns.get_loc("TI_SCORE") + 1))
grade: str = chr(ord('@') + (index_levels + collated_globals.columns.get_loc("GRADE") + 1))

## Configure the series of the chart from the dataframe data
chart.add_series({"values" : f"='Globals Comparison'!${ql_score}$2:${ql_score}${max_row}",
                  "categories" : f"='Globals Comparison'!$A$2:${last_index_cell}${max_row + 1}",
                  "name" : f"='Globals Comparison'!${ql_score}$1:${ql_score}$1"})
# chart.add_series({"values" : "='Globals Comparison'!$V$2:$V$43",
#                   "categories" : "='Globals Comparison'!$A$2:$F$43",
#                   "name" : "='Globals Comparison'!$V$1:$V$1"})
# chart.add_series({"values" : "='Globals Comparison'!$AC$2:$AC$43",
#                   "categories" : "='Globals Comparison'!$A$2:$F$43",
#                   "name" : "='Globals Comparison'!$AC$1:$AC$1"})

## Insert the chart into the worksheet
worksheet_globals.insert_chart(1, 3, chart)



score_medians.to_excel(writer, sheet_name="Score Medians")
score_IQR.to_excel(writer, sheet_name="Score IQR")
score_IQR_percent.to_excel(writer, sheet_name="Score IQR Percent")

score_ranksums.to_excel(writer, sheet_name="Score Ranksums")
if (cli_args.send_to_dsv is not None
    and "Score Ranksums" in cli_args.send_to_dsv):
    ## TODO Statistics_sets["Score Ranksums"]
    score_ranksums.to_csv(cli_args.send_to_dsv["Score Ranksums"], sep=",", na_rep=" ", line_terminator="\n", index=True)
worksheet = writer.sheets["Score Ranksums"]

## Get the dimensions of the dataframe
min_row, min_col = len(configuration_headers) + 2, len(configuration_headers)
max_row, max_col = score_ranksums.shape

## https://xlsxwriter.readthedocs.io/workbook.html#add_format
## https://xlsxwriter.readthedocs.io/format.html#format
significant = out_workbook.add_format({"bg_color" : "#37FF33"})
insignificant = out_workbook.add_format({"bg_color" : "#FF294A"})

## https://xlsxwriter.readthedocs.io/working_with_conditional_formats.html#working-with-conditional-formats
## conditional_format(first_row, first_col, last_row, last_col, options)
worksheet.conditional_format(min_row, min_col, min_row + max_row - 1, min_col + max_col - 1,
                             {"type" : "cell",
                              "criteria" : "less than",
                              "value" : 0.05,
                              "format" : significant})
worksheet.conditional_format(min_row, min_col, min_row + max_row - 1, min_col + max_col - 1,
                             {"type" : "cell",
                              "criteria" : "greater than",
                              "value" : 0.05,
                              "format" : insignificant})
                            #  {"type" : "3_color_scale",
                            #   "max_value" : 1.0,
                            #   "min_value" : 0.0,
                            #   "max_color" : "red",
                            #   "min_color" : "green"})



collated_cat_plans.to_excel(writer, sheet_name="Cat Plan Comparison")

## Graphs
# Plan quality histogram, the x axis in the columns of ranksums matrix
# Time score histogram
# Grade histogram
# Three-dimensional comparison diagram



writer.save()
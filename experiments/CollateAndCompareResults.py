from collections import defaultdict
import functools
import itertools
import os
from typing import Any, Optional, Sequence
import numpy
import pandas
import pandas.io.formats.style as pandas_style
import glob
import argparse
import tqdm
import xlsxwriter
import subprocess
import matplotlib
from matplotlib import pyplot
import tikzplotlib
# import warnings
# warnings.simplefilter(action='ignore', category=pandas.errors.PerformanceWarning)

## Global data set comparison statistics;
##      - Problem with global comparisons, are that affect of one sample is not being seperable may make two others, that are statistically significant, seem like they are not.
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fligner.html
from scipy.stats import kruskal, friedmanchisquare, fligner

## Pair-wise data set comparison statistics;
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ranksums.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
##      - https://stats.stackexchange.com/questions/558814/actual-difference-between-the-statistic-results-from-scipy-stats-ranksums-and-sc
##      - https://stats.stackexchange.com/questions/91034/what-is-the-difference-between-the-wilcoxon-srank-sum-test-and-the-wilcoxons-s
##          - Use the Mann-Whitney-Wilcoxon ranked sum test (ranksums) when the data are not paired (independent), e.g. comparing performance of differnt configurations on different problems.
##          - Use the Mann-Whitney-Wilcoxon signed rank test (wilcoxon) when the data are paired/related, e.g. comparing performance of different configurations on the same problem, or the same configuration for different problems.
from scipy.stats import ranksums, wilcoxon

## Individual data set statistics;
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skewtest.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosistest.html
from scipy.stats import normaltest, skewtest, kurtosis, kurtosistest

#########################################################################################################################################################################################
######## Build the raw data sets
#########################################################################################################################################################################################

def mapping_argument_factory(key_choices: Optional[list[str]] = None, allow_multiple_values: bool = True) -> type:
    "Special action for storing arguments of parameters given as a mapping."   
    
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Sequence[str], option_string: Optional[str] = None):
        _values: dict[str, str] = {}
        try:
            for key_value in values:
                key, value = key_value.split('=', 1)
                if (self.__class__.key_choices is not None
                    and key not in self.__class__.key_choices):
                    error_string: str = f"Error during parsing filter argument '{option_string}' for key-value mapping {key_value}, the key {key} is not allowed."
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
            print(f"Error during parsing filter argument '{option_string}' for key-value mapping {key_value}: {error}.")
            raise error
        setattr(namespace, self.dest, _values)
    
    return type("StoreMappingArgument", (argparse.Action,), {"__call__" : __call__,
                                                             "key_choices" : key_choices.copy() if key_choices is not None else None,
                                                             "allow_multiple_values" : allow_multiple_values})

## Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-out", "--output_path", required=True, type=str)
parser.add_argument("-filter", nargs="+", default=None, action=mapping_argument_factory(), type=str,
                    metavar="header=value_1,value_2,[...]value_n")
parser.add_argument("-combine", "--combine_on", nargs="*", default=[], type=str)
parser.add_argument("-order", "--order_index_headers", nargs="*", default=[], type=str)
parser.add_argument("-sort", "--sort_index_values", nargs="*", default=[], type=str)
parser.add_argument("-diff", "--compare_only_different", nargs="*", default=[], type=str)
parser.add_argument("-same", "--compare_only_same", nargs="*", default=[], type=str)
cli_args: argparse.Namespace = parser.parse_args()

def get_option_list(option_list: list[str]) -> str:
    "List the options given by the user for a particular parameter."
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
print("Order of index headers:\n\t" + get_option_list(cli_args.order_index_headers), end="\n\n")
print("Sort index values by:\n\t" + get_option_list(cli_args.sort_index_values), end="\n\n")
print("Compare only data sets with different:\n\t" + get_option_list(cli_args.compare_only_different), end="\n\n")
print("Compare only data sets with same:\n\t" + get_option_list(cli_args.compare_only_same), end="\n\n")

print("Your original files will NOT be modified.")
input_: str = input("\nProceed? [(y)/n]: ")
if input_ == "n": exit()
print()

#########################################################################################################################################################################################
######## Build the raw data sets
#########################################################################################################################################################################################

## Gather the configurations we want to compare into tuples (each defines a unique set) which we want to compare between each other;
##      - Aggregates are generated seperately for each set,
##      - The following are the configuration headers.
configuration_headers: list[str] = ["problem",
                                    "planning_type",
                                    "planning_mode",
                                    "strategy",
                                    "bound_type",
                                    "online_bounds",
                                    "search_mode",
                                    "achievement_type",
                                    "action_planning",
                                    "preach_type",
                                    "blend_direction",
                                    "blend_type",
                                    "blend_quantity",
                                    "online_method"]

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
        def get_term(matches: Optional[list[str]] = None, default: str = "NONE") -> str:
            "Function for getting hierarchical conformance refinement planning configuration terms from file names."
            
            ## Move to the next term index
            nonlocal index
            index += 1
            
            ## If the index exists...
            if index in range(len(terms)):
                term: str = terms[index]
                ## If the term matches, return it...
                if (matches is None or term in matches):
                    return term
                ## Otherwise, move back to the previous index
                else: index -= 1
            
            ## Return the default if the index does not exist,
            ## or the term does not match
            return default
        
        configuration_dict["planning_mode"] = get_term(["offline", "online"], "online")
        
        if configuration_dict["planning_mode"] == "online":
            configuration_dict["strategy"] = get_term(["basic", "hasty", "steady", "jumpy", "impetuous", "relentless"], "basic")
            configuration_dict["division_commit_type"] = get_term(["con", "rup", "comb"], "rup")
            configuration_dict["prediv"] = get_term(["prediv", "childdiv"], "childdiv")
            configuration_dict["bound_type"] = get_term(["abs", "per", "sl", "inct", "dift", "intt"], "abs")
            for rel_index, term in enumerate(terms[(index := index + 1):]):
                if not term.isdigit():
                    rel_index -= 1; break
            configuration_dict["online_bounds"] = str(tuple(int(bound) for bound in terms[index : index + rel_index + 1]))
            index += rel_index
        else:
            configuration_dict["strategy"] = "NONE"
            configuration_dict["bound_type"] = "NONE"
            configuration_dict["online_bounds"] = "NONE"
        
        configuration_dict["search_mode"] = get_term(["min", "standard", "yield"], "min")
        if configuration_dict["search_mode"] == "min":
            configuration_dict["search_mode"] = configuration_dict["search_mode"] + get_term()
        configuration_dict["achievement_type"] = get_term(["seqa", "sima"], "seqa")
        
        if get_term(["conc"]) == "conc":
            configuration_dict["action_planning"] = "concurrent"
        else: configuration_dict["action_planning"] = "sequential"
        
        if configuration_dict["planning_mode"] == "online":
            if get_term(["preach"]) == "preach":
                configuration_dict["preach_type"] = get_term(["heur", "opt"], "opt")
            
            if get_term(["blend"]) == "blend":
                configuration_dict["blend_direction"] = get_term(["left", "right"], "right")
                
                blend: str = get_term()
                configuration_dict["blend_type"] = blend[0]
                configuration_dict["blend_quantity"] = int(blend[1:])
            
            configuration_dict["online_method"] = get_term(["gf", "cf", "hy"], "gf")
        else:
            configuration_dict["preach_type"] = "NONE"
            configuration_dict["blend_direction"] = "NONE"
            configuration_dict["blend_type"] = "NONE"
            configuration_dict["blend_quantity"] = "NONE"
            configuration_dict["online_method"] = "NONE"
    
    if (cli_args.filter is not None
        and not all((key not in cli_args.filter
                     or value in cli_args.filter[key])
                    for key, value in configuration_dict.items())):
        return None
    return tuple(value for key, value in configuration_dict.items()
                 if key in configuration_headers)

## A dictionary of data sets;
##      - A data set is all the data for a given problem and planner configuration (or unit of a set of them) for a given property,
##      - Mapping: configuration set (row index) X property (worksheet name) -> data frame
data_sets: dict[tuple[str, ...], dict[str, list[pandas.DataFrame]]] = defaultdict(dict)

## Iterate over all directory paths and all excel files within them
files_loaded: int = 0
for path in cli_args.input_paths:
    print(f"\nLoading files from path {path} ...")
    
    for excel_file_name in tqdm.tqdm(glob.glob(f"{path}/*.xlsx")):
        
        ## Extract the configuration from the file name;
        ##  - If a matching configuration exists, then load the data,
        ##  - Otherwise, ignore the file.
        configuration: Optional[list[str]] = extract_configuration(excel_file_name)
        if configuration is None:
            continue
        files_loaded += 1
        
        ## Open each excel workbook and extract its data
        ##  - https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#excelfile-class
        # print(f"Opening excel file {excel_file_name} :: Matching Data Set Configuration {configuration}")
        with pandas.ExcelFile(excel_file_name, engine="openpyxl") as excel_file:
            ## Read globals and concatenated plans
            worksheets: dict[str, pandas.DataFrame] = pandas.read_excel(excel_file, ["Globals", "Cat Plans"])
            
            ## Globals is not nicely formatted so some extra work is needed to extract it;
            ##      - Get the rows were all the entries are null,
            ##      - Get the index over those rows,
            ##      - Clip the dataframe to include only elements up to but excluding the first null row.
            null_rows: pandas.Series = worksheets["Globals"].isnull().all(axis=1)
            null_rows_index: pandas.Index = worksheets["Globals"].index[null_rows]
            worksheets["Globals"] = worksheets["Globals"][:null_rows_index.values[0]]
            
            ## Some of the early classical planning files don't have the time score in globals
            if "TI_SCORE" not in worksheets["Globals"]:
                worksheets["Globals"].insert(worksheets["Globals"].columns.get_loc("AME_PA_SCORE") + 1,
                                             "TI_SCORE", worksheets["Globals"]["HA_SCORE"])
            
            ## Calculate the percentage of the total time spent in grounding, solving, and overhead;
            ##      - These define the relative complexity of;
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
            
            for sheet_name in worksheets:
                data_sets[configuration].setdefault(sheet_name, []).append(worksheets[sheet_name])

## Remove all NONE headers
new_configuration_headers: list[str] = []
none_header_indices: list[int] = []
new_data_sets: dict[tuple[str, ...], dict[str, list[pandas.DataFrame]]] = defaultdict(dict)

for index, header in enumerate(configuration_headers):
    if any(configuration[index] != "NONE" for configuration in data_sets):
        new_configuration_headers.append(header)
    else: none_header_indices.append(index)

for configuration in data_sets:
    new_data_sets[tuple(header for index, header in enumerate(configuration) if index not in none_header_indices)] = data_sets[configuration]

configuration_headers = new_configuration_headers
data_sets = new_data_sets

## Set the order of the configuration headers across the top of the row indices;
##      - Any headers requested to be ordered come first in the header list,
##      - Any headers that are part of set of headers but are not in the order list come after.
HEADER_ORDER: list[str] = []
for header in cli_args.order_index_headers:
    if header in configuration_headers:
        HEADER_ORDER.append(header)
for header in configuration_headers:
    if header not in HEADER_ORDER:
        HEADER_ORDER.append(header)

print(f"\nA total of {files_loaded} matching files were loaded.")
print(f"A total of {len(data_sets)} combined data sets were obtained.\n")
print(f"Configuration headers:\n\t{configuration_headers}")
print("Data sets:\n\t" + "\n\t".join(repr(configuration) for configuration in data_sets))

input_: str = input("\nProceed? [(y)/n]: ")
if input_ == "n": exit()

#########################################################################################################################################################################################
######## Process the raw data sets
#########################################################################################################################################################################################

combined_data_sets: dict[tuple[str, ...], dict[str, pandas.DataFrame]] = defaultdict(dict)
combined_data_sets_quantiles: dict[str, list[pandas.DataFrame]] = defaultdict(list)

## For each data set, add a row to the dataframe with column entries for each comparison level for that set
print("\nProcessing raw data sets...")
for configuration, combined_data_set in tqdm.tqdm(data_sets.items()):
    
    for sheet_name in combined_data_set:
        quantiles_for_data_set: dict[str, list[pandas.DataFrame]] = defaultdict(list)
        data_set: dict[str, list[pandas.DataFrame]] = defaultdict(list)
        
        index_for_data_set: list[str]
        if sheet_name == "Cat Plans":
            index_for_data_set = configuration_headers + ["AL", "statistic"]
        else: index_for_data_set = configuration_headers + ["statistic"]
        
        individual_data_set: pandas.DataFrame
        for individual_data_set in combined_data_set[sheet_name]:
            individual_data_set_copy: pandas.DataFrame = individual_data_set.copy(deep=True)
            data_quantiles: pandas.DataFrame
            
            if sheet_name == "Cat Plans":
                data_quantiles = individual_data_set.groupby("AL").quantile([0.0, 0.25, 0.50, 0.75, 1.0])
                data_quantiles.index = data_quantiles.index.set_levels(data_quantiles.index.levels[1].astype(float), level=1)
                data_quantiles = data_quantiles.rename_axis(["AL", "statistic"])
                
                ## Data quantiles is a multi-index, with the abstraction level (level 0) and the quantiles (level 1)
                ## https://pandas.pydata.org/docs/reference/api/pandas.MultiIndex.get_level_values.html
                for abstraction_level in data_quantiles.index.get_level_values("AL").unique():
                    ## Need to use a tuple to get the index to .loc as Pandas interprets tuple entries as levels and list entries as items in a level
                    ##      - DataFrame.loc[rowId,colId]
                    ##      - https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html#advanced-indexing-with-hierarchical-index
                    data_quantiles.loc[(abstraction_level, "IQR"),:] = (data_quantiles.loc[(abstraction_level, 0.75)] - data_quantiles.loc[(abstraction_level, 0.25)]).values
                    data_quantiles.loc[(abstraction_level, "Range"),:] = (data_quantiles.loc[(abstraction_level, 1.0)] - data_quantiles.loc[(abstraction_level, 0.0)]).values
                data_quantiles = data_quantiles.sort_index()
                
            else:
                data_quantiles = individual_data_set.quantile([0.0, 0.25, 0.50, 0.75, 1.0])
                data_quantiles = data_quantiles.rename_axis("statistic")
                data_quantiles.loc["IQR",:] = (data_quantiles.loc[0.75] - data_quantiles.loc[0.25]).values
                data_quantiles.loc["Range",:] = (data_quantiles.loc[1.0] - data_quantiles.loc[0.0]).values
            
            ## Insert columns to define the configurations,
            ## then append those columns to the index (the abstraction level and aggregate statistic is also part of the index)
            for index, level_name in enumerate(configuration_headers):
                individual_data_set_copy.insert(index, level_name, configuration[index])
                data_quantiles.insert(index, level_name, configuration[index])
            individual_data_set_copy = individual_data_set_copy.set_index(configuration_headers)
            data_quantiles = data_quantiles.set_index(configuration_headers, append=True)
            
            ## Set the order of the index levels;
            ##      - Configurations comes first, then abstraction level for concatenated plans, then the statistic.
            individual_data_set_copy = individual_data_set_copy.reorder_levels(configuration_headers)
            data_quantiles = data_quantiles.reorder_levels(index_for_data_set)
            
            ## Append the data quantiles for the current data set to the list
            data_set[sheet_name].append(individual_data_set_copy)
            quantiles_for_data_set[sheet_name].append(data_quantiles)
        
        ## Take the average of the quantiles over the all the individual data sets in the combined data set
        combined_data_sets[configuration][sheet_name] = pandas.concat(data_set[sheet_name]).astype(float)
        combined_data_sets_quantiles[sheet_name].append(pandas.concat(quantiles_for_data_set[sheet_name]).astype(float).groupby(index_for_data_set).mean())

#########################################################################################################################################################################################
######## Generate the seven-number summaries for plotting results - (all the quantiles, the IQR and the range)
#########################################################################################################################################################################################

## Concatenate all the individual quantile data set frames into single dataframes
quantiles_globals: pandas.DataFrame = pandas.concat(combined_data_sets_quantiles["Globals"])
quantiles_cat_plans: pandas.DataFrame = pandas.concat(combined_data_sets_quantiles["Cat Plans"])
al_range = range(1, quantiles_cat_plans.index.get_level_values("AL").max() + 1)

#########################################################################################################################################################################################
######## Generate the two-number summaries for tabulating results - (The Median and the IQR)
#########################################################################################################################################################################################

## The minimal summary statistics to compare for globals
summary_statistics_globals: list[str] = ["QL_SCORE", "TI_SCORE", "GRADE"]
summary_statistics_cat_plans: list[str] = ["GT", "ST", "OT", "GT_POTT", "ST_POTT", "OT_POTT", "TT", "LT", "CT"]

## Construct a dataframe including just the medians and IQR for all data sets (combined configurations);
##      - The outer columns headers are the median and IQR,
##      - The inner column headers are the "global summary statistics"; (quality score, time score, and grade),
##      - The row index headers are the combined configuration headers, sorted according to user input.
summary_globals: pandas.DataFrame = quantiles_globals.query("statistic in ['IQR', 0.5]")[summary_statistics_globals].unstack("statistic").stack(0).unstack(-1) # quantiles_globals.loc[(*tuple(slice(None) for _ in range(quantiles_globals.index.nlevels - 1)), ["IQR", 0.5]),:][summary_statistics_globals]
summary_cat_plans: pandas.DataFrame = quantiles_cat_plans.query("statistic in ['IQR', 0.5]")[summary_statistics_cat_plans].unstack("statistic").stack(0).unstack(-1)

## Reorder the values in the summary statistic level of the columns index
##      - https://stackoverflow.com/questions/11194610/how-can-i-reorder-multi-indexed-dataframe-columns-at-a-specific-level
summary_globals = summary_globals.reindex(columns=summary_globals.columns.reindex(summary_statistics_globals, level=1)[0])
summary_cat_plans = summary_cat_plans.reindex(columns=summary_cat_plans.columns.reindex(summary_statistics_cat_plans, level=1)[0])

summary_globals = summary_globals.reorder_levels(HEADER_ORDER, axis=0)
summary_cat_plans = summary_cat_plans.reorder_levels((*HEADER_ORDER, "AL"), axis=0)

#########################################################################################################################################################################################
######## Tests of statistical significance
#########################################################################################################################################################################################
##      - The p-value, is a measure of the significance or confidence in the difference between the measurements in two different samples (data sets).
##        If the p-value is statistically significant, the values in one sample are more likely to be larger than the values in the other sample.
##          - A p-value less than 0.05 is statistically significant, and indicates strong evidence against the null hypothesis.
##            Therefore, the null hypothesis (that there's no difference between the medians of the samples) is rejected, and significant support for the alternative hypothesis (that a significant difference does exist) exists.
##            Note that this does not mean that the alternative is accepted, i.e. it does not prove that the data are different, only that there is a sufficiently low chance (less than 5%) that the difference in the data was caused by random chance.
##          - A p-value greater than 0.05 is not statistically significant, and indicates evidence for the null hypothesis. The null hypothesis is retained, and the alternative hypothesis rejected.
##      - https://www.simplypsychology.org/p-value.html#:~:text=A%20p%2Dvalue%20less%20than,and%20accept%20the%20alternative%20hypothesis.
##      - https://blog.minitab.com/en/understanding-statistics/what-can-you-say-when-your-p-value-is-greater-than-005

## Global comparisons (comparisons simultaneously over all data sets)
global_comparison_statistics = {"Score Kruskal" : kruskal,
                                "Score Friedman Chi-Square" : friedmanchisquare,
                                "Fligner" : fligner}
global_comparison_matrix = pandas.DataFrame(index=list(global_comparison_statistics.keys()),
                                            columns=["result"])

## TODO The rows should have the compare only same on them;
##      - So we can say, for configurations with the same X, then there is a significant difference between different Y,
##      - For a given problem, there is a significant difference in the performance by changing search mode



for comparison_statistic, comparison_function in global_comparison_statistics.items():
    print(f"\nProcessing {comparison_statistic}...")
    
    for statistic in summary_statistics_globals:
        comparison = comparison_function(*[combined_data_sets[configuration]["Globals"][statistic].to_list() for configuration in combined_data_sets])
        global_comparison_matrix.loc[comparison_statistic,"result"] = comparison.pvalue

print(global_comparison_matrix)

## Construct a dataframe that acts as a matrix of all possible pair-wise configuration comparisons;
##      - There is a multi-index on both the rows and columns to compare all pair-wise differences,
##      - Result sets that are combined are dropped from both rows and columns and are taken as the mean over all results in those sets.
pair_wise_comparison_statistics = {"Score Ranksums" : ranksums,
                                   "Score Wilcoxon" : functools.partial(wilcoxon, zero_method="zsplit", mode="approx")}
rows_index = pandas.MultiIndex.from_tuples(((*configuration, comparison)
                                            for configuration in data_sets.keys()
                                            for comparison in pair_wise_comparison_statistics.keys()),
                                           names=(*configuration_headers, "comparison"))
columns_index = pandas.MultiIndex.from_tuples(((*configuration, statistic)
                                               for configuration in data_sets.keys()
                                               for statistic in summary_statistics_globals),
                                              names=(*configuration_headers, "result"))
pair_wise_data_set_comparison_matrix = pandas.DataFrame(index=rows_index, columns=columns_index)
pair_wise_data_set_comparison_matrix = pair_wise_data_set_comparison_matrix.sort_index(axis=0, level=cli_args.sort_index_values).sort_index(axis=1, level=cli_args.sort_index_values)

## Make a list of all the desired pair-wise configuration comparisons
compare_configurations: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
for row_configuration, column_configuration in itertools.permutations(data_sets.keys(), r=2):
    ignore: bool = False
    for index, level_name in enumerate(configuration_headers):
        if ((level_name in cli_args.compare_only_different
             and row_configuration[index] == column_configuration[index])
            or (level_name in cli_args.compare_only_same
                and row_configuration[index] != column_configuration[index])):
            ignore = True; break
    if not ignore:
        compare_configurations.append((row_configuration, column_configuration))

## For each comparison statistic...
for comparison_statistic, comparison_function in pair_wise_comparison_statistics.items():
    print(f"\nProcessing {comparison_statistic}...")
    
    ## For each pair-wise configuration comparison...
    for row_configuration, column_configuration in compare_configurations:
        
        ## Compare all the summary statistics
        for statistic in summary_statistics_globals:
            comparison = comparison_function(combined_data_sets[row_configuration]["Globals"][statistic].to_list(),
                                             combined_data_sets[column_configuration]["Globals"][statistic].to_list())
            pair_wise_data_set_comparison_matrix.loc[(*row_configuration, comparison_statistic), (*column_configuration, statistic)] = comparison.pvalue

pair_wise_data_set_comparison_matrix = pair_wise_data_set_comparison_matrix.reorder_levels((*HEADER_ORDER, "comparison"), axis=0)

#########################################################################################################################################################################################
######## Tests of trends
#########################################################################################################################################################################################

## Calculate fitness to linear trend for step-wise grounding time and exponential trend for step-wise solving and total time
##      - This should be split for multiple partial problems.



## Calculate fitness to linear trend for index-wise total number of achieved sub-goal stages



## Calculate sub-plan/refinement tree balancing; NAE of spread of matching child steps, expansion deviation and balance, balance score



## Calculate partial problem balancing; NAE of spread of division steps and variance in length of partial plans



#########################################################################################################################################################################################
######## Excel Outputs
#########################################################################################################################################################################################

## Open a new output excel workbook to save the collated data to;
##      - https://pbpython.com/excel-file-combine.html
##      - https://xlsxwriter.readthedocs.io/working_with_pandas.html
writer = pandas.ExcelWriter(f"{cli_args.output_path}.xlsx", engine="xlsxwriter") # pylint: disable=abstract-class-instantiated
out_workbook: xlsxwriter.Workbook = writer.book

################################################################
######## Summary tables

summary_globals.to_excel(writer, sheet_name="Globals Summary")
summary_cat_plans.to_excel(writer, sheet_name="Cat Plan Summary")

## TODO The graph should probably be of the medians, with IQR as error bars
# worksheet_globals = writer.sheets["Globals Comparison"]

# ## Create a chart object
# chart = out_workbook.add_chart({"type" : "column"})

# ## Get the dimensions of the dataframe
# max_row, max_col = quantiles_globals.shape

# index_levels: int = quantiles_globals.index.nlevels
# last_index_cell: str = chr(ord('@') + index_levels)
# ql_score: str = chr(ord('@') + (index_levels + quantiles_globals.columns.get_loc("QL_SCORE") + 1))
# ti_score: str = chr(ord('@') + (index_levels + quantiles_globals.columns.get_loc("TI_SCORE") + 1))
# grade: str = chr(ord('@') + (index_levels + quantiles_globals.columns.get_loc("GRADE") + 1))

# ## Configure the series of the chart from the dataframe data
# chart.add_series({"values" : f"='Globals Comparison'!${ql_score}$2:${ql_score}${max_row}",
#                   "categories" : f"='Globals Comparison'!$A$2:${last_index_cell}${max_row + 1}",
#                   "name" : f"='Globals Comparison'!${ql_score}$1:${ql_score}$1"})

# ## Insert the chart into the worksheet
# chart.set_size(1000, 1000) ## TODO Calculate a reasonable chart size
# worksheet_globals.insert_chart(max_col + 2, 2, chart)

## TODO Put conditional formatting for scores with coloured bar
#  {"type" : "3_color_scale",
#   "max_value" : 1.0,
#   "min_value" : 0.0,
#   "max_color" : "red",
#   "min_color" : "green"})

################################################################
######## Tests of significant differences between data sets

pair_wise_data_set_comparison_matrix.to_excel(writer, sheet_name="Pair-wise Comparisons")
worksheet = writer.sheets["Pair-wise Comparisons"]

## Get the dimensions of the dataframe
min_row, min_col = len(configuration_headers) + 2, len(configuration_headers) + 1
max_row, max_col = pair_wise_data_set_comparison_matrix.shape

## Add formatting to the excel spreadsheet;
##      - Colour green iff the p value is less than 0.05 (indicating the difference between the compared combined data sets is statistically significant),
##      - Colour red iff the p value is less than 0.05 (indicating the difference between the compared combined data sets is not statistically significant),
##      - conditional_format(first_row, first_col, last_row, last_col, options)
##          - https://xlsxwriter.readthedocs.io/format.html#format
##          - https://xlsxwriter.readthedocs.io/workbook.html#add_format
##          - https://xlsxwriter.readthedocs.io/working_with_conditional_formats.html#working-with-conditional-formats
significant = out_workbook.add_format({"bg_color" : "#37FF33"})
insignificant = out_workbook.add_format({"bg_color" : "#FF294A"})
worksheet.conditional_format(min_row, min_col, min_row + max_row - 1, min_col + max_col - 1,
                             {"type" : "cell", "criteria" : "less than",
                              "value" : 0.05, "format" : significant})
worksheet.conditional_format(min_row, min_col, min_row + max_row - 1, min_col + max_col - 1,
                             {"type" : "cell", "criteria" : "greater than",
                              "value" : 0.05, "format" : insignificant})

################################################################
######## Overall quantiles over combined data sets

quantiles_globals.to_excel(writer, sheet_name="Globals Comparison", merge_cells=False)
quantiles_cat_plans.to_excel(writer, sheet_name="Cat Plan Comparison", merge_cells=False)

## Save the workbook
writer.save()

#########################################################################################################################################################################################
######## Latex table and pgfplots graph outputs
#########################################################################################################################################################################################
######## All results are given as medians, with IQR used as represenation of variance.

################################################################
######## Summary tables

summary_globals.to_latex(f"{cli_args.output_path}_Globals_2NSummary.tex")
summary_cat_plans.to_latex(f"{cli_args.output_path}_CatPlan_2NSummary.tex")
pair_wise_data_set_comparison_matrix.to_latex(f"{cli_args.output_path}_TestOfSignificance.tex")

################################################################
######## Graph plotting setup

als = numpy.arange(al_range.stop)
bars: int = 1
padding: float = 0.10
bar_width: float = (1.0 / bars) - (padding / bars)

bar_width = 0.19 # bar_width(bars=5, pad=0.01)
# def bar_width(bar: int, tbars: int, pad: float) -> float:
#     return ((1.0 / tbars) - pad) * (-((tbars/2) - 0.5 + 1) + bar)

def set_bars(bars: int) -> None:
    "Set the number of bars in the current plot."
    bars = bars
    global bar_width
    bar_width = (1.0 / bars) - (padding / bars)

def get_cat_plans(statistic: str) -> dict[str, Any]:
    return {"height" : quantiles_cat_plans.query("statistic == 0.5")[statistic],
            "yerr" : (quantiles_cat_plans.query("statistic == 0.25")[statistic], quantiles_cat_plans.query("statistic == 0.75")[statistic]),
            "capsize" : 5}

## This would have to be done with a sub-plot for each of the configuration;
##      - Add options;
##          - Seperate onto different plots,
# quantiles_cat_plans.loc[quantiles_cat_plans.index.get_level_values("statistic") == 0.5,"GT"].unstack(level=configuration_headers).plot(kind="bar", subplots=True, rot=0, figsize=(9, 7), layout=(6, 6))

################################################################
######## Bar charts for plan quality
figure_quality_abs_bars, axis_quality_abs_bars = pyplot.subplots() # Median of cat plans
figure_quality_score_bars, axis_quality_score_bars = pyplot.subplots() # Median of globals
figure_quality_score_histogram, axis_quality_score_histogram = pyplot.subplots() # All of globals



################################################################
######## Bar charts for planning time
figure_time_raw_bars, axis_time_raw_bars = pyplot.subplots() # Median of cat plans
figure_time_scatter, axis_time_scatter = pyplot.subplots() # Median of cat plans, show contribution of solving and grounding time to total time in percent
figure_time_agg_bars, axis_time_agg_bars = pyplot.subplots() # Median of globals
figure_time_score_bars, axis_time_score_bars = pyplot.subplots() # Median of globals
figure_quality_score_histogram, axis_quality_score_histogram = pyplot.subplots() # All of globals

## Raw planning time per abstraction level;
##      - Solving time, grounding time, total time, yield time, completion time.
set_bars(5)
##          - Combine as series on same plot.
gt = get_cat_plans("GT")["height"]
axis_time_raw_bars.bar(als - (bar_width * 2), width=bar_width, **get_cat_plans("GT"), label="Median Grounding Time")
axis_time_raw_bars.bar(al_range - bar_width, quantiles_cat_plans["ST"], bar_width, yerr=get_std("ST"), capsize=5, label="Mean Solving")
axis_time_raw_bars.bar(al_range, means["TT"], bar_width, yerr=get_std("TT"), capsize=5, label="Mean Total")
axis_time_raw_bars.bar(al_range + bar_width, quantiles_cat_plans["LT"], bar_width, yerr=get_std("LT"), capsize=5, label="Mean Latency")
axis_time_raw_bars.bar(al_range + (bar_width * 2), quantiles_cat_plans["CT"], bar_width, yerr=get_std("CT"), capsize=5, label="Mean Completion")

## Aggregate ground-level planning times;
##      - Latency time, absolution time, average non-initial wait time, average minimum execution time per action.



## Overall time scores;
##      - Latency time score, absolution time score, average non-initial wait time score, average minimum execution time per action score.



################################################################
######## Bar charts for required memory
# figure_memory_bars, axis_memory_bars = pyplot.subplots()



################################################################
######## Bar charts for expansion factors and sub/partial-plan balance
# figure_expansion_raw_bars, axis_expansion_raw_bars = pyplot.subplots() # Cat plans
# figure_spbalance_raw_bars, axis_spbalance_raw_bars = pyplot.subplots() # Cat plans

## Raw sub/partial-plan expansions;
##      - Expansion factor per level, sub-plan expansion deviation, sub-plan expansion balance, partial-plan expansion deviation, partial-plan expansion balance.



## Sub/partial-plan balance/matching child distribution/spread scores;
##      - Sub-plan expansion balance score, partial-plan expansion balance score, matching-child step normalised mean absolute error score, division step normalised mean absolute error score



################################################################
########



# configuration = next(iter(combined_data_sets))
# time_score = combined_data_sets[configuration]["Globals"]["HA_T"]
# axis.hist(time_score, 50, (0.0, 15.0))

## https://github.com/texworld/tikzplotlib
pyplot.show()
# tikzplotlib.clean_figure()
# tikzplotlib.save(f"{cli_args.output_path}_Globals_Plot.tex")

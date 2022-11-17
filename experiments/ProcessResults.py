###########################################################################
###########################################################################
## Script for generating tables and graphs for experimental results.     ##
## Copyright (C)  2021  Oliver Michael Kamperis                          ##
## Email: o.m.kamperis@gmail.com                                         ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## any later version.                                                    ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program. If not, see <https://www.gnu.org/licenses/>. ##
###########################################################################
###########################################################################

"""Script for generating tables and graphs for experimental results."""

from collections import defaultdict
import functools
import itertools
import os
import sys
from typing import Any, Optional, Sequence, Union
import pandas
import glob
import argparse
import tqdm
import xlsxwriter
from matplotlib import pyplot, figure
import tikzplotlib ## https://github.com/texworld/tikzplotlib
import seaborn as sns
import warnings
warnings.simplefilter(action="ignore", category=pandas.errors.PerformanceWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)
warnings.filterwarnings(action="error", message=".*catastrophic cancellation.*")

## Global data set comparison statistics;
##      - Problem with global comparisons, are that affect of one sample is not being seperable may make two others, that are statistically significant, seem like they are not.
##      - The Kruskal-Wallis H-test tests the null hypothesis that the population median of all of the groups are equal (it is a non-parametric version of ANOVA): https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
##      - The Friedman test tests the null hypothesis that repeated samples of the same individuals have the same distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html
##      - Fligner’s test tests the null hypothesis that all input samples are from populations with equal variances: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fligner.html
from scipy.stats import kruskal, friedmanchisquare, fligner

## Pair-wise data set comparison statistics;
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ranksums.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
##      - https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
##      - Test the null hypothesis that two or more samples come from populations with the same median: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_test.html
##      - https://stats.stackexchange.com/questions/558814/actual-difference-between-the-statistic-results-from-scipy-stats-ranksums-and-sc
##      - https://stats.stackexchange.com/questions/91034/what-is-the-difference-between-the-wilcoxon-srank-sum-test-and-the-wilcoxons-s
##          - Use the Mann-Whitney-Wilcoxon ranked sum test (ranksums) when the data are not paired (independent),
##            e.g. comparing performance of differnt configurations on different problems.
##          - Use the Mann-Whitney-Wilcoxon signed rank test (wilcoxon) when the data are paired/related,
##            e.g. comparing performance of different configurations on the same problem, or the same configuration for different problems.
from scipy.stats import ranksums, wilcoxon, median_test

## Individual data set statistics;
##      - Test whether a sample differs from a normal distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html
##      - Test whether the skew is different from the normal distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skewtest.html
##      - Test whether a dataset has normal kurtosis: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosistest.html
from scipy.stats import normaltest, skewtest, kurtosistest

## Tests of colleration;
##      - The Pearson correlation coefficient measures the linear relationship between two datasets,
##        a test of the null hypothesis that the distributions underlying the samples are uncorrelated and normally distributed (the alternative being that the correlation is nonzero assuming alternative="two-sided"):
##        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
##      - The Spearman rank-order correlation coefficient is a nonparametric measure of the monotonicity of the relationship between two datasets,
##        unlike the Pearson correlation, the Spearman correlation does not assume that both datasets are normally distributed:
##        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
##      - Use non-linear least squares to fit a function, f, to data:
##        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
from scipy.stats import pearsonr, spearmanr
from scipy.optimize import curve_fit

#########################################################################################################################################################################################
######## Build the raw data sets
#########################################################################################################################################################################################

def mapping_argument_factory(key_choices: Optional[list[str]] = None, allow_multiple_values: bool = True) -> type:
    """Construct a special action for storing arguments of parameters given as a mapping."""   
    
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
            print(f"Error during parsing mapping argument '{option_string}' for key-value mapping '{key_value}': {error}.")
            raise error
        setattr(namespace, self.dest, _values)
    
    return type("StoreMappingArgument", (argparse.Action,), {"__call__" : __call__,
                                                             "key_choices" : key_choices.copy() if key_choices is not None else None,
                                                             "allow_multiple_values" : allow_multiple_values})

## Command line arguments parser
parser = argparse.ArgumentParser()
bool_options = lambda input: not input.casefold() == "false"
parser.add_argument("input_paths", nargs="*", default=["./"], type=str, help="Paths to the input directory or file(s).")
parser.add_argument("-out", "--output_path", required=True, type=str, help="Path to the output directory.")
parser.add_argument("-p", "--pause", default=True, type=bool_options, help="Pause after each phase.")
parser.add_argument("-filter", nargs="+", default=None, action=mapping_argument_factory(), type=str,
                    metavar="header=value_1,value_2,[...]value_n", help="Filter the data set by the given header and values.")
parser.add_argument("-combine", "--combine_on", nargs="*", default=[], type=str, help="Combine data sets that have the same value for the given headers, by removing the given headers, the result is an average over the given headers.")
parser.add_argument("-order", "--order_index_headers", nargs="*", default=[], type=str, help="Specify the order of configuration headers.")
parser.add_argument("-sort", "--sort_index_values", nargs="*", default=[], type=str, help="Sort the data by the values of the given configuration headers.")
parser.add_argument("-diff", "--compare_only_different", nargs="*", default=[], type=str, help="Compare only data sets that have different values for the given headers.")
parser.add_argument("-same", "--compare_only_same", nargs="*", default=[], type=str, help="Compare only data sets that have the same values for the given headers.")
parser.add_argument("-graphs", "--make_plots", default=True, type=bool_options, help="Make plots of the data.")
parser.add_argument("-show", "--show_plots", default=True, type=bool_options, help="Show the plots.")
parser.add_argument("-breakf", "--break_first", default="planning_mode", type=str, help="Break the style or colour of all chart plots on the given header. "
                                                                                        "For example, for a bar chart, there will be a bar for each x-axis label for each unique value of the given header.")
parser.add_argument("-breaks", "--break_second", default="problem", type=str, help="For globals plot the given header over the x-axis."
                                                                                   "There will be an x-axis label for each unique value of the given header."
                                                                                   "For level-wise plots, the x-axis is the abstraction level, so the unique values for the header are broken into seperate plots on the same figure.")
parser.add_argument("-actions", "--include_actions", default=True, type=bool_options, help="Include the actions in the tables and plots.")
parser.add_argument("-overhead", "--include_overhead", default=True, type=bool_options, help="Include the overhead time in the tables and plots.")
parser.add_argument("-percent_classical", "--include_percent_classical", default=True, type=bool_options, help="Include the raw time values are a percent of the classical time for the same problem in the tables and plots. This fails if no classical configurations are included or the data is combined on the planning mode or problem.")
parser.add_argument("-problem_wise", "--include_problem_wise_breakdown", default=True, type=bool_options, help="Include the problem-wise data in the tables and plots. Fails if any data set included is classical and therefore contains no partial-plans.")
cli_args: argparse.Namespace = parser.parse_args()

def get_option_list(option_list: list[str]) -> str:
    """List the options given by the user for a particular parameter."""
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
print("Make plots: " + str(cli_args.make_plots), end="\n\n")
print("Show plots: " + str(cli_args.show_plots), end="\n\n")
print("Break first on:\n\t" + cli_args.break_first, end="\n\n")
print("Break second on:\n\t" + cli_args.break_second, end="\n\n")

if (set(cli_args.order_index_headers) | set(cli_args.sort_index_values)) & set(cli_args.combine_on):
    print("Error: The headers given for the options 'order_index_headers' or 'sort_index_values' must not be the same as given for the option 'combine_on'.")
    sys.exit(1)
elif cli_args.combine_on == ["all"] \
    and ((set(cli_args.order_index_headers) | set(cli_args.sort_index_values)) \
         & (set(cli_args.compare_only_different) | set(cli_args.compare_only_same) | {cli_args.break_first, cli_args.break_second})):
    print("Error: If the option 'combine_on' is set to 'all', the headers given for the options 'order_index_headers' and 'sort_index_values' must be one of those given for 'compare_only_different', 'compare_only_same', 'break_first' or 'break_second'.")
    sys.exit(1)

if (set(cli_args.compare_only_different) | set(cli_args.compare_only_same)) & set(cli_args.combine_on):
    print("Error: The headers given for the options 'compare_only_different' or 'compare_only_same' must not be the same as given for the option 'combine_on'.")
    sys.exit(1)

if {cli_args.break_first, cli_args.break_second} & set(cli_args.combine_on):
    print("Error: The headers given for the options 'break_first' and 'break_second' must not be the same as given for the option 'combine_on'.")
    sys.exit(1)

if cli_args.pause:
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
configuration_headers: list[str] = ["problem",          # The problem instance; e.g. PS1, PL2, etc.
                                    "planning_type",    # The planning type; mcl, hcl, hcr.
                                    "planning_mode",    # The planning mode; classical, offline, online.
                                    "strategy",         # The division strategy; e.g. basic, hasty, steady, etc.
                                    "bound_type",       # The bound type; abs, per, sl, cumt.
                                    "online_bounds",    # The online bounds; a vector of numbers.
                                    "search_mode",      # The search mode; standard, min_bound, yield.
                                    "achievement_type", # The sub-goal achievement type; sima, seqa.
                                    "action_planning",  # The action planning type; simultaneous, sequential.
                                    "preach_type",      # The final-goal pre-emptive achievement type; heur, opt.
                                    "blend_direction",  # The blend direction; left, right.
                                    "blend_type",       # The blend type; abs, per.
                                    "blend_quantity",   # The blend quantity; a number.
                                    "online_method"]    # The online method; ground-first, complete-first, hybrid.

if cli_args.combine_on == ["all"]:
    _new_configuration_headers: list[str] = []
    allowed_headers: set[str] = set(cli_args.compare_only_different) | set(cli_args.compare_only_same) | {cli_args.break_first, cli_args.break_second}
    for header in configuration_headers:
        if header in allowed_headers:
            _new_configuration_headers.append(header)
    configuration_headers = _new_configuration_headers
else:
    for combine in cli_args.combine_on:
        configuration_headers.remove(combine)

def extract_configuration(excel_file_name: str) -> Optional[list[str]]:
    """Extract the data set configuration for a given excel file name."""
    configuration_dict: dict[str, str] = {}
    raw_config: str = os.path.basename(excel_file_name).strip("ASH_Excel_").lower().split(".")[0]
    terms: list[str] = raw_config.split("_")
    
    for index, term in enumerate(terms):
        if term in ["mcl", "hcl", "hcr"]:
            planning_type_index = index
            break
    
    configuration_dict["problem"] = "".join(terms[0:planning_type_index])
    configuration_dict["planning_type"] = terms[planning_type_index]
    
    if configuration_dict["planning_type"] in ["mcl", "hcl"]:
        configuration_dict["planning_mode"] = "classical"
        for header in configuration_headers:
            if header not in ["problem", "planning_type", "planning_mode"]:
                configuration_dict[header] = "NONE"
        
    else:
        index: int = 1
        
        def get_term(matches: Optional[list[str]] = None, default: str = "NONE") -> str:
            """Get a planning configuration term from the file name."""
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
            configuration_dict["bound_type"] = get_term(["abs", "per", "sl", "cumt", "inct", "dift", "intt"], "abs")
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
            configuration_dict["search_mode"] = configuration_dict["search_mode"] + get_term("bound")
        configuration_dict["achievement_type"] = get_term(["seqa", "sima"], "seqa")
        
        if get_term(["conc"]) == "conc":
            configuration_dict["action_planning"] = "concurrent"
        else: configuration_dict["action_planning"] = "sequential"
        
        if configuration_dict["planning_mode"] == "online":
            if get_term(["preach"]) == "preach":
                configuration_dict["preach_type"] = get_term(["heur", "opt"], "opt")
            else: configuration_dict["preach_type"] = "NONE"
            
            if get_term(["blend"]) == "blend":
                configuration_dict["blend_direction"] = get_term(["left", "right"], "right")
                
                blend: str = get_term()
                configuration_dict["blend_type"] = blend[0]
                configuration_dict["blend_quantity"] = int(blend[1:])
            else:
                configuration_dict["blend_direction"] = "NONE"
                configuration_dict["blend_type"] = "NONE"
                configuration_dict["blend_quantity"] = "NONE"
            
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
##      - Mapping: configuration set (row index), property (worksheet name) -> list of data frames
data_sets: dict[tuple[str, ...], dict[str, list[pandas.DataFrame]]] = defaultdict(dict)

## Iterate over all directory paths and all excel files within them
files_loaded: int = 0
for path in cli_args.input_paths:
    print(f"\nLoading files from path {path} ...")
    
    for excel_file_name in tqdm.tqdm(glob.glob(f"{path}/ASH_Excel*.xlsx")):
        
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
            worksheets: dict[str, pandas.DataFrame]
            if "classical" in configuration:
                worksheets = pandas.read_excel(excel_file, ["Globals", "Cat Plans", "Concat Step-wise"])
            else: worksheets = pandas.read_excel(excel_file, ["Globals", "Cat Plans", "Partial Plans", "Concat Step-wise", "Concat Index-wise"])
            
            ## Globals is not nicely formatted so some extra work is needed to extract it;
            ##      - Get the rows were all the entries are null,
            ##      - Get the index over those rows,
            ##      - Clip the dataframe to include only elements up to but excluding the first null row.
            null_rows: pandas.Series = worksheets["Globals"].isnull().all(axis=1)
            null_rows_index: pandas.Index = worksheets["Globals"].index[null_rows]
            worksheets["Globals"] = worksheets["Globals"][:null_rows_index.values[0]]
            
            ## Some of the early classical planning files don't have the time score in globals.
            if "TI_SCORE" not in worksheets["Globals"]:
                worksheets["Globals"].insert(worksheets["Globals"].columns.get_loc("AME_PA_SCORE") + 1,
                                             "TI_SCORE", worksheets["Globals"]["HA_SCORE"])
            
            ## Calculate the percentage of the total time spent in grounding, solving, and overhead;
            ##      - These define the relative complexity of;
            ##          - Grounding the logic program (complexity of representing the size of the problem),
            ##          - Solving the logic program (complexity of searching for a solution to the problem of minimal length),
            ##          - The overhead in terms of the time taken to make reactive decisions during search.
            time_types: list[str] = ["GT", "ST", "OT"]
            for sheet_name in (["Cat Plans", "Partial Plans"] if "classical" not in configuration else ["Cat Plans"]):
                for time_type in reversed(time_types):
                    worksheets[sheet_name].insert(worksheets[sheet_name].columns.get_loc("OT") + 1,
                                                  f"{time_type}_POTT", worksheets[sheet_name][time_type] / worksheets[sheet_name]["TT"])
            
            for sheet_name in worksheets:
                ## Get rid of old index data
                worksheets[sheet_name] = worksheets[sheet_name].drop(["Unnamed: 0"], axis="columns")
                
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
    new_configuration = tuple(header for index, header in enumerate(configuration) if index not in none_header_indices)
    new_data_sets[new_configuration] = data_sets[configuration]

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
print(f"Configuration headers:\n\t{configuration_headers}\n")
print("Data sets:\n\t" + "\n\t".join(repr(configuration) for configuration in data_sets))

if cli_args.pause:
    input_: str = input("\nProceed? [(y)/n]: ")
    if input_ == "n": exit()

#########################################################################################################################################################################################
######## Process the raw data sets
#########################################################################################################################################################################################

## Main dataframes storing the processed data;
##      - The first combines each data set that fits a given configuration into a single dataframe for each sheet,
##      - The second combines all the configurations into a single dataframe for each sheet,
##      - The third takes the mean over all data sets in the configuartion of the quantiles over each run of each data set and makes a list of the different configurations (these are then concatenated below to form the seven-number summaries).
combined_data_sets: dict[tuple[str, ...], dict[str, pandas.DataFrame]] = defaultdict(dict)
fully_combined_data_sets: dict[str, pandas.DataFrame] = {}
combined_data_sets_quantiles: dict[str, list[pandas.DataFrame]] = defaultdict(list)

## For each data set, add a row to the dataframe with column entries for each comparison level for that set
print("\nProcessing raw data sets...")
for configuration, combined_data_set in tqdm.tqdm(data_sets.items()):
    
    quantiles_for_data_set: dict[str, list[pandas.DataFrame]] = defaultdict(list)
    data_set: dict[str, list[pandas.DataFrame]] = defaultdict(list)
    
    for sheet_name in combined_data_set:
        make_quantiles: bool = sheet_name in ["Globals", "Cat Plans", "Partial Plans"]
        
        index_for_data_set: list[str]
        if sheet_name in ["Cat Plans", "Partial Plans", "Concat Step-wise", "Concat Index-wise"]:
            index_for_data_set = configuration_headers + ["AL", "statistic"]
        elif sheet_name == "Globals":
            index_for_data_set = configuration_headers + ["statistic"]
        
        ## For each individual data set in this configuration...
        individual_data_set: pandas.DataFrame
        for individual_data_set in combined_data_set[sheet_name]:
            
            ## Calculate the quantiles for this data set
            data_quantiles: pandas.DataFrame
            if sheet_name in ["Cat Plans", "Partial Plans"]:
                data_quantiles = individual_data_set.drop(["RU"], axis="columns").groupby("AL").quantile([0.0, 0.25, 0.50, 0.75, 1.0])
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
               
            elif sheet_name == "Globals":
                data_quantiles = individual_data_set.drop(["RU"], axis="columns").quantile([0.0, 0.25, 0.50, 0.75, 1.0])
                data_quantiles = data_quantiles.rename_axis("statistic")
                data_quantiles.loc["IQR",:] = (data_quantiles.loc[0.75] - data_quantiles.loc[0.25]).values
                data_quantiles.loc["Range",:] = (data_quantiles.loc[1.0] - data_quantiles.loc[0.0]).values
            
            ## Insert columns to define the configurations,
            ## then append those columns to the index (the abstraction level and aggregate statistic is also part of the index)
            for index, level_name in enumerate(configuration_headers):
                individual_data_set.insert(index, level_name, configuration[index])
                if make_quantiles: data_quantiles.insert(index, level_name, configuration[index])
            individual_data_set = individual_data_set.set_index(configuration_headers)
            if make_quantiles: data_quantiles = data_quantiles.set_index(configuration_headers, append=True)
            
            ## Set the order of the index levels;
            ##      - Configurations comes first, then abstraction level for concatenated plans, then the statistic.
            individual_data_set = individual_data_set.reorder_levels(configuration_headers)
            if make_quantiles: data_quantiles = data_quantiles.reorder_levels(index_for_data_set)
            
            ## Append the data quantiles for the current data set to the list
            data_set[sheet_name].append(individual_data_set)
            if make_quantiles: quantiles_for_data_set[sheet_name].append(data_quantiles)
        
        ## Concatenate (combine) all the data sets for the current configuration
        combined_data_sets[configuration][sheet_name] = pandas.concat(data_set[sheet_name]).astype(float)
        
        ## Take the average of the quantiles over the all the individual data sets for the current configuration
        if make_quantiles: combined_data_sets_quantiles[sheet_name].append(pandas.concat(quantiles_for_data_set[sheet_name]).astype(float).groupby(index_for_data_set).mean())

#########################################################################################################################################################################################
######## Generate the fully combined data sets
#########################################################################################################################################################################################

for sheet_name in ["Globals", "Cat Plans", "Partial Plans", "Concat Step-wise", "Concat Index-wise"]:
    to_concat = [combined_data_sets[configuration][sheet_name]
                 for configuration in combined_data_sets
                 if ("classical" not in configuration
                     or sheet_name not in ["Partial Plans", "Concat Index-wise"])]
    if to_concat:
        fully_combined_data_sets[sheet_name] = pandas.concat(to_concat).reset_index()

## Calculate "smoothness" of expansion factor across the hierarchy;
##      - Calculate over "Cat Plans" and insert into "Globals",
##      - Average expansion factor: af = root(top-level - 1, ground-level plan length / top-level plan length)
##      - Smoothest descent plan length: sdpl = top-level plan length * af ^ (top-level - level)
##      - Plan length percentage difference: pld = (plan length / sdpl) - 1
##      - Hierarchical smoothness score: hs = statistics.mean(abs(pld) for level in levels) / af
##      - Adjusted depth of plan length per level: adpl = top-level - math.log(plan length at level / top-level plan length, af)

## TODO

#########################################################################################################################################################################################
######## Generate the seven-number summaries for plotting results - (all the quantiles, the IQR and the range)
#########################################################################################################################################################################################

## Concatenate all the individual quantile data set frames into single dataframes.
quantiles_globals: pandas.DataFrame = pandas.concat(combined_data_sets_quantiles["Globals"])
quantiles_cat_plans: pandas.DataFrame = pandas.concat(combined_data_sets_quantiles["Cat Plans"])
al_range = range(1, quantiles_cat_plans.index.get_level_values("AL").max() + 1)

#########################################################################################################################################################################################
######## Generate the two-number summaries for tabulating results - (The Median and the IQR)
#########################################################################################################################################################################################

## The minimal summary statistics to compare
summary_statistics_globals: list[str] = ["QL_SCORE", "TI_SCORE", "GRADE"]
summary_statistics_ground_level: list[str] = ["GT", "ST", "LT", "CT", "LE"] ## TODO: This is a 1N summary. Add options: --include_actions, --include_overhead_time
summary_statistics_cat_plans: list[str] = ["LE", "AC", "CF", "CP_EF_L",
                                           "GT", "ST", "OT",
                                           "GT_POTT", "ST_POTT", "OT_POTT",
                                           "TT", "LT", "WT", "MET", "CT"]

## Construct a dataframe including just the medians and IQR for all data sets (combined configurations);
##      - The row index headers are the combined configuration headers, sorted according to user input,
##      - The outer columns headers are the median and IQR,
##      - For globals; The inner column headers are the "global summary statistics"; (quality score, time score, and grade),
##      - For cat plans; The inner column headers are the abstraction levels, and the "cat plan summary statistics".
summary_globals: pandas.DataFrame = quantiles_globals.query("statistic in [0.5, 'IQR']")[summary_statistics_globals].unstack("statistic").reorder_levels(HEADER_ORDER, axis=0)
summary_cat_plans: pandas.DataFrame = quantiles_cat_plans.query("statistic in [0.5, 'IQR']")[summary_statistics_cat_plans].unstack("statistic").reorder_levels((*HEADER_ORDER, "AL"), axis=0)
summary_globals_1N_stacked = quantiles_globals.query("statistic == 0.5")[summary_statistics_globals].droplevel("statistic").reorder_levels(HEADER_ORDER, axis=0).unstack(cli_args.break_second).swaplevel(0, 1, axis=1).sort_index(axis=1, level=1)

## Construct a dataframe that groups the fully combined data based on the break headers and the run number.
fully_combined_data_sets_grouped = fully_combined_data_sets["Cat Plans"].groupby([cli_args.break_first, cli_args.break_second, "RU"])
fully_combined_data_sets_ground_level_grouped = fully_combined_data_sets["Cat Plans"].query("AL == 1").groupby([cli_args.break_first, cli_args.break_second])

## Construct a datafrace containing the sum of the grounding, solving, overhead, and total times to the ground level.
fully_combined_data_sets_cat_plans_time_sums = fully_combined_data_sets_grouped[["GT", "ST", "OT", "TT"]].sum()
for time_type in ["GT", "ST", "OT"]:
    fully_combined_data_sets_cat_plans_time_sums[f"{time_type}_POTT"] = fully_combined_data_sets_cat_plans_time_sums[time_type] / fully_combined_data_sets_cat_plans_time_sums["TT"]

## Construct a dataframge containing the raw ground-level statistics.
summary_raw_ground_level: pandas.DataFrame = pandas.merge(fully_combined_data_sets_cat_plans_time_sums.droplevel("RU").groupby([cli_args.break_first, cli_args.break_second])[["GT", "ST"]].median(), fully_combined_data_sets_ground_level_grouped[["LT", "WT", "MET", "CT", "LE"]].median(), left_index=True, right_index=True)
summary_raw_ground_level = summary_raw_ground_level.reorder_levels(HEADER_ORDER, axis=0)
summary_raw_ground_level_stacked = summary_raw_ground_level[["GT", "ST", "LT", "CT", "LE"]].unstack(cli_args.break_second).swaplevel(0, 1, axis=1).sort_index(axis=1, level=1)

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

print("\nProcessing global comparison statistics...")

## Global comparisons (comparisons simultaneously over all data sets)
global_comparison_statistics = {"Score Kruskal" : kruskal,
                                "Score Friedman Chi-Square" : friedmanchisquare,
                                "Fligner" : fligner}
global_comparison_matrix = pandas.DataFrame(index=list(global_comparison_statistics.keys()),
                                            columns=summary_statistics_globals)

## The rows have the compare only same on them;
##      - So we can say, for configurations with the same X, then there is a significant difference between different Y,
##      - For a given problem, there is a significant difference in the performance by changing search mode
for comparison_statistic, comparison_function in global_comparison_statistics.items():
    print(f"\t- Processing {comparison_statistic}...")
    
    for statistic in summary_statistics_globals:
        try:
            comparison = comparison_function(*[combined_data_sets[configuration]["Globals"][statistic].to_list()
                                               for configuration in combined_data_sets])
            pvalue = comparison.pvalue
        except ValueError:
            pvalue = 0.0
        global_comparison_matrix.loc[comparison_statistic,statistic] = pvalue

print("\nProcessing pair-wise comparison statistics...")

## Make a list of all the desired pair-wise configuration comparisons
compare_configurations: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
for row_configuration, column_configuration in itertools.permutations(combined_data_sets.keys(), r=2):
    ignore: bool = False
    for index, level_name in enumerate(configuration_headers):
        if ((level_name in cli_args.compare_only_different
             and row_configuration[index] == column_configuration[index])
            or (level_name in cli_args.compare_only_same
                and row_configuration[index] != column_configuration[index])):
            ignore = True; break
    if not ignore:
        compare_configurations.append((row_configuration, column_configuration))

## Construct a dataframe that acts as a matrix of all possible pair-wise configuration comparisons;
##      - There is a multi-index on both the rows and columns to compare all pair-wise differences,
##      - Result sets that are combined are dropped from both rows and columns and are taken as the mean over all results in those sets.
pair_wise_comparison_statistics = {"Score Ranksums" : ranksums,
                                   "Score Wilcoxon" : functools.partial(wilcoxon, zero_method="zsplit", mode="approx"),
                                   "Median Test" : median_test}
rows_index = pandas.MultiIndex.from_tuples(((*configuration, comparison)
                                            for configuration in combined_data_sets.keys()
                                            for comparison in pair_wise_comparison_statistics.keys()),
                                           names=(*configuration_headers, "comparison"))
columns_index = pandas.MultiIndex.from_tuples(((*configuration, statistic)
                                               for configuration in combined_data_sets.keys()
                                               for statistic in summary_statistics_globals),
                                              names=(*configuration_headers, "result"))
pair_wise_data_set_comparison_matrix = pandas.DataFrame(index=rows_index, columns=columns_index)
pair_wise_data_set_comparison_matrix = pair_wise_data_set_comparison_matrix.sort_index(axis=0, level=cli_args.sort_index_values).sort_index(axis=1, level=cli_args.sort_index_values)

## For each comparison statistic...
for comparison_statistic, comparison_function in pair_wise_comparison_statistics.items():
    print(f"\t- Processing {comparison_statistic}...")
    
    ## For each pair-wise configuration comparison...
    for row_configuration, column_configuration in compare_configurations:
        
        ## Compare all the summary statistics
        for statistic in summary_statistics_globals:
            row_ = combined_data_sets[row_configuration]["Globals"][statistic].to_list()
            column_ = combined_data_sets[column_configuration]["Globals"][statistic].to_list()
            if len(row_) == len(column_):
                try:
                    comparison = comparison_function(row_, column_)
                    pvalue = getattr(comparison, "pvalue", getattr(comparison, "p", -1.0))
                except ValueError:
                    pvalue = 0.0
            else: pvalue = -1.0 ## Indicates that the data sets are not the same length
            pair_wise_data_set_comparison_matrix.loc[(*row_configuration, comparison_statistic), (*column_configuration, statistic)] = pvalue

pair_wise_data_set_comparison_matrix = pair_wise_data_set_comparison_matrix.reorder_levels((*HEADER_ORDER, "comparison"), axis=0)

#########################################################################################################################################################################################
######## Tests of normality, skew and kurtosis
#########################################################################################################################################################################################

print("\nProcessing normality, skew and kurtosis statistics...")

skew_statistics = {"Normality-test" : normaltest,
                   "Skew-test" : skewtest,
                   "Kurtosis-test" : kurtosistest}
raw_statistics = ["BL_LE", "BL_AC", "EX_T", "HA_T", "AME_T", "AME_T_PA"] + summary_statistics_globals
rows_index = pandas.MultiIndex.from_tuples(((*configuration, comparison)
                                            for configuration in combined_data_sets.keys()
                                            for comparison in skew_statistics.keys()),
                                           names=(*configuration_headers, "test"))
skew_test_matrix = pandas.DataFrame(index=rows_index, columns=raw_statistics)
skew_test_matrix = skew_test_matrix.sort_index(axis=0, level=cli_args.sort_index_values)

## For each skew statistic...
for skew_statistic, skew_function in skew_statistics.items():
    print(f"\t- Processing {skew_statistic}...")
    
    ## For each configuration...
    for configuration in combined_data_sets.keys():
        
        ## Compare all the raw statistics
        for raw_statistic in raw_statistics:
            try:
                result = skew_function(combined_data_sets[configuration]["Globals"][raw_statistic].to_list())
                pvalue = result.pvalue
            except RuntimeWarning:
                pvalue = -1.0 ## Indicates catastrophic cancellation due to the data being nearly identical
            skew_test_matrix.loc[(*configuration, skew_statistic), raw_statistic] = pvalue

skew_test_matrix = skew_test_matrix.reorder_levels((*HEADER_ORDER, "test"), axis=0)

#########################################################################################################################################################################################
######## Tests of trends and correlation
#########################################################################################################################################################################################

## Calculate fitness to linear trend for step-wise grounding time, exponential trend for step-wise solving and total time, and linear trend for index-wise total number of achieved sub-goal stages;
##      - This should be split for multiple partial problems.

print("\nProcessing trend and correlation statistics...")

trend_statistics = {"pearson" : pearsonr,
                    "spearman" : spearmanr}
step_wise_statistics = ["C_GT", "C_ST", "C_TT", "C_TACHSGOALS", "C_CP_EF_L", "C_SP_ED_L", "C_SP_EB_L", "C_SP_EBS_L"]
rows_index = pandas.MultiIndex.from_tuples(((*configuration, comparison)
                                            for configuration in combined_data_sets.keys()
                                            for comparison in trend_statistics.keys()),
                                           names=(*configuration_headers, "test"))
trend_test_matrix = pandas.DataFrame(index=rows_index, columns=step_wise_statistics)
trend_test_matrix = trend_test_matrix.sort_index(axis=0, level=cli_args.sort_index_values)

## For each trend statistic...
for trend_statistic, trend_function in trend_statistics.items():
    print(f"\t- Processing {trend_statistic}...")
    
    ## For each configuration...
    for configuration in combined_data_sets.keys():
        
        ## Compare all the step-wise statistics
        for step_wise_statistic in step_wise_statistics:
            result = trend_function(combined_data_sets[configuration]["Concat Step-wise"].query("AL == 1")["SL"].to_list(),
                                    combined_data_sets[configuration]["Concat Step-wise"].query("AL == 1")[step_wise_statistic].to_list())
            trend_test_matrix.loc[(*configuration, trend_statistic), step_wise_statistic] = result.pvalue

trend_test_matrix = trend_test_matrix.reorder_levels((*HEADER_ORDER, "test"), axis=0)

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

summary_globals_1N_stacked.to_excel(writer, sheet_name="1N Score Summary")
summary_raw_ground_level_stacked.to_excel(writer, sheet_name="Raw 1N Summary")
## TODO: summary_raw_ground_level_as_percent_of_classical_stacked.to_excel(writer, sheet_name="1N Summary PC")
## TODO: Ground-level partial-plans 1N raw summary pivoted
## TODO: Ground-level partial-plans 1N raw summary pivoted, as percentage of total
## TODO: Ground-level partial-plans 1N raw summary pivoted, as percentage of offline
## TODO: Ground-level partial-plans 1N raw summary pivoted, as percentage of classical
summary_globals.to_excel(writer, sheet_name="Globals 2N Score Summary")
summary_cat_plans.to_excel(writer, sheet_name="Cat-Plan 2N Minimal Summary")

## Put conditional formatting on the scores
worksheet = writer.sheets["Globals 2N Score Summary"]
min_row, min_col = 2, len(configuration_headers) + 1
max_row, max_col = summary_globals.shape
worksheet.conditional_format(min_row, min_col, min_row + max_row - 1, min_col + max_col - 1,
                             {"type" : "3_color_scale",
                              "max_value" : 1.0,
                              "min_value" : 0.0,
                              "max_color" : "red",
                              "min_color" : "green"})

################################################################
######## Overall quantiles over combined data sets for each configuration

quantiles_globals.to_excel(writer, sheet_name="Globals 5N Full Summary", merge_cells=False)
quantiles_cat_plans.to_excel(writer, sheet_name="Cat Plan 5N Full Summary", merge_cells=False)

################################################################
######## Tests of significant differences between data sets

global_comparison_matrix.to_excel(writer, sheet_name="Global Score Sig-Diff")
pair_wise_data_set_comparison_matrix.to_excel(writer, sheet_name="Pair-wise Score Sig-Diff")
skew_test_matrix.to_excel(writer, sheet_name="Skew Tests")
trend_test_matrix.to_excel(writer, sheet_name="Trend Tests")

for sheet_name in ["Global Score Sig-Diff", "Pair-wise Score Sig-Diff", "Skew Tests", "Trend Tests"]:
    worksheet = writer.sheets[sheet_name]
    
    ## Get the dimensions of the dataframe
    if sheet_name == "Global Score Sig-Diff":
        min_row, min_col = 1, 1
        max_row, max_col = global_comparison_matrix.shape
    elif sheet_name == "Pair-wise Score Sig-Diff":
        min_row, min_col = len(configuration_headers) + 2, len(configuration_headers) + 1
        max_row, max_col = pair_wise_data_set_comparison_matrix.shape
    elif sheet_name == "Normality-Skew-Kurtosis":
        min_row, min_col = 1, 1
        max_row, max_col = skew_test_matrix.shape
    elif sheet_name == "Trend Tests":
        min_row, min_col = 1, 1
        max_row, max_col = trend_test_matrix.shape
    
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
######## Full data sets

fully_combined_data_sets["Globals"].to_excel(writer, sheet_name="All Data Globals", merge_cells=False)
fully_combined_data_sets["Cat Plans"].to_excel(writer, sheet_name="All Data Cat Plans", merge_cells=False)

## Save the workbook
writer.save()

#########################################################################################################################################################################################
#########################################################################################################################################################################################
######## Tables and Plots
######## --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
######## All results are given as medians, with IQR used as represenation of variance (i.e. non-parametric representation), since we are not sure if the data is normally distributed.
#########################################################################################################################################################################################
#########################################################################################################################################################################################

################################################################################################################################
################################################################################################################################
######## Summary tables - All combined data sets in one table.

summary_globals_1N_stacked.to_latex(f"{cli_args.output_path}_1N_Score_Summary.tex", float_format="%.2f")
summary_raw_ground_level_stacked.to_latex(f"{cli_args.output_path}_1N_Raw_Summary.tex", float_format="%.2f")
summary_globals.to_latex(f"{cli_args.output_path}_Globals_2NSummary.tex", float_format="%.2f")
summary_cat_plans.to_latex(f"{cli_args.output_path}_CatPlan_2NSummary.tex", float_format="%.2f")
pair_wise_data_set_comparison_matrix.to_latex(f"{cli_args.output_path}_TestOfSignificance.tex")

summary_globals_1N_stacked.to_csv(f"{cli_args.output_path}_1N_Score_Summary.dat", sep=" ", line_terminator="\n", index=True)
summary_raw_ground_level_stacked.to_csv(f"{cli_args.output_path}_1N_Raw_Summary.dat", sep=" ", line_terminator="\n", index=True)
summary_globals.to_csv(f"{cli_args.output_path}_Globals_2NSummary.dat", sep=" ", line_terminator="\n", index=True)
summary_cat_plans.to_csv(f"{cli_args.output_path}_CatPlan_2NSummary.dat", sep=" ", line_terminator="\n", index=True)
pair_wise_data_set_comparison_matrix.to_csv(f"{cli_args.output_path}_TestOfSignificance.dat", sep=" ", line_terminator="\n", index=True)

################################################################################################################################
################################################################################################################################
######## Graphs setup

if not cli_args.make_plots:
    print("Skipping graph generation and exiting.")
    sys.exit(0)
print("Generating graphs...")

def set_title_and_labels(fig_or_ax: Union[sns.axisgrid.FacetGrid, sns.axisgrid.JointGrid, pyplot.Axes],
                         x_label: str, y_label: str, title: str) -> None:
    """Set the title and axes labels of a figure or axis."""
    title = title.replace("_", " ")
    x_label = x_label.replace("_", " ")
    y_label = y_label.replace("_", " ")
    if isinstance(fig_or_ax, (sns.axisgrid.FacetGrid, sns.axisgrid.JointGrid)):
        fig: figure.Figure = fig_or_ax.figure
        # fig.suptitle(title)
        fig_or_ax.set_axis_labels(x_label, y_label)
    else:
        # fig_or_ax.set_title(title)
        fig_or_ax.set_xlabel(x_label)
        fig_or_ax.set_ylabel(y_label)

def save_figure(fig: figure.Figure, filename: str) -> None:
    """Save a figure to a pdf and tex file."""
    print(f"\t- Generating figure:  {filename}")
    fig.subplots_adjust(top=0.95, hspace=0.4)
    fig.savefig(fname=f"{cli_args.output_path}_{filename}.png", bbox_inches="tight", dpi=600)
    tikzplotlib.save(figure=fig, filepath=f"{cli_args.output_path}_{filename}.tex", dpi=600, textsize=12, axis_width="\\plotWidth", axis_height="\\plotHeight")

## Max limits for absolute plots.
cat_plans_length_max = fully_combined_data_sets["Cat Plans"]["LE"].max()
globals_length_max = fully_combined_data_sets["Globals"]["BL_LE"].max()
cat_plans_total_time_max = fully_combined_data_sets["Cat Plans"]["TT"].max()
globals_total_time_max = fully_combined_data_sets["Globals"]["HA_T"].max()

## Facet grids are a grid of multiple sub-plots, each with a different value of a variable.
fg: sns.FacetGrid

## Joint plots:
##      - Joint plots have a relational plot in the center and marginal distributions on the top and right.
##          - Type controlled with kind={"scatter", "reg", "kde", "hist", "hex", "resid"}
##          - If the plot has a hue, then conditional colors are added to the relational plot,
##            and kde plots are used for the marginal density distributions, otherwise histograms are used.
##      - To add more layers onto the plot, use the methods on the JointGrid object that jointplot() returns.
##      - https://seaborn.pydata.org/generated/seaborn.jointplot.html
##      - https://seaborn.pydata.org/generated/seaborn.JointGrid.html
jg: sns.JointGrid

################################################################################################################################
################################################################################################################################
######## Relational and distributional plots for performance trade-off between planning time and plan quality scores
## For score plots, it is reasonable to take the average and variance over all problems (since it is normalised), but for absolute values the average is not meaningful.

## Grade of planner performance for each configuration;
fg = sns.catplot(
    data=fully_combined_data_sets["Globals"],
    x=cli_args.break_second, y="GRADE", hue=cli_args.break_first,
    kind="box"
)
fg.set(ylim=(0, 1))
set_title_and_labels(fg, cli_args.break_second, "Grade", f"Grade of Planner Performance for each {cli_args.break_first} and {cli_args.break_second}s")
save_figure(fg.figure, "Grades")
pyplot.show()
sys.exit(0)

## Grade of planner perfomance trade-off chart;
jg = sns.JointGrid(
    data=fully_combined_data_sets["Globals"],
    x="TI_SCORE", y="QL_SCORE", hue=cli_args.break_first,
    xlim=(0, 1), ylim=(0, 1)
)
jg.plot_joint(sns.scatterplot); jg.plot_joint(sns.kdeplot, zorder=0, n_levels=6) # zorder=0 plots kde behind scatterplot
jg.plot_marginals(sns.boxplot); jg.plot_marginals(sns.rugplot, height=0.15, clip_on=False)
jg.set_axis_labels("Time Score", "Quality Score")
jg.figure.suptitle(f"Performance Trade-off between Planning Time and Plan Quality for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
jg.savefig(f"{cli_args.output_path}_Grades_ScoreTradeOff.png")
tikzplotlib.save(figure=jg.figure, filepath=f"{cli_args.output_path}_Grades_ScoreTradeOff.tex")

################################################################################################################################
################################################################################################################################
######## Categorical and distributional plots for plan quality

## TODO: How do we deal with number of actions in a general way? It should be able to fit on the same plot.
## TODO: Can we use a hierarchical x-axis? Like I did for the original excel; with the achievement type above and the search mode below.
##       This would also help for the actions, and allow more compact per-abstraction level plots.
## TODO: Partial problem description headers:
##      - AL IT PN TT LE AC SIZE
##      - Make pair-wise plots to show relations between each of these
##      - For example, TT against LE would show how time tneds to grow with length,
##        and LE against SIZE would show how length tends to grow with size
##        (with hue = AL, IT and PN aren't needed).

#########################
## Bar charts:

## Absolute plan quality level-wise bar plot;
##      - x axis is the levels (one bar per configuration), y axis is quantity of actions or length of plan (median over all runs).
g = sns.catplot(
    data=fully_combined_data_sets["Cat Plans"],
    x="AL", y="LE", hue=cli_args.break_first, col=cli_args.break_second,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Abstraction level", "Monolevel plan length")
g.set_titles("{col_var} {col_name}")
g.set(ylim=(0, cat_plans_length_max))
g.figure.suptitle(f"Median plan length per level for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_AbsolutePlanQuality_LevelWise_BarPlot.png")
tikzplotlib.clean_figure(fig=g.figure)
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_AbsolutePlanQuality_LevelWise_BarPlot.tex")

## Plan quality score level-wise bar plot;
##      - x axis is the levels (one bar per configuration), y axis is the plan quality score [0.0-1.0] (median over all runs).
figure_quality_score_levelwise_bars, axis_quality_score_levelwise_bars = pyplot.subplots()
axis_quality_score_levelwise_bars.set(ylim=(0, 1))
sns.barplot(
    data=fully_combined_data_sets["Cat Plans"],
    ax=axis_quality_score_levelwise_bars,
    x="AL", y="QL_SCORE", hue=cli_args.break_first
)
axis_quality_score_levelwise_bars.set_xlabel("Abstraction level")
axis_quality_score_levelwise_bars.set_ylabel("Plan quality score")
axis_quality_score_levelwise_bars.set_title(f"Median plan quality score per level for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
figure_quality_score_levelwise_bars.savefig(f"{cli_args.output_path}_PlanQualityScore_LevelWise_BarPlot.png")
tikzplotlib.save(figure=figure_quality_score_levelwise_bars, filepath=f"{cli_args.output_path}_PlanQualityScore_LevelWise_BarPlot.tex")

## Absolute plan quality global bar plot;
figure_quality_abs_globals_bars, axis_quality_abs_globals_bars = pyplot.subplots()
axis_quality_abs_globals_bars.set(ylim=(0, globals_length_max))
sns.barplot(
    data=fully_combined_data_sets["Globals"],
    ax=axis_quality_abs_globals_bars,
    x=cli_args.break_second, y="BL_LE", hue=cli_args.break_first
)
axis_quality_abs_globals_bars.set_ylabel("Monolevel plan length")
axis_quality_abs_globals_bars.set_title(f"Median ground-plan length for each {cli_args.break_first} and {cli_args.break_second}")
figure_quality_abs_globals_bars.savefig(f"{cli_args.output_path}_AbsolutePlanQuality_Global_BarPlot.png")
tikzplotlib.clean_figure(fig=figure_quality_abs_globals_bars)
tikzplotlib.save(figure=figure_quality_abs_globals_bars, filepath=f"{cli_args.output_path}_AbsolutePlanQuality_Global_BarPlot.tex")

## Plan quality score global bar plot;
figure_quality_score_globals_bars, axis_quality_score_globals_bars = pyplot.subplots()
axis_quality_score_globals_bars.set(ylim=(0, 1))
sns.barplot(
    data=fully_combined_data_sets["Globals"],
    ax=axis_quality_score_globals_bars,
    x=cli_args.break_second, y="QL_SCORE", hue=cli_args.break_first
)
axis_quality_score_globals_bars.set_ylabel("Plan quality score")
axis_quality_score_globals_bars.set_title(f"Median ground-plan quality score for each {cli_args.break_first} and {cli_args.break_second}") 
figure_quality_score_globals_bars.savefig(f"{cli_args.output_path}_PlanQualityScore_Global_BarPlot.png")
tikzplotlib.clean_figure(fig=figure_quality_score_globals_bars)
tikzplotlib.save(figure=figure_quality_score_globals_bars, filepath=f"{cli_args.output_path}_PlanQualityScore_Global_BarPlot.tex")

#########################
## Historgram plots:

## Absolute plan length and number of actions global histogram plot;
g = sns.displot(
    data=fully_combined_data_sets["Globals"],
    x="BL_LE", hue=cli_args.break_first, col=cli_args.break_second,
    kind="hist", kde=True, height=4, aspect=1.5,
    stat="percent", element="step", # multiple="stack"
)
g.set_axis_labels("Monolevel plan length", "Percent of runs achieving length")
g.set_titles("{col_var} {col_name}")
g.figure.suptitle(f"Histogram of ground-plan length for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_AbsolutePlanQuality_Global_HistogramPlot.png")
tikzplotlib.clean_figure(fig=g.figure)
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_AbsolutePlanQuality_Global_HistogramPlot.tex")

## Plan quality score global histogram plot;
g = sns.displot(
    data=fully_combined_data_sets["Globals"],
    x="QL_SCORE", hue=cli_args.break_first,
    kind="hist", kde=True, height=4, aspect=1.5,
    stat="percent", element="step", # multiple="stack"
)
g.set_axis_labels("Plan quality score", "Percent of runs achieving score")
g.set(xlim=(0, 1))
g.figure.suptitle(f"Histogram of ground-plan quality score for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanQualityScore_Global_HistogramPlot.png")
tikzplotlib.clean_figure(fig=g.figure)
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_PlanQualityScore_Global_HistogramPlot.tex")

#########################
## Box plots:

## Absolute plan quality level-wise box plot;
g = sns.catplot(
    data=fully_combined_data_sets["Cat Plans"],
    x="AL", y="QL_SCORE", hue=cli_args.break_first,
    kind="box", height=4, aspect=1.5
)
g.set_axis_labels("Abstraction level", "Plan quality score")
g.set(ylim=(0, 1))
g.figure.suptitle(f"Plan quality score per level for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanQualityScore_LevelWise_CatPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_PlanQualityScore_LevelWise_CatPlot.tex")

## Plan quality score global box plot;
g = sns.catplot(
    data=fully_combined_data_sets["Globals"],
    x=cli_args.break_second, y="QL_SCORE", hue=cli_args.break_first,
    kind="box", height=4, aspect=1.5
)
g.set_axis_labels(cli_args.break_second, "Plan quality score")
g.figure.suptitle(f"Ground-plan quality score for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanQualityScore_Global_CatPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_PlanQualityScore_Global_CatPlot.tex")

################################################################################################################################
################################################################################################################################
######## Categorical and distributional plots for planning time and memory usage

#########################
## Bar charts:

## TODO: Should we have bar and histogram plots for should we also have a break down of the different time scores, HA_T_SCORE, LT_SCORE, etc?
## This would show how each contribute to the total time score.
## Absolution time score, average non-initial wait time, average minimum execution time per action score.

## Absolute total planning time level-wise bar plot;
g = sns.catplot(
    data=fully_combined_data_sets["Cat Plans"],
    x="AL", y="TT", hue=cli_args.break_first, col=cli_args.break_second,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Abstraction level", "Total planning time (s)")
g.set_titles("{col_var} {col_name}")
g.set(ylim=(0, cat_plans_total_time_max))
g.figure.suptitle(f"Median total planning time per level for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_AbsolutePlanningTime_LevelWise_BarPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_AbsolutePlanningTime_LevelWise_BarPlot.tex")

## Plan time score level-wise bar plot;
figure_time_score_levelwise_bars, axis_time_score_levelwise_bars = pyplot.subplots()
axis_time_score_levelwise_bars.set(ylim=(0, 1))
sns.barplot(
    data=fully_combined_data_sets["Cat Plans"],
    ax=axis_time_score_levelwise_bars,
    x="AL", y="TI_SCORE", hue=cli_args.break_first
)
axis_time_score_levelwise_bars.set_xlabel("Abstraction level")
axis_time_score_levelwise_bars.set_ylabel("Planning time score")
axis_time_score_levelwise_bars.set_title(f"Median planning time score per level for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
figure_time_score_levelwise_bars.savefig(f"{cli_args.output_path}_PlanTimeScore_LevelWise_BarPlot.png")
tikzplotlib.save(figure=figure_time_score_levelwise_bars, filepath=f"{cli_args.output_path}_PlanTimeScore_LevelWise_BarPlot.tex")

## Absolute plan time global bar plot;
figure_time_abs_globals_bars, axis_time_abs_globals_bars = pyplot.subplots()
axis_time_abs_globals_bars.set(ylim=(0, globals_total_time_max))
sns.barplot(
    data=fully_combined_data_sets["Globals"],
    ax=axis_time_abs_globals_bars,
    x=cli_args.break_second, y="HA_T", hue=cli_args.break_first
)
axis_time_abs_globals_bars.set_ylabel("Hierarchical Absolution Time (s)")
axis_time_abs_globals_bars.set_title(f"Median Hierarchical Absolution Time for each {cli_args.break_first} and {cli_args.break_second}")
figure_time_abs_globals_bars.savefig(f"{cli_args.output_path}_AbsolutePlanTime_Global_BarPlot.png")
tikzplotlib.save(figure=figure_time_abs_globals_bars, filepath=f"{cli_args.output_path}_AbsolutePlanTime_Global_BarPlot.tex")

## Plan time score global bar plot;
figure_time_score_globals_bars, axis_time_score_globals_bars = pyplot.subplots()
axis_time_score_globals_bars.set(ylim=(0, 1))
sns.barplot(
    data=fully_combined_data_sets["Globals"],
    ax=axis_time_score_globals_bars,
    x=cli_args.break_second, y="TI_SCORE", hue=cli_args.break_first
)
axis_time_score_globals_bars.set_ylabel("Time score")
axis_time_score_globals_bars.set_title(f"Median time score for each {cli_args.break_first} and {cli_args.break_second}") 
figure_time_score_globals_bars.savefig(f"{cli_args.output_path}_PlanTimeScore_Global_BarPlot.png")
tikzplotlib.save(figure=figure_time_score_globals_bars, filepath=f"{cli_args.output_path}_PlanTimeScore_Global_BarPlot.tex")

## Raw aggreate ground-level planning times bar chart;
g = sns.catplot(
    data=summary_raw_ground_level.reset_index(level=[cli_args.break_first, cli_args.break_second]).melt(id_vars=[cli_args.break_first, cli_args.break_second], value_vars=["LT", "WT", "MET", "CT"], var_name="Time type", value_name="Time"),
    x="Time type", y="Time", hue=cli_args.break_first, col=cli_args.break_second,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Time type", "Time (s)")
g.set_titles("{col_var} {col_name}")
g.figure.suptitle(f"Median hierarchical aggregate planning times for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_RawAggregatePlanningTime_Global_CatPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_RawAggregatePlanningTime_Global_CatPlot.tex")

## Score aggreate ground-level planning times bar chart;
g = sns.catplot(
    data=summary_raw_ground_level.reset_index(level=[cli_args.break_first, cli_args.break_second]).melt(id_vars=[cli_args.break_first, cli_args.break_second], value_vars=["LT_SCORE", "WT_SCORE", "MET_SCORE", "CT_SCORE"], var_name="Time score type", value_name="Score"),
    x="Time score type", y="Score", hue=cli_args.break_first, col=cli_args.break_second,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Time Score Type", "Time Score")
g.set_titles("{col_var} {col_name}")
g.figure.suptitle(f"Median hierarchical planning time scores for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_ScoreAggregatePlanningTime_Global_CatPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_ScoreAggregatePlanningTime_Global_CatPlot.tex")

## Break down of sums of grounding and solving times over all abstraction levels;
##      - This needs to be broken down for each break-second since they are not normalised.
g = sns.catplot(
    data=fully_combined_data_sets_cat_plans_time_sums.reset_index(level=[cli_args.break_first, cli_args.break_second]).melt(id_vars=[cli_args.break_first, cli_args.break_second], value_vars=["GT", "ST"], var_name="Time type", value_name="Time"),
    x="Time type", y="Time", hue=cli_args.break_first, col=cli_args.break_second,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Time type", "Time (s)")
g.figure.suptitle(f"Median grounding and solving times for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_GroundSum_PlanningTime_BarPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_GroundSum_PlanningTime_BarPlot.tex")

## Break down of sums of grounding and solving times as percentage of total-time over all abstraction levels;
##      - Does not need to be broken down for each break-second since it is normalised.
g = sns.catplot(
    data=fully_combined_data_sets_cat_plans_time_sums.reset_index(level=[cli_args.break_first, cli_args.break_second]).melt(id_vars=[cli_args.break_first, cli_args.break_second], value_vars=["GT_POTT", "ST_POTT"], var_name="Time type", value_name="Time"),
    x="Time type", y="Time", hue=cli_args.break_first,
    kind="bar", height=4, aspect=1.5
)
g.set_axis_labels("Time type", "Percent of total time")
g.figure.suptitle(f"Median grounding and solving times as percentage of total time for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PercentPlanningTime_BarPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_GroundSum_PercentPlanningTime_BarPlot.tex")

#########################
## Historgram plots:

## Absolute planning time and number of actions global histogram plot;
g = sns.displot(
    data=fully_combined_data_sets["Globals"],
    x="HA_T", hue=cli_args.break_first, col=cli_args.break_second,
    kind="hist", kde=True, height=4, aspect=1.5,
    stat="percent", element="step", # multiple="stack"
)
g.set_axis_labels("Hierarchical Absolution Time (s)", "Percent of runs achieving time")
g.set_titles("{col_var} {col_name}")
g.figure.suptitle(f"Histogram of Hierarchical Absolution Time for each {cli_args.break_first} and {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_AbsolutePlanTime_Global_HistogramPlot.png")
tikzplotlib.clean_figure(fig=g.figure)
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_AbsolutePlanTime_Global_HistogramPlot.tex")

## Planning time score global histogram plot;
g = sns.displot(
    data=fully_combined_data_sets["Globals"],
    x="QL_SCORE", hue=cli_args.break_first,
    kind="hist", kde=True, height=4, aspect=1.5,
    stat="percent", element="step", # multiple="stack"
)
g.set_axis_labels("Hierarchical Absolution Time Score", "Percent of runs achieving score")
g.set(xlim=(0, 1))
g.figure.suptitle(f"Histogram of Hierarchical Absolution Time Score for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanTimeScore_Global_HistogramPlot.png")
tikzplotlib.clean_figure(fig=g.figure)
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_PlanTimeScore_Global_HistogramPlot.tex")

#########################
## Box plots:



#########################
## Scatter plots:

g = sns.jointplot(
    data=fully_combined_data_sets_cat_plans_time_sums,
    x="GT", y="ST",
    hue=cli_args.break_first, kind="scatter"
)
g.set_axis_labels("Grounding time", "Solving time")
g.figure.suptitle(f"Grounding time vs solving time for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanningTimeScatterPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_GroundSum_PlanningTime_ScatterPlot.tex")

g = sns.jointplot(
    data=fully_combined_data_sets_cat_plans_time_sums,
    x="GT_POTT", y="ST_POTT",
    hue=cli_args.break_first, kind="scatter"
)
g.set_axis_labels("Grounding time as percentage of total time", "Solving time as percentage of total time")
# g.set(xlim=(0, 1), ylim=(0, 1))
g.figure.suptitle(f"Grounding time vs solving time as percentage of total time for each {cli_args.break_first} averaged over all {cli_args.break_second}s")
g.savefig(f"{cli_args.output_path}_PlanningTimeScatterPlot.png")
tikzplotlib.save(figure=g.figure, filepath=f"{cli_args.output_path}_GroundSum_PercentPlanningTime_ScatterPlot.tex")

################################################################################################################################
################################################################################################################################
######## Relational plots for step-wise search times, memory, sub-goal achievement, and refinement expansions, and index-wise sub-plan lengths and interleaving quantities.

## TODO: Can use reflines to show for the step-wise plots where the end of each partial-plan and the start of the unconsidered final-goal problem is on average, and on the index-wise plots where the m-children steps are on average.



################################################################################################################################
################################################################################################################################
######## Categorical and distributional plots for expansion factors and sub/partial-plan balance

## Absolute sub/partial-plan expansions;
##      - Expansion factor per level, sub-plan expansion deviation, sub-plan expansion balance, partial-plan expansion deviation, partial-plan expansion balance.



## Sub/partial-plan balance/matching child distribution/spread scores;
##      - NAE of matching child steps, Sub-plan expansion balance score, partial-plan expansion balance score, matching-child step normalised mean absolute error score, division step normalised mean absolute error score



## Balance of partial problems;
##      - NAE division index and step, standard deviation and coefficient of deviation (same as balance) in size of problems.



#########################
#########################
#### EOF

print("\nProcessing complete.")

if cli_args.show_plots:
    pyplot.show()
sys.exit(0)

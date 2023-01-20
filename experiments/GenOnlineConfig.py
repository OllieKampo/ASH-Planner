###########################################################################
###########################################################################
## Script for generating online planning configurations.                 ##
## Copyright (C)  2022  Oliver Michael Kamperis                          ##
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

"""Script for generating online planning configurations with bounds for division strategies."""

import argparse
import math
import re
import itertools
from os import listdir
from os.path import isfile, join
from typing import Optional

## Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-out", "--output_path", default=None, type=str)
parser.add_argument("-als", "--abstraction_levels", required=True, type=int)
parser.add_argument("-type", "--strategy_type", required=True, choices=["proactive", "reactive"], type=str)
parser.add_argument("-pbounds", "--primary_bounds", nargs="*", default=[], type=str)
parser.add_argument("-sbounds", "--secondary_bounds", nargs="*", default=[], type=str)
parser.add_argument("-smaller", "--lower_only_smaller", action="store_true", default=False)
parser.add_argument("-summin", "--bound_sum_min", default=None, type=str)
parser.add_argument("-summax", "--bound_sum_max", default=None, type=str)
parser.add_argument("-prodmin", "--bound_prod_min", default=None, type=str)
parser.add_argument("-prodmax", "--bound_prod_max", default=None, type=str)
cli_args: argparse.Namespace = parser.parse_args()

def get_combinations(bounds: list[str], abstraction_levels: int) -> list[tuple[str, ...]]:
    """Get all combinations of bounds for the given abstraction levels."""
    return [combination for combination in itertools.product(bounds, repeat=abstraction_levels)]

def generate_configurations(file_name: str, input_path: str, output_path: str,
                            abstraction_levels: int, proactive: bool,
                            primary_bounds: list[str], secondary_bounds: list[str],
                            lower_only_smaller: bool = True,
                            bound_sum_min: Optional[str] = None,
                            bound_sum_max: Optional[str] = None,
                            bound_prod_min: Optional[str] = None,
                            bound_prod_max: Optional[str] = None) -> None:
    """Generate online planning configurations with bounds for division strategies."""
    print(f"Generating configurations for template file '{file_name}' over {abstraction_levels} "
          f"abstraction levels by combining bounds primary={primary_bounds}, secondary={secondary_bounds}.")
    
    with open(input_path, "r") as file_reader:
        lines: list[str] = file_reader.readlines()
        bound_line: int = lines.index("-bound << insert bounds >>\n")
        
        split_file_name: list[str] = re.split("[p|s]?bounds", file_name)
        
        primary_combinations = get_combinations(primary_bounds, abstraction_levels - 1)
        secondary_combinations = get_combinations(secondary_bounds, abstraction_levels - 1)
        
        if secondary_combinations:
            combined_combinations = [[p, s] for p, s in itertools.product(primary_combinations, secondary_combinations)]
        else: combined_combinations = primary_combinations
        
        for combination in combined_combinations:
            if lower_only_smaller:
                if any((index != 0 and float(bound) > min(map(float, combination[:index])))
                    for index, bound in enumerate(combination)):
                    continue
            
            if bound_sum_min is not None:
                if sum(float(b) for b in combination) < float(bound_sum_min):
                    continue
            if bound_sum_max is not None:
                if sum(float(b) for b in combination) > float(bound_sum_max):
                    continue
            if bound_prod_min is not None:
                if math.prod(float(b) for b in combination) < float(bound_prod_min):
                    continue
            if bound_prod_max is not None:
                if math.prod(float(b) for b in combination) > float(bound_prod_max):
                    continue
            
            new_file_name: str
            if isinstance(combination, list):
                new_file_name = f"{split_file_name[0]}{'_'.join(combination[0])}{split_file_name[1]}{'_'.join(combination[1])}{split_file_name[2]}"
            else:
                absolute_bounds: bool = True
                
                bound_type: str = ""
                if any(proactive_strategy in file_name for proactive_strategy in ["hasty", "steady", "jumpy"]):
                    absolute_bounds = '.' not in combination[0]
                    bound_type = "abs_" if absolute_bounds else "per_"
                
                _combination: tuple[str, ...] = combination
                if not absolute_bounds:
                    _combination = tuple(str(int(100.0 * float(bound))) for bound in combination)
                
                new_file_name = f"{split_file_name[0]}{bound_type}{'_'.join(_combination)}{split_file_name[1]}"
            
            print(f"Generating configuration file: {new_file_name} with bounds {_combination}.")
            
            with open(join(output_path, new_file_name), "w") as file_writer:
                for number, line in enumerate(lines):
                    if number == bound_line:
                        bounds: str = ""
                        for l, bound in enumerate(combination):
                            _l: int = l if proactive else (l + 1)
                            if isinstance(bound, tuple):
                                bounds += f" {abstraction_levels - _l}={bound[0]},{bound[1]}"
                            else: bounds += f" {abstraction_levels - _l}={bound}"
                        file_writer.write(f"-bound{bounds}\n")
                    else: file_writer.write(line)

if __name__ == "__main__":
    print(f"Generating online planning configurations with bounds: primary={cli_args.primary_bounds}, secondary={cli_args.secondary_bounds}")
    
    paths: str = cli_args.input_paths
    for path in paths:
        ## If the path is a file, generate configurations for this file.
        if isfile(path) and path.endswith(".config"):
            generate_configurations(path.split("\\")[-1], path, cli_args.output_path,
                                    cli_args.abstraction_levels, cli_args.strategy_type == "proactive",
                                    cli_args.primary_bounds, cli_args.secondary_bounds, cli_args.lower_only_smaller,
                                    cli_args.bound_sum_min, cli_args.bound_sum_max,
                                    cli_args.bound_prod_min, cli_args.bound_prod_max)
        
        ## If the path is a directory, generate configurations for all files in the directory.
        else:
            for file_name in listdir(path):
                if isfile(input_path := join(path, file_name)):
                    generate_configurations(file_name, input_path, cli_args.output_path,
                                            cli_args.abstraction_levels, cli_args.strategy_type == "proactive",
                                            cli_args.primary_bounds, cli_args.secondary_bounds, cli_args.lower_only_smaller,
                                            cli_args.bound_sum_min, cli_args.bound_sum_max,
                                            cli_args.bound_prod_min, cli_args.bound_prod_max)

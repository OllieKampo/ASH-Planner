import argparse
import re
import sys
import itertools
from os import listdir
from os.path import isfile, join

## Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("input_paths", nargs="*", type=str)
parser.add_argument("-out", "--output_path", required=True, type=str)
parser.add_argument("-als", "--abstraction_levels", required=True, type=int)
parser.add_argument("-pbounds", "--primary_bounds", nargs="*", default=[], type=str)
parser.add_argument("-sbounds", "--secondary_bounds", nargs="*", default=[], type=str)
cli_args: argparse.Namespace = parser.parse_args()

def get_combinations(bounds: list[str], abstraction_levels: int) -> set[tuple[str, ...]]:
    combinations = set()
    for permutation in itertools.permutations(bounds):
        for combination in itertools.combinations_with_replacement(permutation, r=abstraction_levels):
            combinations.add(combination)

def generate_configurations(template_file_path: str, primary_bounds: list[str], secondary_bounds: list[str], abstraction_levels: int) -> None:
    print(f"Generating configurations for template file: {template_file_path} over {abstraction_levels} "
          f"abstraction levels by combining bounds primary={primary_bounds}, secondary={secondary_bounds}.")
    
    with open(template_file_path, "r") as file_reader:
        lines: list[str] = file_reader.readlines()
        bound_line: int = lines.index("-bound << insert bounds >>\n")
        
        split_path: list[str] = re.split("[p|s]?bounds", template_file_path)
        
        primary_combinations = get_combinations(primary_bounds, abstraction_levels)
        secondary_combinations = get_combinations(secondary_bounds, abstraction_levels)
        
        if secondary_combinations:
            combined_combinations = {tuple(p, s) for p, s in itertools.product(primary_combinations, secondary_combinations)}
        else: combined_combinations = primary_combinations
        
        for combination in combined_combinations:
            
            new_file_path: str
            if isinstance(combination, tuple):
                new_file_path = f"{split_path[0]}{'_'.join(combination[0])}{split_path[1]}{'_'.join(combination[1])}{split_path[2]}"
            else:
                absolute_bounds: bool = '.' not in combination[0]
                
                bound_type: str = ""
                if any(proactive_strategy in template_file_path for proactive_strategy in ["hasty", "steady", "jumpy"]):
                    bound_type = "_abs_" if absolute_bounds else "_per_"
                
                _combination: tuple[str, ...] = combination
                if not absolute_bounds:
                    _combination = tuple(str(100 * float(bound)) for bound in combination)
                
                new_file_path = f"{split_path[0]}{bound_type}{'_'.join(_combination)}{split_path[1]}"
            
            print(f"Generating configuration file: {new_file_path} with bounds {_combination}.")
            
            with open(new_file_path, "w") as file_writer:
                for number, line in enumerate(lines):
                    if number == bound_line:
                        bounds: str = ""
                        for l, bound in enumerate(combination):
                            if isinstance(bound, tuple):
                                bounds += f" {(abstraction_levels + 1) - l}={bound[0]},{bound[1]}"
                            else: bounds += f" {(abstraction_levels + 1) - l}={bound}"
                        file_writer.write(f"-bound{bounds}\n")
                    else: file_writer.write(line)

# abstraction_levels: int = cli_args.abstraction_levels
# primary_bounds: list[str] = cli_args.primary_bounds
# secondary_bounds: list[str] = cli_args.secondary_bounds

paths: str = cli_args.input_paths
for path in paths:
    if path.endswith(".config"):
        generate_configurations(path)
    else:
        for file_name in listdir(path):
            if isfile(file_path := join(path, file_name)):
                generate_configurations(file_path)
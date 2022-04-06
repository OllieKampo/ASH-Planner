import sys
import itertools
from os import listdir
from os.path import isfile, join

abstraction_levels: int = int(sys.argv[2])
bounds_to_combine: list[str] = sys.argv[3:]

absolute_bounds: bool = '.' not in bounds_to_combine[0]

def generate_configurations(template_file_path: str) -> None:
    print(f"Generating configurations for template file: {template_file_path} over "
          f"{abstraction_levels} abstraction levels by combining bounds {bounds_to_combine}.")
    
    with open(template_file_path, "r") as file_reader:
        lines: list[str] = file_reader.readlines()
        bound_line: int = lines.index("-bound << insert bounds >>\n")
        combinations = set()
        
        for permutation in itertools.permutations(bounds_to_combine):
            for combination in itertools.combinations_with_replacement(permutation, r=abstraction_levels):
                combinations.add(combination)
        
        for combination in combinations:
            split_path: list[str] = template_file_path.split('bounds')
            
            bound_type: str = ""
            if any(proactive_strategy in template_file_path for proactive_strategy in ["hasty", "steady", "jumpy"]):
                bound_type = "_abs_" if absolute_bounds else "_per_"
            
            _combination: tuple[str, ...] = combination
            if not absolute_bounds:
                _combination = tuple(str(100 * float(bound)) for bound in combination)
            
            new_file_path: str = f"{split_path[0]}{bound_type}{'_'.join(_combination)}{split_path[1]}"
            print(f"Generating configuration file: {new_file_path} with bounds {_combination}.")
            
            with open(new_file_path, "w") as file_writer:
                for number, line in enumerate(lines):
                    if number == bound_line:
                        bounds: str = ""
                        for l, bound in enumerate(combination):
                            bounds = bounds + f" {(abstraction_levels + 1) - l}={bound}"
                        file_writer.write(f"-bound{bounds}\n")
                    else: file_writer.write(line)

path: str = sys.argv[1]
if path.endswith(".config"):
    generate_configurations(path)
else:
    for file_name in listdir(path):
        if isfile(file_path := join(path, file_name)):
            generate_configurations(file_path)
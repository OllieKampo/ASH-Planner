import sys
import itertools

with open(sys.argv[1], "r") as file_reader:
    lines: list[str] = file_reader.readlines()
    bound_line: int = lines.index("-bound\n")
    combinations = set()
    
    for permutation in itertools.permutations(sys.argv[3:]):
        for combination in itertools.combinations_with_replacement(permutation, r=int(sys.argv[2])):
            combinations.add(combination)
    
    for combination in combinations:
        file_name: str = f"{sys.argv[1].split('.config')[0]}_{'_'.join(combination)}.config"
        print(f"Generating: {file_name} with bounds {combination}")
        
        with open(file_name, "w") as file_writer:
            for number, line in enumerate(lines):
                if number == bound_line:
                    bounds: str = ""
                    for l, bound in enumerate(combination):
                        bounds = bounds + f" {(int(sys.argv[2]) + 1) - l}={bound}"
                    file_writer.write(f"-bounds{bounds}\n")
                else: file_writer.write(line)
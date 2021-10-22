import argparse
parser = argparse.ArgumentParser()
parser.add_argument("a", action="extend", nargs="*")
parser.add_argument("-pm", "--planning_mode", choices=["classical", "hcr-offline", "hcr-online"], default="hcr-online", type=str)
subparsers = parser.add_subparsers(help="sub-command help TODO")
parser_mode = subparsers.add_parser("online_mode", help="mode help")
parser_mode.add_argument("--continuous", choices=["True", "False"], type=str, help="prop help TODO")
parser_mode.add_argument("--division_strategy", choices=["none", "cautious", "balanced", "reckless"], type=str, help="prop help TODO")
parser_mode.add_argument("--detect_dependencies", choices=["All", "True", "False"], type=str, help="identifies dependencies between sub-problems and partial-problems, "
                         "In continuous mode, this will identify both dependent sub-problems and interleaved sub-problems, within each partial problem (or the complete problem if division is disabled)"
                         "In dis-continuous mode, this will not be able to identify either aspect of subproblems."
                         "If problem division is enabled, dependencies between the partial problems themselves will only be detected if 'All', which requires that a undivided version of the problem is solved.")
# look_back = type: {subgoal stages, partial plans}, number: int
# final_goal_preferences: {pos_fgoals: bool, neg_fgoals: bool}
# iterative_smoothing = passes(number of times to attempt to find a better plan), merge quantity, growth factor(if not zero, each pass contains a multi-iteration, where the later iterations have a higher merge quantity), growth phases
parser.add_argument("--d", action="extend", nargs="*", type=int)
parser.add_argument("--f", nargs="?", choices=[True, False, None], default=True, const=True, type=lambda str_: str_ if str_ is None else str_ == "True")
bool_options = dict(nargs="?", choices=[True, False], default=False, const=True, type=lambda str_: str_ == "True")
print(bool_options)
# parser_optimise = subparsers.add_parser("optimise", help="TODO")
# parser_optimise.add_argument("--opt", **bool_options,
#                                 help="Display help information about the optimisation module and exit")
# print(parser_optimise)
namespace: argparse.Namespace = parser.parse_args()
print(namespace)
###########################################################################
###########################################################################
## Interactive terminal script for ASH                                   ##
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

import argparse
import datetime
import functools
import itertools
import logging
import os
import sys
from typing import Any, Optional, Sequence, Type, Union
import time
import json
import numpy
from matplotlib import pyplot

import core.Planner as Planner
import core.Strategies as Strategies
from core.Helpers import center_text
import Experiment

## Main module logger
_Launcher_logger: logging.Logger = logging.getLogger(__name__)
_Launcher_logger.setLevel(logging.DEBUG)

Number = Union[int, float]

_ASH_TITLE: str = """
░█████╗░░██████╗██╗░░██╗
██╔══██╗██╔════╝██║░░██║
███████║╚█████╗░███████║
██╔══██║░╚═══██╗██╔══██║
██║░░██║██████╔╝██║░░██║
╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝
 
=======================================================================
ASH - The ASP based Hierarchical Conformance Refinement Planner
Copyright (C)  2021  Oliver Michael Kamperis
=======================================================================
 
This program comes with ABSOLUTELY NO WARRANTY; for details use `--warranty'. This is free software,
and you are welcome to redistribute it under certain conditions; use `--conditions' for details.
For help and usage instructions use `--help' and `--instructions' respectively.
"""

_ASH_VERSION: str = "PROTOTYPE v0.4.2"

_ASH_WARRANTY: str = """
THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""

_ASH_CONDITIONS: str = """
ASH - The ASP based Hierarchical Conformance Refinement Planner
Copyright (C)  2021  Oliver Michael Kamperis
Email: o.m.kamperis@gmail.com
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

_ASH_INSTRUCTIONS: str = """

Onine Planning Methods
----------------------

If continuous yield is disabled and the division strategy is 'none', then the planner enters offline planning mode.
In offline mode, all monolevel planning problems are complete, and solved prior to yielding anything (execution).

An increment can involve at most one partial problem per level, but might not include all levels in each increment.
For example, in complete-first divided planning, there is only one partial problem per increment, whereas ground-first usually involves a hierarchy of partial problems per increment.

Division Strategies
-------------------

The strategy 'none' does not make any divisions, making all monolevel planning problems complete.
The strategy 'all' makes every possible problem division, entering the planner into sub-planning mode.

Saving grounding
----------------

Gets rid of any learnt no-good clauses, might reduce some overheads, and uses less memory, but there is a cost in solving the base program parts again.

Detecting Partial Problem Dependencies
--------------------------------------

In sequential yield mode, 'simple' will identify both dependent sub-problems and interleaved sub-problems, within each partial problem or the complete problem if division is disabled.
If blending is enabled, 'simple' will also find dependencies between adjacent partial problems only, since blending only occurs between adjacent partial problems.

If problem division is enabled, dependencies between the partial problems themselves will only be detected in 'all' mode, which requires that a complete version of the problem to also be solved.

Final Goal Preemptive Achievement Heuristics
--------------------------------------------

The final-goal preemtive achievement heuristics modify the behaviour of the underlying Clingo ASP solver.
If enabled, they ensure that; when an arbitrary choice between multiple actions, whose effects
all achieve the included sub-goal stages, is available in a non-final partial problem the,
solver will prefer to choose the action(s) whose effects achieve a final goal literal, if one such action is available.

When there is an arbitrary choice, we say that the final-goal is preemptively applicable to the
partial problem. This usually occurs because sub-goals are defined by the more general abstract
state space, and there is usually many ways to achieve that sub-goal in the original state space,
because many original fluent state literals will map to any given abstract state literal. As a
result, there are many actions whose effects will achieve one such sub-goal, but don't achieve the final-goal.
This is called the guidance problem, where the sub-goals don't give the planner at the next level enough
information at the level, in order the achieve the stricter requirements of problems with larger, more detailed
state spaces, and thus more specific/detailed final-goals.

Informally, the heuristic requests the planner to plan actions that achieve positive goals, and to not plan actions that would unachieve negative goals, if doing so is possible and does not increase the plan length.
Importantly, these are effectively soft suggestions, the planner only accepts them if there are no drawbacks in the short-term.
Resultantly, the solutions to early partial plans still have the same quality in terms of length and number of actions, but the heuristic will override action preferences.

By default, only preemptively achieving positive final-goals are prefered. This is because there is
a comparitively small number of positive final goals, and only very few are applicable at a given time.
This tends to mean that preemptively achieving positive final goals is a very prudent course of action.
Contrastly, preemptively achieving negative final-goals is rarely effective. This is because there is
usually far more negtive final-goals, since all fluent state literals for any final goal state variable
that are not assigned a positive final-goal, are assigned a negative final goal literal As a result, there
are usually many possible negtive final-goals that can be preemptively achieved, many of which will
not actually be at all helpful in the long term, especially as achieving the positives usually achieves the
negatives by implication.

Search and Solution Spaces
--------------------------

The solution space is the set of all legal solutions to a monolevel planning problem.
The union of the ground-level solution spaces over all possible refinement schemas is effective solution space of the hierarchical planning problem.
This may be the top-level classical planning problem, or a refinement planning problem defined under some refinement schema.
Solution spaces are generating during the standard planning mode, simply by requesting the ASP program solver to find all its answer sets (usually only one is requested, which effectively contains one random solution).
This is similar to multiple-refinement, except ever possible top-level plan is refined, as are all of their refinements

Note that the planner cannot simultaneously generate both the search and solution space, as this would have no meaning.

The ith index sub-goals stage search space is equivalent to the partial solution space of a partial problem whose last sub-goal stage is the ith index.

To generating the search space, the planner enters a special mode, that forces a certain length plan to be generated,
and seeing how many possible plans there are of that length, whilst achieving a fixed (or maximal) number of subgoals if conformance is enabled.
    - Goal-wise: minimal achievement of ith sub-goal stage
    - Step-wise: achievement of maximal number of subgoals of k length
achievement of ith subgoal at k > k_{min} length (useful when looking at solution space of interleaved subgoal stages)

Solution space says that there are X potential/feasible/viable solutions of the complete problem having achieved the ith subgoal stage in k steps.
Should be able to work out the branching factor from the search spaces, since the branching factor is just the everage number of legal state transitions from the state at each step 'j' less than the 'k' length search space.
Branching factor and search space are not the same;
    - branching factor 'b' is the number of 'choices' (legal transitions) that were available at each step of the plan that was actually chosen as the solution,
    - partial solution space is the number of possible plans of 'k' length or that achieve the 'ith' subgoal state at step 'k' (state that satisfies the subgoal stage) which is usually 'b^k',
    - solution space is the number of actual solutions (the search space to a final goal state (state that satisfies the final goal)).
"""

def get_hierarchical_arg(dict_or_number: Union[Number, dict[int, Number]], level: int, default: Optional[Number] = None) -> Optional[Number]:
    """Get the value of a hierarchical argument at a given abstraction level."""
    if isinstance(dict_or_number, dict):
        if (arg := dict_or_number.get(level, default)) is not None:
            return arg
        else: return default
    return dict_or_number

def __main() -> int:
    """Main method which creates a console session and returns 0 if the console returns cleanly."""
    
    ## Run initial setup and get CLI arguments
    namespace: argparse.Namespace = __setup()
    
    ## Print the headers; title, warranty and distribution conditions as requested
    print(center_text(_ASH_TITLE, prefix_blank_line=True))
    if namespace.warranty:
        print(center_text(_ASH_WARRANTY, framing_width=80, append_blank_line=True))
    if namespace.conditions:
        print(center_text(_ASH_CONDITIONS, framing_width=80, append_blank_line=True))
    if namespace.instructions:
        print(center_text(_ASH_INSTRUCTIONS, framing_width=80, append_blank_line=True))
        return 0
    
    ## Pause to let the user read the headers
    if not namespace.disable_pause_on_start:
        input("Press any key to begin...")
    
    ## Find the verbosity mode;
    ##      - Results is a special mode where output from the planner is disabled and only experimental results are shown
    if namespace.ash_output != "experiment":
        verbosity = Planner.Verbosity[namespace.ash_output.capitalize()]
    else: verbosity = Planner.Verbosity.Minimal
    
    ## Setup the planner
    planner = Planner.HierarchicalPlanner(namespace.files, name="Main", threads=namespace.threads,
                                          verbosity=verbosity, silence_clingo=not namespace.clingo_output)
    
    ## Initialise the planning problem
    find_inconsistencies: bool = namespace.operation == "find-problem-inconsistencies"
    inconsistencies = planner.initialise_problem(find_inconsistencies)
    if find_inconsistencies: return 0
    
    conformance_type: Optional[Planner.ConformanceType] = None
    division_strategy: Optional[Strategies.DivisionStrategy] = None
    
    if namespace.conformance_type is not None:
        conformance_type = Planner.ConformanceType(namespace.conformance_type)
    
    def get_hierarchical_args(dict_or_number: Union[Number, dict[int, Number]], default: Optional[Number] = None) -> Union[Number, dict[int, Number]]:
        """Get the value of a hierarchical argument at a given abstraction level."""
        if isinstance(dict_or_number, dict):
            hierarchical_args: dict[int, Number] = {}
            for level in planner.domain.level_range:
                if (arg := dict_or_number.get(level, default)) is not None:
                    hierarchical_args[level] = arg
                else: hierarchical_args[level] = default
            return hierarchical_args
        return dict_or_number
    
    ## If problem space generation or dependency detection is enabled then attempt to load a schema
    if (namespace.problem_space is not None
        or namespace.detect_dependencies):
        
        # if not namespace.load_schema is not None:
        #     raise RuntimeError("Cannot generate problem spaces or detect dependencies without a refinement schema.")
        # if namespace.operation != "standard":
        #     raise RuntimeError("Can only generate problem spaces or detect dependencies in standard operation mode.")
        
        # with open(namespace.load_schema, 'r') as file_reader:
        #     json_dict = json.loads(file_reader.read())
        # schema = Planner.RefinementSchema.from_json(json_dict)
        # planner.load_schema(schema, False, False)
        
        planning_function = functools.partial(planner.monolevel_plan,
                                              1, # schema.level - 1,
                                              namespace.enable_concurrency,
                                              False, # True
                                              
                                              conformance_type=conformance_type,
                                              sequential_yield=False,
                                              use_minimum_search_length_bound=False,
                                              
                                              minimise_actions=namespace.minimise_actions,
                                              preempt_pos_fgoals=namespace.positive_final_goal_preemptive_achievement_heuristic,
                                              preempt_neg_fgoals=namespace.negative_final_goal_preemptive_achievement_heuristic,
                                              
                                              generate_search_space=namespace.problem_space == "search",
                                              generate_solution_space=namespace.problem_space == "solution",
                                            
                                              time_limit=get_hierarchical_arg(namespace.planning_time_limit, namespace.bottom_level),
                                              length_limit=get_hierarchical_arg(namespace.search_length_limit, namespace.bottom_level))
    
    ## Planning mode is hierarchical (conformance refinement or classical)
    elif namespace.planning_mode in ["hcr", "hcl"]:
        
        ## Determine division strategy for conformance refinement planning
        refinement_planning: bool = namespace.planning_mode == "hcr"
        division_strategy: Optional[Strategies.DivisionStrategy] = None
        
        if refinement_planning:
            ## If a division strategy is given then online planning is enabled
            if namespace.division_strategy != "none":
                
                ## Obtain the specified division strategy
                division_strategy_name: str
                proactive_basis_name: str = ""
                division_strategy_class: Type[Strategies.DivisionStrategy]
                proactive_basis: Type[Strategies.DivisionStrategy]
                
                if len(strategy_name_split := namespace.division_strategy.split('-')) == 2:
                    proactive_basis_name = strategy_name_split[1]
                    proactive_basis = Strategies.GetStrategy[proactive_basis_name].value
                
                division_strategy_name = strategy_name_split[0]
                division_strategy_class = Strategies.GetStrategy[division_strategy_name].value
                
                ## Obtain the bounds, blends and backwards horizon for the strategy
                bounds: dict[int, Union[Number, tuple[Number]]] = {}
                blend: dict[int, Strategies.Blend] = {}
                horizon: dict[int, Number] = {}
                
                level_range: range = planner.constrained_level_range(namespace.bottom_level, namespace.top_level)
                for level in level_range:
                    bounds[level] = get_hierarchical_arg(namespace.division_strategy_bounds, level)
                    blend[level] = Strategies.Blend(get_hierarchical_arg(namespace.left_blend_quantities, level, 0),
                                                    get_hierarchical_arg(namespace.right_blend_quantities, level, 0))
                    horizon[level] = get_hierarchical_arg(namespace.backwards_horizon, level)
                    
                    ## Blending together more than half of partial problems is generally not advisable;
                    ##      - In particular, if the right blend of problem X overlaps with the left blend of problem X + 2, then problem X + 1
                    if ((isinstance((left := blend[level].left), float) and left > 0.5)
                        or isinstance((right := blend[level].right), float) and right > 0.5):
                        _Launcher_logger.warn("Blend quantities of greater than 0.5 are generally detrimental to performance.")
                    
                    ## Ensure that there is not a left blend requiring revision of a refined plan on a saved grounding;
                    ##      - It is not possible to do this since it is not possible to change any sub-goal stages that have already been committed.
                    if (namespace.save_grounding
                        and not namespace.avoid_refining_sgoals_marked_for_blending
                        and blend[level].left > 0):
                        raise ValueError("It is not possible to left blend on a saved grounding without avoiding refining sgoals marked for blending.")
                
                ## Instantiate the strategy with its specific bounds
                reactive_bound_type = Strategies.ReactiveBoundType(f"{namespace.bound_type}_time_bound")
                moving_average: int = namespace.moving_average
                preemptive: bool = namespace.preemptive_division
                interrupting: bool = namespace.interrupting_division
                
                if issubclass(division_strategy_class, Strategies.Basic):
                    division_strategy = division_strategy_class(problems=bounds, blend=blend)
                
                if issubclass(division_strategy_class, Strategies.NaiveProactive):
                    division_strategy = division_strategy_class(size_bound=bounds, blend=blend)
                
                if division_strategy_class == Strategies.Relentless:
                    division_strategy = division_strategy_class(time_bound=bounds,
                                                                bound_type=reactive_bound_type,
                                                                backwards_horizon=horizon,
                                                                moving_average=moving_average,
                                                                preemptive=preemptive,
                                                                interrupting=interrupting)
                
                if issubclass(division_strategy_class, Strategies.Impetuous):
                    if not isinstance(_bound := next(iter(bounds.values())), tuple) or len(_bound) != 2:
                        raise ValueError("The impetuous division strategy requires exactly two bounds per level.")
                    
                    division_strategy = division_strategy_class(cumulative_time_bound={level : bound[0] if bound is not None else None for level, bound in bounds.items()},
                                                                continuous_time_bound={level : bound[1] if bound is not None else None for level, bound in bounds.items()},
                                                                continuous_bound_type=reactive_bound_type,
                                                                backwards_horizon=horizon,
                                                                moving_average=moving_average,
                                                                preemptive=preemptive)
                
                if issubclass(division_strategy_class, Strategies.Rapid):
                    division_strategy = division_strategy_class(proactive_basis,
                                                                size_bound={level : bound[0] if bound is not None else None for level, bound in bounds.items()},
                                                                reactive_time_bound={level : bound[1] if bound is not None else None for level, bound in bounds.items()},
                                                                reactive_bound_type=reactive_bound_type,
                                                                backwards_horizon=horizon,
                                                                moving_average=moving_average)
        
        planning_function = functools.partial(planner.hierarchical_plan,
                                              namespace.bottom_level,
                                              namespace.top_level,
                                              namespace.enable_concurrency,
                                              refinement_planning,
                                              
                                              conformance_type=conformance_type,
                                              sequential_yield=namespace.sequential_yielding,
                                              division_strategy=division_strategy,
                                              online_method=Planner.OnlineMethod(namespace.online_method),
                                              save_grounding=namespace.save_grounding,
                                              use_search_length_bound=namespace.minimum_search_length_bound,
                                              avoid_refining_sgoals_marked_for_blending=namespace.avoid_refining_sgoals_marked_for_blending,
                                              make_observable=namespace.make_observable,
                                              
                                              minimise_actions=namespace.minimise_actions,
                                              preempt_pos_fgoals=namespace.positive_final_goal_preemptive_achievement_heuristic,
                                              preempt_neg_fgoals=namespace.negative_final_goal_preemptive_achievement_heuristic,
                                              order_fgoals_achievement=namespace.final_goal_intermediate_achievement_ordering_preferences,
                                              
                                              detect_interleaving=namespace.detect_interleaving,
                                              detect_dependencies=namespace.detect_dependencies,
                                              generate_search_space=False,
                                              generate_solution_space=False,
                                              
                                              time_limit=get_hierarchical_args(namespace.planning_time_limit),
                                              length_limit=get_hierarchical_args(namespace.search_length_limit),
                                              
                                              pause_on_level_change=namespace.pause_on_level_change,
                                              pause_on_increment_change=namespace.pause_on_increment_change)
    
    ## Planning mode is monolevel classical
    else:
        planning_function = functools.partial(planner.monolevel_plan,
                                              namespace.bottom_level,
                                              namespace.enable_concurrency,
                                              False,
                                              minimise_actions=namespace.minimise_actions,
                                              time_limit=get_hierarchical_arg(namespace.planning_time_limit, namespace.bottom_level),
                                              length_limit=get_hierarchical_arg(namespace.search_length_limit, namespace.bottom_level))
    
    
    
    if namespace.operation == "standard":
        planning_function()
        
        ## Get the resulting plans
        hierarchical_plan: Planner.HierarchicalPlan = planner.get_hierarchical_plan(bottom_level=namespace.bottom_level,
                                                                                    top_level=namespace.bottom_level if namespace.planning_mode == "mcl" else namespace.top_level)
        
        ## Save the plans as requested
        if (plan_file := namespace.plan_file) is not None:
            _Launcher_logger.info(f"Saving generated plan to file: {plan_file}")
            try:
                with open(plan_file, 'w') as file_writer:
                    file_writer.write(json.dumps(hierarchical_plan.serialisable_dict, indent=4))
            except:
                _Launcher_logger.error("Failed to save plan to file.", exc_info=1)
        
        ## Save the refinement schema as requested
        if (schema_file := namespace.save_schema) is not None:
            _Launcher_logger.info(f"Saving generated refinement schema to file: {schema_file}")
            try:
                with open(schema_file, 'w') as file_writer:
                    file_writer.write(json.dumps(hierarchical_plan.get_refinement_schema(namespace.schema_level).serialisable_dict, indent=4))
            except:
                _Launcher_logger.error("Failed to save schema to file.", exc_info=1)
        
        ## Graphify statistics as requested
        if namespace.display_graph:
            # __display_graphs() TODO
            
            import math
            
            bar_width: float
            # def bar_width(bar: int, tbars: int, pad: float) -> float:
            #     return ((1.0 / tbars) - pad) * (-((tbars/2) - 0.5 + 1) + bar)
            
            ## Find the regression plots for each partial plan
            regression_lines: dict[int, dict[str, Any]] = {"total" : {}, "ground" : {}, "search" : {}}
            for increment, partial_plan in hierarchical_plan.partial_plans[namespace.bottom_level].items():
                func, x_points, y_points, popt, pcov = partial_plan.regress_total_time
                regression_lines["total"][increment] = {"func" : func, "x_points" : x_points, "y_points" : y_points, "popt" : popt, "pcov" : pcov}
                func, x_points, y_points, popt, pcov = partial_plan.regress_grounding_time
                regression_lines["ground"][increment] = {"func" : func, "x_points" : x_points, "y_points" : y_points, "popt" : popt, "pcov" : pcov}
                func, x_points, y_points, popt, pcov = partial_plan.regress_solving_time
                regression_lines["search"][increment] = {"func" : func, "x_points" : x_points, "y_points" : y_points, "popt" : popt, "pcov" : pcov}
            
            ## Generate four graphs;
            ##      - Planning statistics per abstraction level bar chart,
            ##      - Ground level planning times against search length (one line per abstraction level), (conformance mapping here too?)
            ##      - Total number of achieved sub-goal stages against search length (one line per abstraction level), (deviation and balance here too?)
            ##      - Planning time per online planning increment.
            figure, axes = pyplot.subplots(2, 2)
            
            xlabels = [str(n) for n in reversed(planner.domain.level_range)]
            x = numpy.arange(len(xlabels))
            
            grounding_times, solving_times, total_times, latency_times, completion_times = [], [], [], [], []
            memory_rss, memory_vms = [], []
            concat_length, concat_actions = [], []
            concat_length_expansion, concat_actions_expansion = [], []
            concat_subplan_length_deviation, concat_subplan_actions_deviation = [], []
            concat_subplan_length_balance, concat_subplan_actions_balance = [], []
            
            # problems, average_yield_times, par_deviation, par_balance = [], [], [], []
            
            for level in reversed(hierarchical_plan.level_range):
                overall_totals = hierarchical_plan.get_overall_totals(level)
                
                grounding_times.append(overall_totals.grounding_time)
                solving_times.append(overall_totals.solving_time)
                total_times.append(overall_totals.total_time)
                # average_yield_times.append(hierarchical_plan.get_average_yield_time(level))
                latency_times.append(hierarchical_plan.get_latency_time(level))
                completion_times.append(hierarchical_plan.get_completion_time(level))
                
                memory_rss.append(overall_totals.memory.rss)
                memory_vms.append(overall_totals.memory.vms)
                
                concat_length.append(hierarchical_plan.concatenated_plans[level].plan_length)
                concat_actions.append(hierarchical_plan.concatenated_plans[level].total_actions)
                
                factor: Planner.Expansion = hierarchical_plan.concatenated_plans[level].get_plan_expansion_factor()
                deviation: Planner.Expansion = hierarchical_plan.concatenated_plans[level].get_expansion_deviation()
                balance: Planner.Expansion = hierarchical_plan.concatenated_plans[level].get_degree_of_balance()
                
                concat_length_expansion.append(factor.length)
                concat_actions_expansion.append(factor.action)
                concat_subplan_length_deviation.append(deviation.length)
                concat_subplan_actions_deviation.append(deviation.action)
                concat_subplan_length_balance.append(balance.length)
                concat_subplan_actions_balance.append(balance.action)
                
                # problems.append(len(hierarchical_plan.partial_plans[level]))
                # par_deviation.append(hierarchical_plan.get_partial_plan_expansion_deviation())
                # par_balance.append(hierarchical_plan.get_partial_plan_balance())
            
            ## Hierarchical grand total planning time statistics
            bar_width = 0.19 # bar_width(bars=5, pad=0.01)
            axes[0, 0].bar(x - (bar_width * 2.0), grounding_times, bar_width, label="Grounding Time (s)")
            axes[0, 0].bar(x - (bar_width * 1.0), solving_times, bar_width, label="Solving Time (s)")
            axes[0, 0].bar(x, total_times, bar_width, label="Total Time (s)")
            axes[0, 0].bar(x + (bar_width * 1.0), latency_times, bar_width, label="Latency Time (s)")
            axes[0, 0].bar(x + (bar_width * 2.0), completion_times, bar_width, label="Completion Time (s)")
            axes[0, 0].set_xticks(x)
            axes[0, 0].set_xticklabels(xlabels)
            axes[0, 0].set_ylabel("Time (s)")
            axes[0, 0].set_xlabel("Abstraction level")
            axes[0, 0].legend()
            
            ## Hierarchical required memory statistics
            bar_width = 0.45
            axes[0, 1].bar(x - (bar_width * 0.5), memory_rss, bar_width, label="Resident Set Size")
            axes[0, 1].bar(x + (bar_width * 0.5), memory_vms, bar_width, label="Virtual Memory Size")
            axes[0, 1].set_xticks(x)
            axes[0, 1].set_xticklabels(xlabels)
            axes[0, 1].set_ylabel("Required Memory (Mb)")
            axes[0, 1].set_xlabel("Abstraction level")
            axes[0, 1].legend()
            
            ## Hierarchical concatenated plan quality statistics
            bar_width = 0.45
            axes[1, 0].bar(x - (bar_width * 0.5), concat_length, bar_width, label="Concatenated Length")
            axes[1, 0].bar(x + (bar_width * 0.5), concat_actions, bar_width, label="Concatenated Actions")
            ## TODO Trailing plan length?
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(xlabels)
            axes[1, 0].set_ylabel("Plan Quality")
            axes[1, 0].set_xlabel("Abstraction level")
            axes[1, 0].legend()
            
            ## Problems per level
            # axes[1, 1].bar(x - (bar_width * 1.5), problems, bar_width, label="Partial Problems")
            # axes[1, 1].bar(x - (bar_width * 0.5), average_yield_times, bar_width, label="Resident Set Size")
            # axes[1, 1].bar(x + (bar_width * 0.5), par_deviation, bar_width, label="Resident Set Size")
            # axes[1, 1].bar(x + (bar_width * 1.5), par_balance, bar_width, label="Resident Set Size")
            bar_width = 0.15
            axes[1, 1].bar(x - (bar_width * 2.5), concat_length_expansion, bar_width, label="Concatenated length expansion")
            axes[1, 1].bar(x - (bar_width * 1.5), concat_actions_expansion, bar_width, label="Concatenated action expansion")
            axes[1, 1].bar(x - (bar_width * 0.5), concat_subplan_length_deviation, bar_width, label="Sub-plan length deviation")
            axes[1, 1].bar(x + (bar_width * 0.5), concat_subplan_actions_deviation, bar_width, label="Sub-plan action deviation")
            axes[1, 1].bar(x + (bar_width * 1.5), concat_subplan_length_balance, bar_width, label="Sub-plan length balance")
            axes[1, 1].bar(x + (bar_width * 2.5), concat_subplan_actions_balance, bar_width, label="Sub-plan action balance")
            axes[1, 1].set_xticks(x)
            axes[1, 1].set_xticklabels(xlabels)
            axes[1, 1].set_ylabel("Plan Refinement Expansion")
            # axes[1, 1].set_ylabel("Partial Problems/Plans")
            axes[1, 1].set_xlabel("Abstraction level")
            axes[1, 1].legend()
            
            # # Display the division points applied to this level;
            # #   - highlight proactively chosen division points in yellow,
            # #   - highlight reactively chosen division points in orange,
            # #   - highlight inherited divisions in red (the start and end of each division scenario).
            # division_points: list[Strategies.DivisionPoint] = hierarchical_plan.get_division_points(namespace.bottom_level + 1)
            
            # bottom_level_plan: Planner.MonolevelPlan = hierarchical_plan[namespace.bottom_level]
            
            # ## TODO add sequential yield steps
            # for time_type in regression_lines:
            #     for increment, line in regression_lines[time_type].items():
            #         axes[1, 0].plot(line["x_points"], line["y_points"], "green")
            #         axes[1, 0].plot(line["x_points"], line["func"](line["x_points"], *line["popt"]), color="red")
            
            # matching_child_steps: list[int] = []
            # if bottom_level_plan.conformance_mapping is not None:
            #     for step in bottom_level_plan:
            #         if bottom_level_plan.conformance_mapping.sgoals_achieved_at.reversed_get(step) is not None:
            #             matching_child_steps.append(step) 
            
            # max_y_points: int = max(y_points)
            
            # axes[1, 0].bar(bottom_level_plan.keys(), [max_y_points if step in matching_child_steps else 0 for step in bottom_level_plan],
            #             width=0.30, color="cyan", label="Matching children")
            # axes[1, 0].bar(bottom_level_plan.keys(), [max(y_points) if any(step == bottom_level_plan.conformance_mapping.sgoals_achieved_at.get(point.index, -1) and point.proactive and not point.inherited for point in division_points) else 0 for step in bottom_level_plan],
            #             width=0.30, color="yellow", label="Proactive divisions")
            # axes[1, 0].bar(bottom_level_plan.keys(), [max(y_points) if any(step == bottom_level_plan.conformance_mapping.sgoals_achieved_at.get(point.index, -1) - point.preemptive and point.reactive for point in division_points) else 0 for step in bottom_level_plan],
            #             width=0.30, color="blue", label="Reactive divisions")
            # axes[1, 0].bar(bottom_level_plan.keys(), [max(y_points) if any(step == bottom_level_plan.conformance_mapping.sgoals_achieved_at.get(point.index, -1) and point.inherited for point in division_points) else 0 for step in bottom_level_plan],
            #             width=0.30, color="red", label="Inherited divisions")
            # axes[1, 0].set_ylabel("Time (s)")
            # axes[1, 0].set_xlabel("Search length")
            # axes[1, 0].legend()
            
            # axes[1, 1].plot(bottom_level_plan.keys(), list(itertools.accumulate(1 if step in matching_child_steps else 0 for step in bottom_level_plan)),
            #                 color="cyan", label="Goal Progression (total achieved sub-goal stages)")
            # axes[1, 1].plot(bottom_level_plan.keys(), list(itertools.accumulate(((bottom_level_plan.conformance_mapping.get_subplan_length(index), index) if (index := bottom_level_plan.conformance_mapping.sgoals_achieved_at.reversed_get(step)[0]) is not None else None for step in bottom_level_plan),
            #                                                                     func=lambda value, init: ((init * (value[1] - 1)) + value[0]) / value[1] if value is not None else init)),
            #                 color="red", label="Expansion Factor (goal-wise)")
            # axes[1, 1].plot(bottom_level_plan.keys(), list(itertools.accumulate(1 if bottom_level_plan.conformance_mapping.sgoals_achieved_at.reversed_get(step) is not None else 0 for step in bottom_level_plan)),
            #                 width=bar_width, color="magenta", label="Expansion Deviation (goal-wise)")
            
            pyplot.show()
        
        
        
    else:
        ## Run the experiments
        experiment = Experiment.Experiment(planner,
                                           planning_function,
                                           namespace.initial_runs,
                                           namespace.experimental_runs,
                                           namespace.ash_output == "experiment")
        results: Experiment.Results = experiment.run_experiments()
        
        # if namespace.excel_file is not None:
        #     data.to_excel(namespace.excel_file)
        # if namespace.data_file is not None:
        #     data.to_dsv(namespace.data_file, sep=namespace.data_sep, endl=namespace.data_end)
        
        # if namespace.display_graph:
        #     xlabels = [str(n) for n in reversed(planner.domain.level_range)]
        #     x = numpy.arange(len(xlabels))
        #     bar_width = 0.30
            
        #     figure: matplotlib.figure.Figure
        #     figure, axis = matplotlib.pyplot.subplots()
        #     rects1 = axis.bar(x - bar_width, data.averages.grounding_time, bar_width, label="Average Grounding Time (s)")
        #     rects2 = axis.bar(x, data.averages.solving_time, bar_width, label="Average Solving Time (s)")
        #     rects3 = axis.bar(x + bar_width, data.averages.total_time, bar_width, label="Average Total Time (s)")
            
        #     axis.set_ylabel("Time (s)")
        #     axis.set_title(f"Average computation times per abstraction level :: {'Conformance Refinement' if namespace.planning_mode == 'hcr' else 'Classical'}")
        #     axis.set_xticks(x)
        #     axis.set_xticklabels(xlabels)
        #     axis.legend()
            
        #     matplotlib.pyplot.show()
    
    
    
    ## Return a clean exit
    return 0



def __setup() -> argparse.Namespace:
    ## Record launch time
    launch_time: datetime.datetime = datetime.datetime.now()
    output_file_append: str = launch_time.strftime('%Y-%m-%d_%H-%M-%S')
    
    ## Declare command line arguments parser
    parser = argparse.ArgumentParser(description="Launcher script for generating plans and running experiments with ASH. "
                                                 "Copyright (C) 2021 Oliver Michael Kamperis.")
    
    ## Inner function for creating options for Boolean arguments
    def bool_options(default: Optional[bool], const: Optional[bool] = True, add_none: bool = False) -> dict[str, Any]:
        """
        Create a Boolean argument.
        
        Parameters
        ----------
        `default: Optional[bool]` - The default argument value used when the argument is not given by the user.
        
        `const: Optional[bool] = True` - The standard argument value used when the argument is given without a value.
        
        `add_none: bool = False` - Whether to allow None to be valid arguments value.
        
        Returns
        -------
        `dict[str, Any]` - A dictionary of options for creating a Boolean argument.
        """
        choices: list[Optional[bool]] = [True, False]
        if add_none: choices.append(None)
        return dict(nargs="?", choices=choices, default=default, const=const,
                    type=lambda input_: None if input_ == "None" else input_ == "True")
    
    ## Inner function for processing optional number argument types
    def optional_number(value: str) -> Optional[Number]:
        if not value or value == "None":
            return None
        try:
            if '.' in value:
                return float(value)
            else: return int(value)
        except ValueError as error:
            print(f"Cannot parse {value} as a float or int: {error}")
            raise error
    
    ## Inner function for processing optional integer argument types
    def optional_int(value: str) -> Optional[int]:
        if not value or value == "None":
            return None
        try:
            return int(value)
        except ValueError as error:
            print(f"Cannot parse {value} as a float or int: {error}")
            raise error
    
    ## Inner function for processing optional string arguments types
    def optional_str(value: str) -> Optional[str]:
        if not value or value == "None":
            return None
        return value
    
    ## Special action for storing arguments of parameters that can have a different values for each abstraction level in the hierarchy
    class StoreHierarchicalArguments(argparse.Action):
        def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                     values: Sequence[str], option_string: Optional[str] = None):
            
            _values: Union[Number, dict[int, Number]] = {}
            
            try:
                if len(values) == 1 and '=' not in values[0]:
                    if ',' in values[0]:
                        _values = tuple(optional_number(v) for v in values[0].split(','))
                    else: _values = optional_number(values[0])
                else:
                    for key_value in values:
                        key, value = key_value.split('=', 1)
                        if ',' in value:
                            _values[int(key)] = tuple(optional_number(v) for v in value.split(','))
                        else: _values[int(key)] = optional_number(value)
            except ValueError as error:
                print(f"Error during parsing hierarchical argument '{option_string}': {error}")
                raise error
            
            setattr(namespace, self.dest, _values)
    
    ## Input files
    parser.add_argument("files", nargs="*", type=str,
                        help="a list of planning domain and problem files to load, at least one must be given")
    parser.add_argument("--display_loader", type=str,
                        help="display the contents of a ASH loader file")
    parser.add_argument("-rules", "--domain_rules", type=str,
                        help="the domain rules name from a ASH loader file")
    parser.add_argument("-struct", "--domain_structure", type=str,
                        help="the world structure name from a ASH loader file")
    parser.add_argument("-problem", "--problem_specifics", type=str,
                        help="the problem specification name from a ASH loader file")
    parser.add_argument("--load_schema", default=None, type=str,
                        help="specify a file to load a refinement schema from to generate problem spaces and check for dependencies between partial problems")
    
    ## Output files
    parser.add_argument("-pf", "--plan_file", default=f"./solutions/plans/ASH_Plan_{output_file_append}.txt", type=str,
                        help="specify a custom file to save the generated plans to during standard operation, "
                             f"by default ./plans/ASH_Plan_{output_file_append}.txt")
    parser.add_argument("-lf", "--log_file", default=f"./logs/ASH_Log_{output_file_append}.log", type=str,
                        help=f"specify a custom file to save the log file to, by default ./logs/ASH_Log_{output_file_append}.log")
    parser.add_argument("-xf", "--excel_file", nargs="?", default=None, const=f"./results/ASH_Excel_{output_file_append}.xlsx", type=str,
                        help="output experimental results to an excel (.xlsx) file, optionally specify a file name, "
                             f"as standard ./results/ASH_Excel_{output_file_append}.xlsx")
    parser.add_argument("-df", "--data_file", nargs="?", default=None, const=f"./results/ASH_Data_{output_file_append}.dat", type=str,
                        help="output experimental results to a Delimiter-Seperated Values (DSV) (.dat) file, "
                             f"optionally specify a file name, as standard ./results/ASH_Data_{output_file_append}.dat")
    parser.add_argument("-df_ds", "--data_sep", default=" ", type=str,
                        help="string specifying the delimiter between fields (values) of the output data file, by default ' '")
    parser.add_argument("-df_de", "--data_end", default="\n", type=str,
                        help="string specifying the delimiter between records (rows) of the output data file, by default '\\n'")
    parser.add_argument("-sf", "--save_schema", default=f"./solutions/schemas/ASH_Schema_{output_file_append}.txt", type=str,
                        help=f"specify a file name to save a schema to, by default ./solutions/schemas/ASH_Schema_{output_file_append}.txt")
    parser.add_argument("--schema_level", default=1, type=int,
                        help="specify an abstraction level to make a schema for, by default 1 (the ground level)")
    
    ## Header options
    parser.add_argument("-v", "--version", action="version", version=f"ASH - The ASP based Hierarchical Conformance Refinement Planner :: {_ASH_VERSION}")
    parser.add_argument("-w", "--warranty", action="store_true", help="show the program's warranty information on launch")
    parser.add_argument("-c", "--conditions", action="store_true", help="show the program's warranty conditions on launch")
    parser.add_argument("-i", "--instructions", action="store_true", help="show the program's instructions on launch and exit")
    
    ## Launcher options
    parser.add_argument("-ao", "--ash_output", choices=["verbose", "standard", "simple", "experiment"], default="simple", type=str,
                        help="the output verbosity of ASH; 'verbose' (full details of planned actions and the achievement sub-goal stages), "
                        "'standard' (only planned actions), 'simple' (tqdm progress bars, plans and results), "
                        "or 'experiment' (experiment tracking tqdm progress bars and results only), by default 'simple'")
    parser.add_argument("-co", "--clingo_output", **bool_options(default=False),
                        help="whether to enable output from Clingo, by default False")
    parser.add_argument("-cl", "--console_logging", choices=["DEBUG", "INFO", "WARN"], default="INFO",
                        help="the logging level to print to the console; 'DEBUG', 'INFO', or 'WARN', by default 'INFO'")
    parser.add_argument("--disable_logging", action="store_true",
                        help="disable all logging, removing all overhead on producing logs")
    parser.add_argument("-dpos", "--disable_pause_on_start", action="store_true", default=False,
                        help="disable the pause for user input when the planner starts")
    parser.add_argument("-dg", "--display_graph", **bool_options(default=True),
                        help="whether to display experimental results in a simple graph upon completion of all experimental runs")
    
    ## Experimentation options
    parser.add_argument("-op", "--operation", choices=["standard", "experiment", "find-problem-inconsistencies"], default="standard", type=str,
                        help="the operating mode of ASH; 'standard' (generate a single hierarchical refinement diagram and save the generated plans), "
                             "'experiment' (run the planner several times, generating a fresh plan each time, and gathering aggregate experimental statistics), "
                             "'find-problem-inconsistencies' (only generate the initial states and final goals, then return), by default 'standard'")
    parser.add_argument("-er", "--experimental_runs", default=1, type=int,
                        help="integer specifying number of experimental runs, by default 1")
    parser.add_argument("-ir", "--initial_runs", nargs="?", default=0, const=1, type=int,
                        help="integer specifying number of initial 'dry' runs before experimental results are recorded, by default 0, as standard 1")
    parser.add_argument("--pause_on_run_completion", **bool_options(default=False),
                        help="whether to pause execution of the benchmarking system after completion of each experimental run, by default False, as standard True")
    
    ## ASP solver options
    parser.add_argument("-th", "--threads", default=os.cpu_count(), type=int,
                        help=f"integer specifying number of solver threads, by default {os.cpu_count()} (your cpu count)")
    parser.add_argument("-tl", "--planning_time_limit", nargs="+", default=3600, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="maximum cumulative planning time limit in seconds, given as either a single value (used at all abstraction levels) or a dictionary of level-value pairs, by default 3600 (one hour)")
    parser.add_argument("-ll", "--search_length_limit", nargs="+", default=None, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="maximum search length limit, given as either a single value (used at all abstraction levels) or a dictionary of level-value pairs, by default None")
    
    ## ASH general options
    parser.add_argument("-m", "--planning_mode", choices=["hcr", "scr", "mcl", "hcl"], default="hcr", type=str,
                        help="what planning mode to use; 'hcr' (hierarchical conformance refinement), 'scr' (schema conformance refinement), 'mcl' (monolevel classical), or 'hcl' (hierarchical classical), by default 'hcr'")
    parser.add_argument("-t", "--conformance_type", choices=["sequential", "simultaneous"], default="sequential", type=str,
                        help="what conformance constraint type to use; 'sequential' (sub-goals of a stage can be achieved by any of its producing abstract action's children), "
                             "'simultaneous' (all sub-goals of a stage must be achieved by its producing abstract action's matching child), by default 'sequential'")
    parser.add_argument("-conc", "--enable_concurrency", **bool_options(default=False),
                        help="whether to enable action concurrency, by default False, as standard True")
    parser.add_argument("-mini_act", "--minimise_actions", **bool_options(default=None, add_none=True),
                        help="whether to enable the optimisation statement that minimises the number of actions in generated plans, "
                             "if None then the planner decides (chooses True if concurrency is enabled else False), by default None, as standard True")
    parser.add_argument("-yield", "--sequential_yielding", **bool_options(default=True),
                        help="whether to sequentially yield sub-plans as they are found by the incremental solver, this is more expensive than one-shot "
                             "(complete or divided) planning but allows refinement planning progress to be observed, by default False, as standard True")
    parser.add_argument("-detect_int", "--detect_interleaving", **bool_options(default=False),
                        help="whether to detect interleaving during sequential yielding, this is an expensive operation, by default False")
    parser.add_argument("-min_bound", "--minimum_search_length_bound", **bool_options(default=True),
                        help="whether to use the minimum search length bound to reduce search time at low search lengths, by default True")
    parser.add_argument("-obs", "--make_observable", **bool_options(default=False),
                        help="whether to make the plan that minimally achieves the previous in sequence sub-goal stage observable in sequential yield planning, "
                             "this is an expensive operation and ASH currently only uses this for debugging purposes, by default False, as standard True")
    
    ## Problem space generation options
    parser.add_argument("-space", "--problem_space", choices=["None", "search", "solution"], default=None, type=optional_str,
                        help="the type of problem space to generate; None (disable problem space generation), 'search' (the number of potential plans that may lead to a solution), "
                             "'solution' (the number of valid solutions), by default None. Note that in order to generate problem spaces a refinement schema must be loaded.")
    # parser.add_argument("--problem_space_level", default=1, type=int,
    #                     help="the level to generate the problem spaces at, by default 1 (the ground level)")
    # parser.add_argument("-sea_space", "--generate_search_space", **bool_options(default=False),
    #                     help="whether to generate the search space, this is generated step-wise and the goal-wise is extract automatically from the conformance mapping, by default False, as standard True")
    # parser.add_argument("-sol_space", "--generate_solution_space", **bool_options(default=False),
    #                     help="whether to generate the solution space, only one plan (the first) is refined in 'hcr' planning mode "
    #                          "and extended if problem division is enabled, the solution space type controls whether to generate the space goal-wise or problem-wise, by default False, as standard True")
    # parser.add_argument("-space_lim", "--problem_space_size_limit", nargs="?", default=0, const=1000, type=int,
    #                     help="the limit on the size of the problem space to generate, by default 0 (no limit), as standard 1000 (usually takes approximately a minute to generate)")
    # parser.add_argument("-sol_space_type", choices=["problem-wise", "goal-wise"], default="problem-wise", type=str,
    #                     help="the type of solution space to generate, 'problem-wise' generates the space at the end of each problem, "
    #                          "'goal-wise' generates it at the achievement of each sub-goal stage and is only avialable during sequential yield planning, by default 'problem-wise'")
    
    ## Hierarchical planning options
    parser.add_argument("-plc", "--pause_on_level_change", **bool_options(default=False),
                        help="whether to pause execution of the planner when the current planning level changes in hierarchical planning, by default False, as standard True")
    parser.add_argument("-pic", "--pause_on_increment_change", **bool_options(default=False),
                        help="whether to pause execution of the planner when the current planning increment changes in online planning, by default False, as standard True")
    parser.add_argument("-top", "--top_level", default=None, type=optional_int,
                        help="override the top level used in hierarchical planning, if not given or None then the hierarchical system law definition's top-level is used, by default None")
    parser.add_argument("-bot", "--bottom_level", default=1, type=int,
                        help="override the bottom level used in hierarchical planning, if not given then the bottom level is the ground level, by default 1 (the ground level)")
    
    ## Online planning options
    parser.add_argument("-method", "--online_method", choices=["ground-first", "complete-first", "hybrid"], default="ground-first", type=str,
                        help="what divided planning method to use; ground-first (solve only the initial partial problems first, propagating directly down to the ground level "
                             "as fast as possible, afterwards solve the lowest unsolved partial problem until the ground level is complete), 'complete-first' (solve all "
                             "partial problems at each level before moving to the next level, successively completing each level until the ground is reached), "
                             "or 'hybrid' (uses a mix of the prior, solve only the initial partial problems first, propagating directly down to the ground level as fast as possible, then successively complete each level), by default 'ground-first'")
    parser.add_argument("-strat", "--division_strategy", choices=["none", "basic", "steady", "hasty", "jumpy", "relentless", "impetuous", "rapid-basic", "rapid-steady", "rapid-hasty", "cautious", "reckless", "sensible", "audacious"], default="none", type=str,
                        help="the division strategy to use; 'none', 'basic', 'steady', 'hasty', 'cautious', 'reckless', 'sensible',  'impetuous', or 'audacious', by default 'none'")
    parser.add_argument("-bound", "--division_strategy_bounds", nargs="+", default=None, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="the bound used on the division strategy, this a maximum or minimum bound on the size, complexity, or planning time of the partial "
                             "problems as defined by the nature of the strategy itself, given as either a tuple of values (used at all abstraction levels) "
                             "or a dictionary of level-tuple pairs to set different bounds for each level, if None then the strategy takes its specific default bound, by default None")
    parser.add_argument("--bound_type", choices=["incremental", "differential", "integral", "cumulative"], default="incremental", type=str,
                        help="the type of bound used by reactive or adaptive strategies for their modifiable bound; 'incremental' (the total incremental planning time (seconds/step), averaged over the moving range), "
                             "'differential' (the rate of change (increase) in the total incremental planning time (seconds/step/step), averaged over the moving range), 'integral' (the sum of the total incremental planning times (seconds) over the moving range), "
                             "'predictive' (the predicted total incremental planning time of the next search step (seconds/step)), or "
                             "'cumulative' (the sum of all total incremental planning times (seconds) since the last reactive division, essentially an alias for an integral bound type with no range bound), by default 'incremental'")
    parser.add_argument("-horizon", "--backwards_horizon", nargs="+", default=0, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="the backwards horizon used when making continuous reactive divisions, continuous divisions cannot be commited until the horizon is reached, by default 0")
    parser.add_argument("-preempt", "--preemptive_division", **bool_options(default=False),
                        help="whether to use preemptive reactive division, this allows a reactive division to be commited on any child step of the current sub-goal stage, "
                             "otherwise if disabled reactive divisions can only be commited on a minimal matching child step (the step at which the current sub-goal stage was originally minimally achieved), by default False")
    parser.add_argument("-interrupt", "--interrupting_division", **bool_options(default=False),
                        help="whether to commit an interruting division when a reactive division is made, interrupting divisions are problem shifting, by default False")
    parser.add_argument("-average", "--moving_average", default=1, type=optional_int,
                        help="the number of previous incremental times to use to calculate a moving average when using an incremental time bound, "
                             "if a differential search time gradient bound is used then this is the amount of steps used to calculate the differential, "
                             "by default 1 (disables moving average mode), as standard None (uses a minimum number of steps to allow a gradient calculation)")
    parser.add_argument("-lblend", "--left_blend_quantities", nargs="+", default=0, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="the number of sub-goal stages to blend each partial problem with the previous adjacent partial problem in divided planning, "
                             "given as either a single value (used at all abstraction levels) or a dictionary of level-value pairs, by default 0 (disables left blending)")
    parser.add_argument("-rblend", "--right_blend_quantities", nargs="+", default=0, action=StoreHierarchicalArguments, type=str, metavar="value | level1=value1 level_i=value_i [...] level_n=value_n",
                        help="the number of sub-goal stages to blend each partial problem with the following adjacent partial problem in divided planning, "
                             "given as either a single value (used at all abstraction levels) or a dictionary of level-value pairs, by default 0 (disables right blending)")
    parser.add_argument("-avoid", "--avoid_refining_sgoals_marked_for_blending", **bool_options(default=False),
                        help="whether to avoid refining sub-goal stages marked for blending at the previous level, this is done by prohibiting proactively generated division scenarios "
                             "from dividing sub-goal stage inside the left blend of the right point of the current (partial) refinement planning problem, this can save overall planning time "
                             "by avoiding refining sub-goal stages that are guaranteed to be revised by blending at the higher abstraction levels but can reduce plan quality at the lower abstraction levels, "
                             "the more abstraction levels there are the more prevalent this trade-off becomes, by default False, as standard True")
    parser.add_argument("-inde_tasks", "--treat_tasks_as_independent", **bool_options(default=True),
                        help="overrides the division strategy used in tasking models to treat refining each individual task as an independent sub-problem at the next level, by default True")
    parser.add_argument("-save", "--save_grounding", **bool_options(default=False),
                        help="whether to save the ASP program grounding between divided planning increments, by default False, as standard True")
    parser.add_argument("-preempt_pos_fgoals", "--positive_final_goal_preemptive_achievement_heuristic", **bool_options(default=None, const=True, add_none=True),
                        help="whether to enable the ASP program heuristic that prefers choosing actions whose effects preemptively achieve positive final"
                             "goals, when there is an arbitrary choice available in non-final partial problems, by default None, as standard True")
    parser.add_argument("-preempt_neg_fgoals", "--negative_final_goal_preemptive_achievement_heuristic", **bool_options(default=None, const=True, add_none=True),
                        help="whether to enable the ASP program heuristic that prefers choosing actions whose effects preemptively achieve negative final"
                             "goals, when there is an arbitrary choice available in non-final partial problems, by default None, as standard True")
    parser.add_argument("-order_fgoals", "--final_goal_intermediate_achievement_ordering_preferences", **bool_options(default=None, const=True, add_none=True),
                        help="whether to enable optimisation of ordering preferences over the achievement of final-goals for tasking models, "
                             "if None then the planner decides (chooses True if a planning problem has a tasking model, False otherwise), by default None, as standard True")
    parser.add_argument("-detect_dep", "--detect_dependencies", **bool_options(default=False),
                        help="whether to detect dependencies between partial-problems in online planning, this is an expensive operation and occurs after solving the hierarchical planning problem by online planning,"
                             "this is done by complete planning at each level (using the fixed generated refinement schema) and comparing the generated plan qualities, by default False")
    ## This does not tell us the impact of the conformance constraining sub-goal stages being affected by dependencies between partial problems that divided the previous level from which those sub-goal stages were produced.
    
    ## Parse the arguments and return the namespace
    namespace: argparse.Namespace = parser.parse_args()
    
    ## Setup the logger
    if not namespace.disable_logging:
        logging.basicConfig(handlers=[logging.FileHandler(f"./logs/ASH_Log_{output_file_append}.log", "w", "utf-8")],
                            format="[%(asctime)s] %(levelname)-4s :: %(name)-8s >> %(message)s\n",
                            datefmt="%d-%m-%Y_%H-%M-%S",
                            level=logging.DEBUG)
        _Launcher_logger.debug(center_text(_ASH_TITLE, prefix_blank_line=True, framing_width=116, framing_char='#'))
        _Launcher_logger.debug(center_text(_ASH_WARRANTY, prefix_blank_line=True, framing_width=80))
        _Launcher_logger.debug(center_text(_ASH_CONDITIONS, prefix_blank_line=True, framing_width=80))
        _Launcher_logger.debug("Command line arguments:\n" + "\n".join(repr(item) for item in sys.argv[1:]))
        _Launcher_logger.debug("Parsed command line argumenys:\n" + "\n".join(repr(item) for item in namespace.__dict__.items()))
        
        ## Setup the console stream
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.__dict__[namespace.console_logging])
        console_handler.setFormatter(logging.Formatter("%(levelname)-4s :: %(name)-12s >> %(message)s\n"))
        logging.getLogger("").addHandler(console_handler)
    
    return namespace



## Launch ASH and enter main method
if __name__ == "__main__":
    start_real_time: float = time.perf_counter()
    start_process_time: float = time.process_time()
    exit_code: int = -1
    
    try:
        exit_code = __main()
    except BaseException as exception:
        _Launcher_logger.exception("Exception during main:\n", exc_info=exception)
    
    _Launcher_logger.info(f"Overall time: Real = {time.perf_counter() - start_real_time}, Process = {time.process_time() - start_process_time}")
    _Launcher_logger.info(f"Exiting with code {exit_code}")
    sys.exit(exit_code)
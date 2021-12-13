###########################################################################
###########################################################################
## Python script for running experiments with ASH                        ##
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

import logging
import statistics
import time
from typing import Any, Callable, Iterator, NamedTuple

import pandas
import tqdm
import numpy
from ASP_Parser import Statistics

import core.Planner as Planner
from core.Helpers import center_text
from core.Strategies import DivisionPoint, DivisionScenario

## Experiment module logger
_EXP_logger: logging.Logger = logging.getLogger(__name__)
_EXP_logger.setLevel(logging.DEBUG)

class Quantiles(NamedTuple):
    "Convenience class for representing quantiles."
    min: float = 0.0
    lower: float = 0.0
    med: float = 0.0
    upper: float = 0.0
    max: float = 0.0

class Results:
    "Encapsulates the results of experimental trails as a collection of hierarchical plans."
    
    __slots__ = ("__plans",
                 "__dataframes",
                 "__is_changed")
    
    def __init__(self) -> None:
        self.__plans: list[Planner.HierarchicalPlan] = []
        self.__dataframes: dict[str, pandas.DataFrame] = {}
        self.__is_changed: bool = False
    
    def __getitem__(self, index: int) -> Planner.HierarchicalPlan:
        return self.__plans[index]
    
    def __iter__(self) -> Iterator[Planner.HierarchicalPlan]:
        yield from self.__plans
    
    def __len__(self) -> int:
        return len(self.__plans)
    
    def add(self, plan: Planner.HierarchicalPlan) -> None:
        self.__plans.append(plan)
        self.__is_changed = True
    
    @property
    def mean(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["CAT"].drop("RU", axis="columns").groupby("AL").mean().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def std(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["CAT"].drop("RU", axis="columns").groupby("AL").std().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def step_wise_averages(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["STEP_CAT"].drop("RU", axis="columns").groupby(["AL", "SL"]).mean().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def step_wise_std(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["STEP_CAT"].drop("RU", axis="columns").groupby(["AL", "SL"]).std().sort_index(axis="index", ascending=False).reset_index()
    
    def best_quality(self) -> Planner.HierarchicalPlan:
        best_plan: Planner.HierarchicalPlan
        best_quality, best_length, best_actions = 0
        for hierarchical_plan in self.__plans:
            bottom_plan: Planner.MonolevelPlan = hierarchical_plan[hierarchical_plan.bottom_level]
            if (plan_quality := bottom_plan.calculate_plan_quality(best_length, best_actions)) > best_quality:
                best_plan = bottom_plan
                best_quality = plan_quality
                best_length = bottom_plan.plan_length
                best_actions = bottom_plan.total_actions
        return best_plan
    
    def process(self) -> dict[str, pandas.DataFrame]:
        "Process the currently collected data and return them as a pandas dataframe."
        if self.__dataframes is not None and not self.__is_changed:
            return self.__dataframes
        self.__is_changed = False
        
        ## Collate the data into a dictionary
        data_dict: dict[str, dict[str, list[float]]] = {}
        
        data_dict["PROBLEM_SEQUENCE"] = {"RU" : [], "SN" : [], "AL" : [], "IT" : [], "PN" : [], "SIZE" : []} ## TODO Account for blends in size?
        
        data_dict["DIVISION_SCENARIOS"] = {"RU" : [], "AL" : [], "SN" : [], "PLANS_CONCAT" : [], "SIZE" : []}
        
        data_dict["GLOBALS"] = {} ## TODO Absolution time, average wait time, average minimum execution time, average miniumum execution time per action
        
        data_dict["CAT"] = {"RU" : [], "AL" : [],
                            "GT" : [], "ST" : [], "OT" : [], "TT" : [], "LT" : [], "CT" : [], "WT" : [],
                            "RSS" : [], "VMS" : [],
                            "LE" : [], "AC" : [], "CF" : [], "PSG" : [],
                            "CP_EF_L" : [], "CP_EF_A" : [], "SP_ED_L" : [], "SP_ED_A" : [], "SP_EB_L" : [], "SP_EB_A" : [],
                            "SP_MIN_L" : [], "SP_MIN_A" : [], "SP_LOWER_L" : [], "SP_LOWER_A" : [], "SP_MED_L" : [], "SP_MED_A" : [], "SP_UPPER_L" : [], "SP_UPPER_A" : [], "SP_MAX_L" : [], "SP_MAX_A" : [],
                            "DS_T" : [], "DS_TD_MEAN" : [], "DS_TD_STD" : [], "DS_TD_CD" : [], "DS_TD_MIN" : [], "DS_TD_LOWER" : [], "DS_TD_MED" : [], "DS_TD_UPPER" : [], "DS_TD_MAX" : [],
                            "DS_TS_MEAN" : [], "DS_TS_STD" : [], "DS_TS_CD" : [], "DS_TS_MIN" : [], "DS_TS_LOWER" : [], "DS_TS_MED" : [], "DS_TS_UPPER" : [], "DS_TS_MAX" : []}
        
        data_dict["PAR"] = {"RU" : [], "AL" : [], "IT" : [],
                            "GT" : [], "ST" : [], "OT" : [], "TT" : [], "YT" : [], "WT" : [],
                            "RSS" : [], "VMS" : [],
                            "LE" : [], "AC" : [], "PSG" : []}
        
        data_dict["STEP_CAT"] = {"RU" : [], "AL" : [], "SL" : [],
                                 "S_GT" : [], "S_ST" : [], "S_TT" : [],
                                 "C_GT" : [], "C_ST" : [], "C_TT" : [],
                                 "T_RSS" : [], "T_VMS" : [], "M_RSS" : [], "M_VMS" : [],
                                 "C_TACHSGOALS" : [], "S_SGOALI" : [], "IS_MATCHING" : [],
                                 "C_CP_EF_L" : [], "C_CP_EF_A" : [], "C_SP_ED_L" : [], "C_SP_ED_A" : [], "C_SP_EB_L" : [], "C_SP_EB_A" : [],
                                 "IS_DIV_APP" : [], "IS_INHERITED" : [], "IS_PROACTIVE" : [], "IS_INTERRUPT" : [], "PREEMPTIVE" : [], "IS_DIV_COM" : [], "DIV_COM_APP_AT" : []}
                            #  "IS_LOCO" : [], "IS_MANI" : [], "IS_CONF" : []
        
        data_dict["INDEX_WISE"] = {"INDEX" : [], "NUM_SGOALS" : [],
                                   "SP_L" : [], "SP_A" : [],
                                   "INTER_Q" : [], "INTER_S" : [],
                                   "MAJORITY_TYPE" : []}
                                #    "SP_RE_GT" : [],
                                #    "SP_RE_ST" : [],
                                #    "SP_RE_TT" : []
        
        for run, hierarchical_plan in enumerate(self.__plans):
            for sequence_number, level, increment, problem_number in hierarchical_plan.get_hierarchical_problem_sequence():
                data_dict["PROBLEM_SEQUENCE"]["RU"].append(run)
                data_dict["PROBLEM_SEQUENCE"]["SN"].append(sequence_number)
                data_dict["PROBLEM_SEQUENCE"]["AL"].append(level)
                data_dict["PROBLEM_SEQUENCE"]["IT"].append(increment)
                data_dict["PROBLEM_SEQUENCE"]["PN"].append(problem_number)
                solution: Planner.MonolevelPlan = hierarchical_plan.partial_plans[level][increment]
                problem_size: int = 1
                if solution.is_refined:
                    problem_size = solution.conformance_mapping.problem_size
                data_dict["PROBLEM_SEQUENCE"]["SIZE"].append(problem_size)
            
            for level in reversed(hierarchical_plan.level_range):
                concatenated_plan: Planner.MonolevelPlan = hierarchical_plan.concatenated_plans[level]
                concatenated_totals: Planner.ASH_Statistics = concatenated_plan.planning_statistics.grand_totals
                data_dict["CAT"]["RU"].append(run)
                data_dict["CAT"]["AL"].append(level)
                
                ## Raw timing statistics
                data_dict["CAT"]["GT"].append(concatenated_totals.grounding_time)
                data_dict["CAT"]["ST"].append(concatenated_totals.solving_time)
                data_dict["CAT"]["OT"].append(concatenated_totals.overhead_time)
                data_dict["CAT"]["TT"].append(concatenated_totals.total_time)
                
                ## Hierarchical timing statistics
                data_dict["CAT"]["LT"].append(hierarchical_plan.get_latency_time(level))
                data_dict["CAT"]["CT"].append(hierarchical_plan.get_completion_time(level))
                data_dict["CAT"]["WT"].append(hierarchical_plan.get_average_wait_time(level))
                
                ## Required memory usage
                data_dict["CAT"]["RSS"].append(concatenated_totals.memory.rss)
                data_dict["CAT"]["VMS"].append(concatenated_totals.memory.vms)
                
                ## Concatenated plan quality
                data_dict["CAT"]["LE"].append(concatenated_plan.plan_length)
                data_dict["CAT"]["AC"].append(concatenated_plan.total_actions)
                data_dict["CAT"]["CF"].append(concatenated_plan.compression_factor)
                data_dict["CAT"]["PSG"].append(concatenated_plan.total_produced_sgoals)
                
                ## Sub-plan Expansion
                factor: Planner.Expansion = concatenated_plan.get_plan_expansion_factor()
                deviation: Planner.Expansion = concatenated_plan.get_expansion_deviation()
                balance: Planner.Expansion = concatenated_plan.get_degree_of_balance()
                data_dict["CAT"]["CP_EF_L"].append(factor.length)
                data_dict["CAT"]["CP_EF_A"].append(factor.action)
                data_dict["CAT"]["SP_ED_L"].append(deviation.length)
                data_dict["CAT"]["SP_ED_A"].append(deviation.action)
                data_dict["CAT"]["SP_EB_L"].append(balance.length)
                data_dict["CAT"]["SP_EB_A"].append(balance.action)
                
                sub_plan_expansion: list[Planner.Expansion] = []
                length_expansion = Quantiles()
                action_expansion = Quantiles()
                if concatenated_plan.is_refined:
                    for index in concatenated_plan.conformance_mapping.constraining_sgoals:
                        sub_plan_expansion.append(concatenated_plan.get_expansion_factor(index))
                    length_expansion = Quantiles(*numpy.quantile([sp.length for sp in sub_plan_expansion], [0.0, 0.25, 0.5, 0.75, 1.0]))
                    action_expansion = Quantiles(*numpy.quantile([sp.action for sp in sub_plan_expansion], [0.0, 0.25, 0.5, 0.75, 1.0]))
                
                data_dict["CAT"]["SP_MIN_L"].append(length_expansion.min)
                data_dict["CAT"]["SP_MIN_A"].append(action_expansion.min)
                data_dict["CAT"]["SP_LOWER_L"].append(length_expansion.lower)
                data_dict["CAT"]["SP_LOWER_A"].append(action_expansion.lower)
                data_dict["CAT"]["SP_MED_L"].append(length_expansion.med)
                data_dict["CAT"]["SP_MED_A"].append(action_expansion.med)
                data_dict["CAT"]["SP_UPPER_L"].append(length_expansion.upper)
                data_dict["CAT"]["SP_UPPER_A"].append(action_expansion.upper)
                data_dict["CAT"]["SP_MAX_L"].append(length_expansion.max)
                data_dict["CAT"]["SP_MAX_A"].append(action_expansion.max)
                
                ## Division Scenarios
                division_tree_level: list[DivisionScenario] = hierarchical_plan.problem_division_tree.get(level, [])
                total_divisions: int = len(division_tree_level)
                data_dict["CAT"]["DS_T"].append(total_divisions)
                
                divisions_per_scenario: list[int] = [scenario.get_total_divisions(False) for scenario in division_tree_level]
                mean_divisions: float = 0.0
                stdev_divisions: float = 0.0
                bal_divisions: float = 0.0
                quantiles_divisions = Quantiles()
                
                sizes_per_scenario: list[int] = [scenario.size for scenario in division_tree_level]
                mean_size: float = 0.0
                stdev_size: float = 0.0
                bal_size: float = 0.0
                quantiles_sizes = Quantiles()
                
                if total_divisions != 0:
                    mean_divisions = statistics.mean(divisions_per_scenario)
                    if len(divisions_per_scenario) >= 2:
                        stdev_divisions = statistics.stdev(divisions_per_scenario)
                    else: stdev_divisions = 0.0
                    bal_divisions = stdev_divisions / mean_divisions
                    quantiles_divisions = Quantiles(*numpy.quantile(divisions_per_scenario, [0.0, 0.25, 0.5, 0.75, 1.0]))
                    
                    mean_size = statistics.mean(sizes_per_scenario)
                    if len(sizes_per_scenario) >= 2:
                        stdev_size = statistics.stdev(sizes_per_scenario)
                    else: stdev_size = 0.0
                    bal_size = stdev_size / mean_size
                    quantiles_sizes = Quantiles(*numpy.quantile(sizes_per_scenario, [0.0, 0.25, 0.5, 0.75, 1.0]))
                
                data_dict["CAT"]["DS_TD_MEAN"].append(mean_divisions)
                data_dict["CAT"]["DS_TD_STD"].append(stdev_divisions)
                data_dict["CAT"]["DS_TD_CD"].append(bal_divisions)
                data_dict["CAT"]["DS_TD_MIN"].append(quantiles_divisions.min)
                data_dict["CAT"]["DS_TD_LOWER"].append(quantiles_divisions.lower)
                data_dict["CAT"]["DS_TD_MED"].append(quantiles_divisions.med)
                data_dict["CAT"]["DS_TD_UPPER"].append(quantiles_divisions.upper)
                data_dict["CAT"]["DS_TD_MAX"].append(quantiles_divisions.max)
                
                data_dict["CAT"]["DS_TS_MEAN"].append(mean_size)
                data_dict["CAT"]["DS_TS_STD"].append(stdev_size)
                data_dict["CAT"]["DS_TS_CD"].append(bal_size)
                data_dict["CAT"]["DS_TS_MIN"].append(quantiles_sizes.min)
                data_dict["CAT"]["DS_TS_LOWER"].append(quantiles_sizes.lower)
                data_dict["CAT"]["DS_TS_MED"].append(quantiles_sizes.med)
                data_dict["CAT"]["DS_TS_UPPER"].append(quantiles_sizes.upper)
                data_dict["CAT"]["DS_TS_MAX"].append(quantiles_sizes.max)
                
                ## Partial Problems
                # data_dict["CAT"]["PR_T"].append(len(hierarchical_plan.partial_plans[level]))
                # data_dict["CAT"]["PR_MS"]
                # data_dict["CAT"]["PR_DS"]
                # data_dict["CAT"]["PR_BS"]
                # data_dict["CAT"]["PR_MINS"]
                # data_dict["CAT"]["PR_MEDS"]
                # data_dict["CAT"]["PR_MAXS"]
                
                # ## Partial Plans TODO Add as a property calculated from PAR
                # data_dict["CAT"]["PP_ML"]
                # data_dict["CAT"]["PP_MA"]
                # data_dict["CAT"]["PP_DL"]
                # data_dict["CAT"]["PP_DA"]
                # data_dict["CAT"]["PP_BL"]
                # data_dict["CAT"]["PP_BA"]
                # data_dict["CAT"]["PP_MINL"]
                # data_dict["CAT"]["PP_MEDL"]
                # data_dict["CAT"]["PP_MAXL"]
                
                ## Step-wise
                grounding_time_sum: float = 0.0
                solving_time_sum: float = 0.0
                total_time_sum: float = 0.0
                rss_max: float = 0.0
                vms_max: float = 0.0
                for step, stats in concatenated_plan.planning_statistics.incremental.items():
                    data_dict["STEP_CAT"]["RU"].append(run)
                    data_dict["STEP_CAT"]["AL"].append(level)
                    data_dict["STEP_CAT"]["SL"].append(step)
                    
                    ## Accumlating plan costs
                    data_dict["STEP_CAT"]["S_GT"].append(stats.grounding_time)
                    data_dict["STEP_CAT"]["S_ST"].append(stats.solving_time)
                    data_dict["STEP_CAT"]["S_TT"].append(stats.total_time)
                    data_dict["STEP_CAT"]["C_GT"].append(grounding_time_sum := grounding_time_sum + stats.grounding_time)
                    data_dict["STEP_CAT"]["C_ST"].append(solving_time_sum := solving_time_sum + stats.solving_time)
                    data_dict["STEP_CAT"]["C_TT"].append(total_time_sum := total_time_sum + stats.total_time)
                    
                    data_dict["STEP_CAT"]["T_RSS"].append(stats.memory.rss)
                    data_dict["STEP_CAT"]["T_VMS"].append(stats.memory.vms)
                    data_dict["STEP_CAT"]["M_RSS"].append(rss_max := max(rss_max, stats.memory.rss))
                    data_dict["STEP_CAT"]["M_VMS"].append(vms_max := max(vms_max, stats.memory.vms))
                    
                    ## Conformance mapping
                    current_sgoals_index: int = 1
                    is_matching_child: bool = False
                    if concatenated_plan.is_refined:
                        current_sgoals_index = concatenated_plan.conformance_mapping.current_sgoals[step]
                        is_matching_child = step in concatenated_plan.conformance_mapping.sgoals_achieved_at.values()
                    data_dict["STEP_CAT"]["C_TACHSGOALS"] = current_sgoals_index - 1
                    data_dict["STEP_CAT"]["S_SGOALI"] = current_sgoals_index
                    data_dict["STEP_CAT"]["IS_MATCHING"] = is_matching_child
                    
                    ## Accumulating expansion factor
                    step_factor: Planner.Expansion = concatenated_plan.get_expansion_factor(range(1, current_sgoals_index + 1))
                    step_deviation: Planner.Expansion = concatenated_plan.get_expansion_deviation(range(1, current_sgoals_index + 1))
                    step_balance: Planner.Expansion = concatenated_plan.get_degree_of_balance(range(1, current_sgoals_index + 1))
                    data_dict["STEP_CAT"]["C_CP_EF_L"].append(step_factor.length)
                    data_dict["STEP_CAT"]["C_CP_EF_A"].append(step_factor.action)
                    data_dict["STEP_CAT"]["C_SP_ED_L"].append(step_deviation.length)
                    data_dict["STEP_CAT"]["C_SP_ED_A"].append(step_deviation.action)
                    data_dict["STEP_CAT"]["C_SP_EB_L"].append(step_balance.length)
                    data_dict["STEP_CAT"]["C_SP_EB_A"].append(step_balance.action)
                    
                    ## Problem divisions
                    division_points: list[DivisionPoint] = []
                    if concatenated_plan.is_refined:
                        hierarchical_plan.get_division_points(level + 1)
                    reached_point: DivisionPoint = None
                    committed_point: DivisionPoint = None
                    for point in division_points:
                        if is_matching_child and point.index == current_sgoals_index:
                            reached_point = point
                        if step == point.committed_step:
                            committed_point = point
                    data_dict["STEP_CAT"]["IS_DIV_APP"].append(reached_point is not None)
                    data_dict["STEP_CAT"]["IS_INHERITED"].append(reached_point is not None and reached_point.inherited)
                    data_dict["STEP_CAT"]["IS_PROACTIVE"].append(reached_point is not None and reached_point.proactive)
                    data_dict["STEP_CAT"]["IS_INTERRUPT"].append(reached_point is not None and reached_point.interrupting)
                    data_dict["STEP_CAT"]["PREEMPTIVE"].append(reached_point is not None and reached_point.preemptive)
                    data_dict["STEP_CAT"]["IS_DIV_COM"].append(committed_point is not None)
                    data_dict["STEP_CAT"]["DIV_COM_APP_AT"].append(committed_point is not None and committed_point.index)
                
                for iteration in hierarchical_plan.partial_plans[level]:
                    partial_plan: Planner.MonolevelPlan = hierarchical_plan.partial_plans[level][iteration]
                    partial_totals: Planner.ASH_Statistics = partial_plan.planning_statistics.grand_totals
                    data_dict["PAR"]["RU"].append(run)
                    data_dict["PAR"]["AL"].append(level)
                    data_dict["PAR"]["IT"].append(iteration)
                    
                    data_dict["PAR"]["GT"].append(partial_totals.grounding_time)
                    data_dict["PAR"]["ST"].append(partial_totals.solving_time)
                    data_dict["PAR"]["OT"].append(partial_totals.overhead_time)
                    data_dict["PAR"]["TT"].append(partial_totals.total_time)
                    
                    data_dict["PAR"]["YT"].append(hierarchical_plan.get_yield_time(level, iteration))
                    data_dict["PAR"]["WT"].append(hierarchical_plan.get_wait_time(level, iteration))
                    
                    data_dict["PAR"]["RSS"].append(partial_totals.memory.rss)
                    data_dict["PAR"]["VMS"].append(partial_totals.memory.vms)
                    
                    data_dict["PAR"]["LE"].append(partial_plan.plan_length)
                    data_dict["PAR"]["AC"].append(partial_plan.total_actions)
                    data_dict["PAR"]["PSG"].append(partial_plan.total_produced_sgoals)
        
        ## Create a Pandas dataframe from the data dictionary
        self.__dataframes = {key : pandas.DataFrame(data_dict[key]) for key in data_dict}
        return self.__dataframes
    
    def to_dsv(self, file: str, sep: str = " ", endl: str = "\n", index: bool = True) -> None:
        "Save the currently collected data to a Delimiter-Seperated Values (DSV) file."
        dataframes = self.process()
        dataframes["CAT"].to_csv(file, sep=sep, line_terminator=endl, index=index)
    
    def to_excel(self, file: str) -> None:
        "Save the currently collected data to an excel file."
        dataframes = self.process()
        writer = pandas.ExcelWriter(file, engine="xlsxwriter") # pylint: disable=abstract-class-instantiated
        
        dataframes["PROBLEM_SEQUENCE"].to_excel(writer, sheet_name="Problem Sequence")
        # dataframes["DIVISION_SCENARIOS"].to_excel(writer, sheet_name="Division Scenarios")
        
        dataframes["CAT"].to_excel(writer, sheet_name="Concat Plans")
        self.mean.to_excel(writer, sheet_name="Concat Level-Wise Aggregates", startrow=1)
        self.std.to_excel(writer, sheet_name="Concat Level-Wise Aggregates", startrow=(self.__plans[-1].top_level + 3))
        dataframes["PAR"].to_excel(writer, sheet_name="Partial Plans")
        
        dataframes["STEP_CAT"].to_excel(writer, sheet_name="Concat Step-wise")
        self.step_wise_averages.to_excel(writer, sheet_name="Concat Step-wise Mean") # (2 + len(dataframes["STEP_CAT"]))
        self.step_wise_std.to_excel(writer, sheet_name="Concat Step-wise Stdev") # (2 + (len(dataframes["STEP_CAT"]) * 2))
        
        writer.save()

class Experiment:
    "Encapsulates an experiment to be ran."
    
    __slots__ = ("__planner",
                 "__planning_function",
                 "__initial_runs",
                 "__experimental_runs",
                 "__enable_tqdm")
    
    def __init__(self,
                 planner: Planner.HierarchicalPlanner,
                 planning_function: Callable[[], Any],
                 initial_runs: int,
                 experimental_runs: int,
                 enable_tqdm: bool
                 ) -> None:
        
        self.__planner: Planner.HierarchicalPlanner = planner
        self.__planning_function: Callable[[], Any] = planning_function
        self.__initial_runs: int = initial_runs
        self.__experimental_runs: int = experimental_runs
        self.__enable_tqdm: bool = enable_tqdm
    
    def run_experiments(self) -> Results:
        "Run the encapsulated experiments and return a result object containing obtained statistics."
        results: Results = self.__run_all()
        dataframes = results.process()
        columns: list[str] = ["RU", "AL", "GT", "ST", "TT", "LT", "CT", "WT", "RSS", "VMS", "LE", "AC", "CF", "PSG"]
        _EXP_logger.info("\n\n" + center_text("Experimental Results", framing_width=40, centering_width=60)
                         + "\n\n" + center_text("Concatenated Plans", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + dataframes["CAT"].to_string(index=False, columns=columns)
                         + "\n\n" + center_text("Level-wise Means", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.mean.to_string(index=False, columns=columns[1:])
                         + "\n\n" + center_text("Level-wise Standard Deviation", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.std.to_string(index=False, columns=columns[1:])
                         + "\n\n" + center_text("Partial Plans", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + dataframes["PAR"].to_string(index=False))
        return results
    
    def __run_all(self) -> Results:
        _EXP_logger.info("\n\n" + center_text(f"Running experiments : Initial runs = {self.__initial_runs} : Experimental runs = {self.__experimental_runs}",
                                              framing_width=96, centering_width=100, framing_char="#"))
        
        results = Results()
        hierarchical_plan: Planner.HierarchicalPlan
        planning_time: float
        
        ## Do initial runs
        for run in tqdm.tqdm(range(1, self.__initial_runs + 1), desc="Initial runs completed", disable=not self.__enable_tqdm, leave=False, ncols=180, colour="white", unit="run"):
            hierarchical_plan, planning_time = self.__run()
            _EXP_logger.log(logging.DEBUG if self.__enable_tqdm else logging.INFO,
                            "\n\n" + center_text(f"Initial run {run} : Time {planning_time:.6f}s",
                                                 framing_width=48, centering_width=60))
        
        experiment_real_start_time = time.perf_counter()
        experiment_process_start_time = time.process_time()
        
        ## Do experimental runs
        for run in tqdm.tqdm(range(1, self.__experimental_runs + 1), desc="Experimental runs completed", disable=not self.__enable_tqdm, leave=False, ncols=180, colour="white", unit="run"):
            hierarchical_plan, planning_time = self.__run()
            results.add(hierarchical_plan)
            _EXP_logger.log(logging.DEBUG if self.__enable_tqdm else logging.INFO,
                            "\n\n" + center_text(f"Experimental run {run} : Time {planning_time:.6f}s",
                                                 framing_width=48, centering_width=60))
        
        experiment_real_total_time: float = time.perf_counter() - experiment_real_start_time
        experiment_process_total_time: float = time.process_time() - experiment_process_start_time
        
        _EXP_logger.info("\n\n" + center_text(f"Completed {self.__experimental_runs} experimental runs : "
                                              f"Real time {experiment_real_total_time:.6f}s, "
                                              f"Proccess time {experiment_process_total_time:.6f}s",
                                              framing_width=96, centering_width=100, framing_char="#"))
        
        return results
    
    def __run(self) -> tuple[Planner.HierarchicalPlan, float]:
        "Run the planner with this experiment's planning function once and return the plan."
        
        run_start_time: float = time.perf_counter()
        
        ## Generate one plan for run
        self.__planning_function()
        hierarchical_plan: Planner.HierarchicalPlan = self.__planner.get_hierarchical_plan()
        
        ## Ensure that the planner is purged after reach run
        self.__planner.purge_solutions()
        
        run_total_time: float = time.perf_counter() - run_start_time
        
        return hierarchical_plan, run_total_time

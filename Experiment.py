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
import time
from typing import Any, Callable, Iterator, Optional

import _collections_abc
import pandas
import tqdm

import ASP_Parser as ASP
import core.Planner as Planner
from core.Helpers import center_text

## Experiment module logger
_EXP_logger: logging.Logger = logging.getLogger(__name__)
_EXP_logger.setLevel(logging.DEBUG)

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
        
        max_: int = 100
        
        ## Collate the data into a dictionary
        data_dict: dict[str, dict[str, list[float]]] = {"CAT" : {"RU" : [], "AL" : [], "GT" : [], "ST" : [], "TT" : [], "LT" : [], "CT" : [], "RSS" : [], "VMS" : [], "LE" : [], "AC" : [], "PSG" : [], "CPE_L" : [], "CPE_A" : [], "SPD_L" : [], "SPD_A" : [], "SPB_L" : [], "SPB_A" : []},
                                                        "PAR" : {"RU" : [], "AL" : [], "IT" : [], "GT" : [], "ST" : [], "TT" : [], "RSS" : [], "VMS" : [], "LE" : [], "AC" : [], "PSG" : []}}
        
        for run, hierarchical_plan in enumerate(self.__plans):
            for level in reversed(hierarchical_plan.level_range):
                concatenated_plan: Planner.MonolevelPlan = hierarchical_plan.concatenated_plans[level]
                grand_totals: Planner.ASH_Statistics = concatenated_plan.planning_statistics.grand_totals
                data_dict["CAT"]["RU"].append(run)
                data_dict["CAT"]["AL"].append(level)
                
                data_dict["CAT"]["GT"].append(grand_totals.grounding_time)
                data_dict["CAT"]["ST"].append(grand_totals.solving_time)
                # data_dict["CAT"]["OT"].append(grand_totals.overhead_time)
                data_dict["CAT"]["TT"].append(grand_totals.total_time)
                
                data_dict["CAT"]["LT"].append(hierarchical_plan.get_latency_time(level))
                data_dict["CAT"]["CT"].append(hierarchical_plan.get_completion_time(level))
                data_dict["CAT"]["WT"].append(hierarchical_plan.get_average_wait_time(level))
                
                ## Required memory usage
                data_dict["CAT"]["RSS"].append(grand_totals.memory.rss)
                data_dict["CAT"]["VMS"].append(grand_totals.memory.vms)
                
                ## Concatenated plan quality
                data_dict["CAT"]["LE"].append(concatenated_plan.plan_length)
                data_dict["CAT"]["AC"].append(concatenated_plan.total_actions)
                data_dict["CAT"]["PSG"].append(concatenated_plan.total_produced_sgoals)
                
                ## Sub-plan Expansion
                factor: Planner.Expansion = concatenated_plan.get_plan_expansion_factor()
                deviation: Planner.Expansion = concatenated_plan.get_expansion_deviation()
                balance: Planner.Expansion = concatenated_plan.get_degree_of_balance()
                data_dict["CAT"]["CPE_L"].append(factor.length)
                data_dict["CAT"]["CPE_A"].append(factor.action)
                data_dict["CAT"]["SPD_L"].append(deviation.length)
                data_dict["CAT"]["SPD_A"].append(deviation.action)
                data_dict["CAT"]["SPB_L"].append(balance.length)
                data_dict["CAT"]["SPB_A"].append(balance.action)
                
                ## Division Scenarios
                hierarchical_plan.problem_division_tree[level][0].get_total_divisions(False)
                hierarchical_plan.problem_division_tree[level][0].size
                data_dict["CAT"]["DS_T"]
                data_dict["CAT"]["DS_MD"]
                data_dict["CAT"]["DS_DD"]
                data_dict["CAT"]["DS_BD"]
                data_dict["CAT"]["DS_MIND"]
                data_dict["CAT"]["DS_MEDD"]
                data_dict["CAT"]["DS_MAXD"]
                
                ## Partial Problems
                data_dict["CAT"]["PR_T"].append(len(hierarchical_plan.partial_plans[level]))
                data_dict["CAT"]["PR_MS"]
                data_dict["CAT"]["PR_DS"]
                data_dict["CAT"]["PR_BS"]
                data_dict["CAT"]["PR_MINS"]
                data_dict["CAT"]["PR_MEDS"]
                data_dict["CAT"]["PR_MAXS"]
                
                ## Partial Plans
                data_dict["CAT"]["PP_ML"]
                data_dict["CAT"]["PP_MA"]
                data_dict["CAT"]["PP_DL"]
                data_dict["CAT"]["PP_DA"]
                data_dict["CAT"]["PP_BL"]
                data_dict["CAT"]["PP_BA"]
                data_dict["CAT"]["PP_MINL"]
                data_dict["CAT"]["PP_MEDL"]
                data_dict["CAT"]["PP_MAXL"]
                
                for iteration in hierarchical_plan.partial_plans[level]:
                    partial_plan: Planner.MonolevelPlan = hierarchical_plan.partial_plans[level][iteration]
                    grand_totals: Planner.ASH_Statistics = partial_plan.planning_statistics.grand_totals
                    data_dict["PAR"]["RU"].append(run)
                    data_dict["PAR"]["AL"].append(level)
                    data_dict["PAR"]["IT"].append(iteration)
                    
                    data_dict["PAR"]["GT"].append(grand_totals.grounding_time)
                    data_dict["PAR"]["ST"].append(grand_totals.solving_time)
                    # data_dict["PAR"]["OT"].append(grand_totals.overhead_time)
                    data_dict["PAR"]["TT"].append(grand_totals.total_time)
                    
                    data_dict["PAR"]["YT"].append(hierarchical_plan.get_yield_time(level, iteration))
                    data_dict["PAR"]["WT"].append(hierarchical_plan.get_wait_time(level, iteration))
                    
                    data_dict["PAR"]["RSS"].append(grand_totals.memory.rss)
                    data_dict["PAR"]["VMS"].append(grand_totals.memory.vms)
                    
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
        dataframes["CAT"].to_excel(writer, sheet_name="Concatenated Plans")
        dataframes["PAR"].to_excel(writer, sheet_name="Partial Plans")
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
        _EXP_logger.info("\n\n" + center_text("Experimental Results", framing_width=40, centering_width=60)
                         + "\n\n" + center_text("Level-wise Means", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.mean.to_string(index=False)
                         + "\n\n" + center_text("Level-wise Standard Deviation", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.std.to_string(index=False)
                         + "\n\n" + center_text("Concatenated Plans", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + dataframes["CAT"].to_string(index=False)
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

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
                 "__dataframe",
                 "__is_changed")
    
    def __init__(self) -> None:
        self.__plans: list[Planner.HierarchicalPlan] = []
        self.__dataframe: Optional[pandas.DataFrame] = None
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
    def averages(self) -> ASP.Statistics:
        raise NotImplementedError
    
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
    
    def process(self) -> pandas.DataFrame:
        "Process the currently collected data and return them as a pandas dataframe."
        if self.__dataframe is not None and not self.__is_changed:
            return self.__dataframe
        
        self.__is_changed = False
        
        max_: int = 100
        
        ## Collate the data into a dictionary
        data_dict: dict[str, list[float]] = {"Run" : [], "Inc" : [], "AL" : [], "GT" : [], "ST" : [], "TT" : [], "L" : [], "A" : []}
        
        # for run, datum in enumerate(self.data):
        #     curr_step: dict[int, dict[int, int]] = {}
        #     for iteration in datum.statistics:
        #         curr_step[iteration] = {}
        #         for level in datum.statistics[iteration]:
        #             statistic: ASH_Statistic = datum.statistics[iteration][level]
        #             data_dict["RU"].append(run)
        #             data_dict["IT"].append(iteration)
        #             data_dict["AL"].append(level)
        #             data_dict["GT"].append(round(statistic.grounding_time, 6))
        #             data_dict["ST"].append(round(statistic.solving_time, 6))
        #             data_dict["TT"].append(round(statistic.total_time, 6))
        #             data_dict["S"].append(statistic.steps)
        #             data_dict["A"].append(statistic.actions)
                    
        #             for inner_iteration in datum.statistics:
        #                 if inner_iteration > iteration:
        #                     break
        #                 if level in datum.statistics[inner_iteration]:
        #                     inner_statistic: ASH_Statistic = datum.statistics[inner_iteration][level]
        #                 else: continue
        #                 if level not in curr_step[iteration]:
        #                     curr_step[iteration][level] = 0
        #                 for step in range(curr_step[iteration][level] + 1, max_ + 1):
        #                     if step - curr_step[iteration][level] in inner_statistic.inc_stats:
        #                         data_dict.setdefault(step, []).append(inner_statistic.inc_stats[step - curr_step[iteration][level]].total_time)
        #                     elif inner_iteration == iteration:
        #                         data_dict.setdefault(step, []).append(0.0)
        #                     else:
        #                         curr_step[iteration][level] = step - 1
        #                         break
        
        ## Create a Pandas dataframe from the data dictionary
        self.__dataframe = pandas.DataFrame(data_dict)
        return self.__dataframe
    
    def to_dsv(self, file: str, sep: str = " ", endl: str = "\n", index: bool = True) -> None:
        "Save the currently collected data to a Delimiter-Seperated Values (DSV) file."
        dataframe = self.process()
        dataframe.to_csv(file, sep=sep, line_terminator=endl, index=index)
    
    def to_excel(self, file: str) -> None:
        "Save the currently collected data to an excel file."
        dataframe = self.process()
        writer = pandas.ExcelWriter(file, engine="xlsxwriter") # pylint: disable=abstract-class-instantiated
        dataframe.to_excel(writer, sheet_name="Sheet1")
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
        results: Results = self.__run_all()
        dataframe: pandas.DataFrame = results.process()
        # _EXP_logger.info("\n\n" + center_text("Experimental Results", framing_width=40, centering_width=60)
        #                  + "\n\n" + dataframe.to_string(columns=["RU", "IT", "AL", "GT", "ST", "TT", "S", "A"], index=False))
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

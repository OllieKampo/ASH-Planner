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
from typing import Any, Callable, Iterator, NamedTuple, Optional

import pandas
import tqdm
import numpy
from ASP_Parser import Statistics

import core.Planner as Planner
from core.Helpers import center_text
from core.Strategies import DivisionPoint, DivisionScenario, SubGoalRange

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

def rmse(actual: list[int], perfect: list[float]) -> float:
    if len(actual) != len(perfect): raise ValueError("Actual and perfect point spread lists must have equal length.")
    return (sum(abs(obs - float(pred)) ** 2 for obs, pred in zip(actual, perfect)) / len(actual)) ** (0.5)

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
    def cat_level_wise_means(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["CAT"].drop("RU", axis="columns").groupby("AL").mean().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def cat_level_wise_stdev(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["CAT"].drop("RU", axis="columns").groupby("AL").std().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def par_level_wise_means(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["PAR"].drop(["RU", "IT"], axis="columns").groupby("AL").mean().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def par_level_wise_stdev(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["PAR"].drop(["RU", "IT"], axis="columns").groupby("AL").std().sort_index(axis="index", ascending=False).reset_index()
    
    @property
    def step_wise_means(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["STEP_CAT"].drop("RU", axis="columns").groupby(["AL", "SL"]).mean().sort_index(axis="index", ascending=True).reset_index()
    
    @property
    def step_wise_stdev(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["STEP_CAT"].drop("RU", axis="columns").groupby(["AL", "SL"]).std().sort_index(axis="index", ascending=True).reset_index()
    
    @property
    def index_wise_means(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["INDEX_CAT"].drop("RU", axis="columns").groupby(["AL", "INDEX"]).mean().sort_index(axis="index", ascending=True).reset_index()
    
    @property
    def index_wise_stdev(self) -> pandas.DataFrame:
        dataframes = self.process()
        return dataframes["INDEX_CAT"].drop("RU", axis="columns").groupby(["AL", "INDEX"]).std().sort_index(axis="index", ascending=True).reset_index()
    
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
        
        data_dict["GLOBALS"] = {"RU" : [], "EX_T" : [], "HA_T" : [], "AW_T" : [], "AME_T" : [], "AME_T_PA" : [], "BL_LE" : [], "BL_AC" : []}
        
        data_dict["PROBLEM_SEQUENCE"] = {"RU" : [], "SN" : [], "AL" : [], "IT" : [], "PN" : [],
                                         "START_S" : [], "IS_INITIAL" : [], "IS_FINAL" : [],
                                         "SIZE" : [],  "SGLITS_T" : [],
                                         "FIRST_I" : [], "LAST_I" : []}
                                        #  "L_BLEND" : [], "R_BLEND" : []
        
        data_dict["SCENARIOS"] = {"RU" : [], "AL" : [], "SN" : [],
                                  "SIZE" : [], "SGLITS_T" : [],
                                  "FIRST_I" : [], "LAST_I" : [],
                                  "DIVS" : [], "SPREAD" : []}
        
        data_dict["DIVISIONS"] = {"RU" : [], "AL" : [], "DN" : [],
                                  "APP_INDEX" : [], "COM_INDEX" : [], "COM_STEP" : [], "L_BLEND" : [], "R_BLEND" : [],
                                  "IS_INHERITED" : [], "IS_PROACTIVE" : [], "IS_INTERRUPT" : [], "PREEMPTIVE" : []}
        
        data_dict["CAT"] = {"RU" : [], "AL" : [],
                            "GT" : [], "ST" : [], "OT" : [], "TT" : [],
                            "LT" : [], "CT" : [], "WT" : [],
                            "RSS" : [], "VMS" : [],
                            "LE" : [], "AC" : [], "CF" : [], "PSG" : [],
                            "SIZE" : [], "SGLITS_T" : [],
                            "HAS_TRAILING" : [], "TOT_CHOICES" : [], "PRE_CHOICES" : [], "FGOALS_ORDER" : [],
                            "CP_EF_L" : [], "CP_EF_A" : [], "SP_ED_L" : [], "SP_ED_A" : [], "SP_EB_L" : [], "SP_EB_A" : [],
                            "SP_MIN_L" : [], "SP_MIN_A" : [], "SP_LOWER_L" : [], "SP_LOWER_A" : [], "SP_MED_L" : [], "SP_MED_A" : [], "SP_UPPER_L" : [], "SP_UPPER_A" : [], "SP_MAX_L" : [], "SP_MAX_A" : [],
                            "T_INTER_SP" : [], "P_INTER_SP" : [], "T_INTER_Q" : [], "P_INTER_Q" : [],
                            "M_CHILD_SPREAD" : [], "DIV_INDEX_SPREAD" : [], "DIV_STEP_SPREAD" : [],
                            "DIVS_T" : [], "DS_T" : [], "DS_TD_MEAN" : [], "DS_TD_STD" : [], "DS_TD_CD" : [],
                            "DS_TD_MIN" : [], "DS_TD_LOWER" : [], "DS_TD_MED" : [], "DS_TD_UPPER" : [], "DS_TD_MAX" : [],
                            "DS_TS_MEAN" : [], "DS_TS_STD" : [], "DS_TS_CD" : [],
                            "DS_TS_MIN" : [], "DS_TS_LOWER" : [], "DS_TS_MED" : [], "DS_TS_UPPER" : [], "DS_TS_MAX" : [],
                            "PR_T" : [], "PR_TS_MEAN" : [], "PR_TS_STD" : [], "PR_TS_CD" : [],
                            "PR_TS_MIN" : [], "PR_TS_LOWER" : [], "PR_TS_MED" : [], "PR_TS_UPPER" : [], "PR_TS_MAX" : [],
                            "PP_LE_MEAN" : [], "PP_AC_MEAN" : [], "PP_LE_STD" : [], "PP_AC_STD" : [], "PP_LE_CD" : [], "PP_AC_CD" : [], 
                            "PP_LE_MIN" : [], "PP_AC_MIN" : [], "PP_LE_LOWER" : [], "PP_AC_LOWER" : [], "PP_LE_MED" : [], "PP_AC_MED" : [], "PP_LE_UPPER" : [], "PP_AC_UPPER" : [], "PP_LE_MAX" : [], "PP_AC_MAX" : []}
        
        data_dict["PAR"] = {"RU" : [], "AL" : [], "IT" : [], "PN" : [],
                            "GT" : [], "ST" : [], "OT" : [], "TT" : [],
                            "YT" : [], "WT" : [], "ET" : [],
                            "RSS" : [], "VMS" : [],
                            "LE" : [], "AC" : [], "CF" : [], "PSG" : [],
                            "START_S" : [], "END_S" : [],
                            "SIZE" : [], "SGLITS_T" : [],
                            "FIRST_I" : [], "LAST_I" : [],
                            "TOT_CHOICES" : [], "PRE_CHOICES" : []}
        
        data_dict["STEP_CAT"] = {"RU" : [], "AL" : [], "SL" : [],
                                 "S_GT" : [], "S_ST" : [], "S_TT" : [],
                                 "C_GT" : [], "C_ST" : [], "C_TT" : [],
                                 "T_RSS" : [], "T_VMS" : [], "M_RSS" : [], "M_VMS" : [],
                                 "C_TACHSGOALS" : [], "S_SGOALI" : [], "IS_MATCHING" : [], "IS_TRAILING" : [],
                                 "C_CP_EF_L" : [], "C_CP_EF_A" : [], "C_SP_ED_L" : [], "C_SP_ED_A" : [], "C_SP_EB_L" : [], "C_SP_EB_A" : [],
                                 "IS_DIV_APP" : [], "IS_INHERITED" : [], "IS_PROACTIVE" : [], "IS_INTERRUPT" : [], "PREEMPTIVE" : [], "IS_DIV_COM" : [], "DIV_COM_APP_AT" : [],
                                 "IS_LOCO" : [], "IS_MANI" : [], "IS_CONF" : []}
        
        data_dict["INDEX_CAT"] = {"RU" : [], "AL" : [], "INDEX" : [],
                                  "NUM_SGOALS" : [], "ACH_AT" : [], "YLD_AT" : [],
                                  "IS_DIV" : [], "IS_INHERITED" : [], "IS_PROACTIVE" : [], "IS_INTERRUPT" : [], "PREEMPTIVE" : [],
                                  "SP_RE_GT" : [], "SP_RE_ST" : [], "SP_RE_TT" : [],
                                  "SP_L" : [], "SP_A" : [], "SP_START_S" : [], "SP_END_S" : [], "INTER_Q" : [],
                                  "IS_LOCO" : [], "IS_MANI" : [], "IS_CONF" : []}
        
        for run, hierarchical_plan in enumerate(self.__plans):
            data_dict["GLOBALS"]["RU"].append(run)
            data_dict["GLOBALS"]["EX_T"].append(hierarchical_plan.execution_latency_time)
            data_dict["GLOBALS"]["HA_T"].append(hierarchical_plan.absolution_time)
            data_dict["GLOBALS"]["AW_T"].append(hierarchical_plan.get_average_wait_time(hierarchical_plan.bottom_level))
            
            data_dict["GLOBALS"]["AME_T"].append(hierarchical_plan.get_average_minimum_execution_time(hierarchical_plan.bottom_level))
            data_dict["GLOBALS"]["AME_T_PA"].append(hierarchical_plan.get_average_minimum_execution_time(hierarchical_plan.bottom_level, per_action=True))
            
            data_dict["GLOBALS"]["BL_LE"].append(hierarchical_plan[hierarchical_plan.bottom_level].plan_length)
            data_dict["GLOBALS"]["BL_AC"].append(hierarchical_plan[hierarchical_plan.bottom_level].total_actions)
            
            for sequence_number, level, increment, problem_number in hierarchical_plan.get_hierarchical_problem_sequence():
                data_dict["PROBLEM_SEQUENCE"]["RU"].append(run)
                data_dict["PROBLEM_SEQUENCE"]["SN"].append(sequence_number)
                data_dict["PROBLEM_SEQUENCE"]["AL"].append(level)
                data_dict["PROBLEM_SEQUENCE"]["IT"].append(increment)
                data_dict["PROBLEM_SEQUENCE"]["PN"].append(problem_number)
                
                solution: Planner.MonolevelPlan = hierarchical_plan.partial_plans[level][increment]
                data_dict["PROBLEM_SEQUENCE"]["START_S"].append(solution.action_start_step)
                data_dict["PROBLEM_SEQUENCE"]["IS_INITIAL"].append(solution.is_initial)
                data_dict["PROBLEM_SEQUENCE"]["IS_FINAL"].append(solution.is_final)
                
                problem_size: int = 1
                sgoal_literals_total: int = 0
                sgoals_range = SubGoalRange(1, 1)
                # l_blend = 0; r_blend = 0
                if solution.is_refined:
                    problem_size = solution.conformance_mapping.problem_size
                    sgoal_literals_total = solution.conformance_mapping.total_constraining_sgoals
                    sgoals_range = solution.conformance_mapping.constraining_sgoals_range
                    # r_blend = hierarchical_plan.get_division_points(level + 1)[sequence_number - 1].blend.left
                    # r_blend = hierarchical_plan.get_division_points(level + 1)[sequence_number].blend.right
                
                data_dict["PROBLEM_SEQUENCE"]["SIZE"].append(problem_size)
                data_dict["PROBLEM_SEQUENCE"]["SGLITS_T"].append(sgoal_literals_total)
                data_dict["PROBLEM_SEQUENCE"]["FIRST_I"].append(sgoals_range.first_index)
                data_dict["PROBLEM_SEQUENCE"]["LAST_I"].append(sgoals_range.last_index)
                # data_dict["PROBLEM_SEQUENCE"]["L_BLEND"].append(l_blend)
                # data_dict["PROBLEM_SEQUENCE"]["R_BLEND"].append(r_blend)
            
            for level in reversed(hierarchical_plan.level_range):
                
                ## Division Points
                for division_number, division_point in enumerate(hierarchical_plan.get_division_points(level + 1)):
                    data_dict["DIVISIONS"]["RU"].append(run)
                    data_dict["DIVISIONS"]["AL"].append(level)
                    data_dict["DIVISIONS"]["DN"].append(division_number)
                    
                    data_dict["DIVISIONS"]["APP_INDEX"].append(division_point.index)
                    data_dict["DIVISIONS"]["COM_INDEX"].append(division_point.committed_index)
                    data_dict["DIVISIONS"]["COM_STEP"].append(division_point.committed_step)
                    data_dict["DIVISIONS"]["L_BLEND"].append(division_point.blend.left)
                    data_dict["DIVISIONS"]["R_BLEND"].append(division_point.blend.right)
                    
                    data_dict["DIVISIONS"]["IS_INHERITED"].append(division_point.inherited)
                    data_dict["DIVISIONS"]["IS_PROACTIVE"].append(division_point.proactive)
                    data_dict["DIVISIONS"]["IS_INTERRUPT"].append(division_point.interrupting)
                    data_dict["DIVISIONS"]["PREEMPTIVE"].append(division_point.preemptive)
                
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
                ## Threshold quality with 5s execution latency TODO
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
                
                ## Conformance constraints
                problem_size: int = 1
                total_sub_goal_literals: int = 0
                if concatenated_plan.is_refined:
                    problem_size = concatenated_plan.conformance_mapping.problem_size
                    total_sub_goal_literals = concatenated_plan.conformance_mapping.total_constraining_sgoals
                data_dict["CAT"]["SIZE"].append(problem_size)
                data_dict["CAT"]["SGLITS_T"].append(total_sub_goal_literals)
                
                ## Trailing plans
                data_dict["CAT"]["HAS_TRAILING"].append(concatenated_plan.has_trailing_plan)
                
                ## Final-goal preemptive achievement
                data_dict["CAT"]["TOT_CHOICES"].append(concatenated_plan.total_choices)
                data_dict["CAT"]["PRE_CHOICES"].append(concatenated_plan.preemptive_choices)
                
                ## Final-goal intermediate ordering preferences
                data_dict["CAT"]["FGOALS_ORDER"].append(bool(concatenated_plan.fgoal_ordering_correct))
                
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
                
                ## Interleaving
                interleaving: tuple[tuple[int, float], tuple[int, float]] = ((0, 0.0), (0, 0.0))
                if concatenated_plan.is_refined:
                    interleaving = concatenated_plan.interleaving
                data_dict["CAT"]["T_INTER_SP"].append(interleaving[0][0])
                data_dict["CAT"]["P_INTER_SP"].append(interleaving[0][1])
                data_dict["CAT"]["T_INTER_Q"].append(interleaving[1][0])
                data_dict["CAT"]["P_INTER_Q"].append(interleaving[1][1])
                
                ## Sub-plan (refinement tree) balancing, partial plan balancing, and division spread
                rmse_mchild: float = 0.0
                rmse_div_indices: float = 0.0
                rmse_div_steps: float = 0.0
                
                if concatenated_plan.is_refined:
                    perfect_mchild_spacing: float = concatenated_plan.plan_length / problem_size
                    perfect_mchild_spread: list[float] = [perfect_mchild_spacing * index for index in concatenated_plan.conformance_mapping.constraining_sgoals_range]
                    mchilds: list[int] = list(concatenated_plan.conformance_mapping.sgoals_achieved_at.values())
                    rmse_mchild = rmse(mchilds, perfect_mchild_spread)
                    
                    total_divisions: int = len(hierarchical_plan.get_division_points(level + 1))
                    total_problems: int = (total_divisions - 2) + 1
                    
                    if total_problems > 1:
                        perfect_div_index_spacing: float = concatenated_plan.conformance_mapping.total_constraining_sgoals / total_problems
                        perfect_div_index_spread: list[float] = [perfect_div_index_spacing * index for index in range(0, total_divisions)]
                        div_indices: list[int] = [point.index for point in hierarchical_plan.get_division_points(level + 1)]
                        rmse_div_indices = rmse(div_indices, perfect_div_index_spread)
                        
                        perfect_div_step_spacing: float = concatenated_plan.plan_length / total_problems
                        perfect_div_step_spread: list[float] = [perfect_div_step_spacing * index for index in range(0, total_divisions)]
                        div_steps: list[int] = [concatenated_plan.conformance_mapping.sgoals_achieved_at.get(point.index, 0) for point in hierarchical_plan.get_division_points(level + 1)]
                        rmse_div_steps = rmse(div_steps, perfect_div_step_spread)
                    
                    _EXP_logger.debug(f"Refinement spread at {run=}, {level=}: {rmse_mchild=}, {rmse_div_indices=}, {rmse_div_steps=}")
                
                ## The spread is the root mean squared error between;
                ##      - The final achieved matching child steps (representing the observed data),
                ##      - The theoretical perfectly balanced spread of matching child steps (representing the predicted data).
                ## The facet is that the perfect spacing is usually not achievable since the spacing will usually lie between steps since the plan length is usually not perfect
                data_dict["CAT"]["M_CHILD_SPREAD"].append(rmse_mchild)
                data_dict["CAT"]["DIV_INDEX_SPREAD"].append(rmse_div_indices)
                data_dict["CAT"]["DIV_STEP_SPREAD"].append(rmse_div_steps)
                
                ## Division Scenarios
                division_tree_level: list[DivisionScenario] = hierarchical_plan.problem_division_tree.get(level, [])
                total_scenarios: int = len(division_tree_level)
                data_dict["CAT"]["DS_T"].append(total_scenarios)
                
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
                
                total_divisions: int = sum(divisions_per_scenario)
                data_dict["CAT"]["DIVS_T"].append(total_divisions)
                
                if total_scenarios != 0:
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
                
                ## Scenario divisions
                data_dict["CAT"]["DS_TD_MEAN"].append(mean_divisions)
                data_dict["CAT"]["DS_TD_STD"].append(stdev_divisions)
                data_dict["CAT"]["DS_TD_CD"].append(bal_divisions)
                data_dict["CAT"]["DS_TD_MIN"].append(quantiles_divisions.min)
                data_dict["CAT"]["DS_TD_LOWER"].append(quantiles_divisions.lower)
                data_dict["CAT"]["DS_TD_MED"].append(quantiles_divisions.med)
                data_dict["CAT"]["DS_TD_UPPER"].append(quantiles_divisions.upper)
                data_dict["CAT"]["DS_TD_MAX"].append(quantiles_divisions.max)
                
                ## Scenario sizes
                data_dict["CAT"]["DS_TS_MEAN"].append(mean_size)
                data_dict["CAT"]["DS_TS_STD"].append(stdev_size)
                data_dict["CAT"]["DS_TS_CD"].append(bal_size)
                data_dict["CAT"]["DS_TS_MIN"].append(quantiles_sizes.min)
                data_dict["CAT"]["DS_TS_LOWER"].append(quantiles_sizes.lower)
                data_dict["CAT"]["DS_TS_MED"].append(quantiles_sizes.med)
                data_dict["CAT"]["DS_TS_UPPER"].append(quantiles_sizes.upper)
                data_dict["CAT"]["DS_TS_MAX"].append(quantiles_sizes.max)
                
                ## Partial Problems Size Balancing
                partial_plans: dict[int, Planner.MonolevelPlan] = hierarchical_plan.partial_plans.get(level, {})
                total_problems: int = len(partial_plans)
                
                ## Classical problems have size 1 (since they only include the final-goal),
                ## for refinement problems the final-goal takes the same index as the final-sub-goal stage (the stage produced from the final-goal achieving abstract action),
                ## this also relates to the representation of the last refinement tree abopting trailing plans.
                sizes_per_problem: list[int] = []
                if concatenated_plan.is_refined:
                    sizes_per_problem = [partial_plan.conformance_mapping.problem_size for partial_plan in partial_plans.values()]
                mean_problem_size: float = 1.0
                stdev_problem_size: float = 0.0
                bal_problem_size: float = 0.0
                quantiles_problem_size = Quantiles()
                
                if concatenated_plan.is_refined:
                    mean_problem_size = statistics.mean(sizes_per_problem)
                    if len(sizes_per_problem) >= 2:
                        stdev_problem_size = statistics.stdev(sizes_per_problem)
                    else: stdev_problem_size = 0.0
                    bal_problem_size = stdev_problem_size / mean_problem_size
                    quantiles_problem_size = Quantiles(*numpy.quantile(sizes_per_problem, [0.0, 0.25, 0.5, 0.75, 1.0]))
                
                data_dict["CAT"]["PR_T"].append(total_problems)
                data_dict["CAT"]["PR_TS_MEAN"].append(mean_problem_size)
                data_dict["CAT"]["PR_TS_STD"].append(stdev_problem_size)
                data_dict["CAT"]["PR_TS_CD"].append(bal_problem_size)
                data_dict["CAT"]["PR_TS_MIN"].append(quantiles_problem_size.min)
                data_dict["CAT"]["PR_TS_LOWER"].append(quantiles_problem_size.lower)
                data_dict["CAT"]["PR_TS_MED"].append(quantiles_problem_size.med)
                data_dict["CAT"]["PR_TS_UPPER"].append(quantiles_problem_size.upper)
                data_dict["CAT"]["PR_TS_MAX"].append(quantiles_problem_size.max)
                
                ## Partial Plan Length Balancing
                length_per_plan: list[int] = []
                actions_per_plan: list[int] = []
                if concatenated_plan.is_refined:
                    length_per_plan = [partial_plan.plan_length for partial_plan in partial_plans.values()]
                    actions_per_plan = [partial_plan.total_actions for partial_plan in partial_plans.values()]
                mean_plan_length: float = 1.0
                mean_total_actions: float = 1.0
                stdev_plan_length: float = 0.0
                stdev_total_actions: float = 0.0
                bal_plan_length: float = 0.0
                bal_total_actions: float = 0.0
                quantiles_plan_length = Quantiles()
                quantiles_total_actions = Quantiles()
                
                if concatenated_plan.is_refined:
                    mean_plan_length = statistics.mean(length_per_plan)
                    mean_total_actions = statistics.mean(actions_per_plan)
                    if len(length_per_plan) >= 2:
                        stdev_plan_length = statistics.stdev(length_per_plan)
                        stdev_total_actions = statistics.stdev(actions_per_plan)
                    else:
                        stdev_plan_length = 0.0
                        stdev_total_actions = 0.0
                    bal_plan_length = stdev_plan_length / mean_plan_length
                    bal_plan_length = stdev_total_actions / mean_total_actions
                    quantiles_plan_length = Quantiles(*numpy.quantile(length_per_plan, [0.0, 0.25, 0.5, 0.75, 1.0]))
                    quantiles_plan_length = Quantiles(*numpy.quantile(actions_per_plan, [0.0, 0.25, 0.5, 0.75, 1.0]))
                
                data_dict["CAT"]["PP_LE_MEAN"].append(mean_plan_length)
                data_dict["CAT"]["PP_AC_MEAN"].append(mean_total_actions)
                data_dict["CAT"]["PP_LE_STD"].append(stdev_plan_length)
                data_dict["CAT"]["PP_AC_STD"].append(stdev_total_actions)
                data_dict["CAT"]["PP_LE_CD"].append(bal_plan_length)
                data_dict["CAT"]["PP_AC_CD"].append(bal_total_actions)
                data_dict["CAT"]["PP_LE_MIN"].append(quantiles_plan_length.min)
                data_dict["CAT"]["PP_AC_MIN"].append(quantiles_total_actions.min)
                data_dict["CAT"]["PP_LE_LOWER"].append(quantiles_plan_length.lower)
                data_dict["CAT"]["PP_AC_LOWER"].append(quantiles_total_actions.lower)
                data_dict["CAT"]["PP_LE_MED"].append(quantiles_plan_length.med)
                data_dict["CAT"]["PP_AC_MED"].append(quantiles_total_actions.med)
                data_dict["CAT"]["PP_LE_UPPER"].append(quantiles_plan_length.upper)
                data_dict["CAT"]["PP_AC_UPPER"].append(quantiles_total_actions.upper)
                data_dict["CAT"]["PP_LE_MAX"].append(quantiles_plan_length.max)
                data_dict["CAT"]["PP_AC_MAX"].append(quantiles_total_actions.max)
                
                ## Step-wise
                grounding_time_sum: float = 0.0
                solving_time_sum: float = 0.0
                total_time_sum: float = 0.0
                rss_max: float = 0.0
                vms_max: float = 0.0
                
                for step in concatenated_plan:
                    
                    current_stat: Statistics = Statistics(0.0, 0.0)
                    for stat in concatenated_plan.planning_statistics.incremental.values():
                        if max(stat.step_range) == step:
                            current_stat = stat
                    
                    data_dict["STEP_CAT"]["RU"].append(run)
                    data_dict["STEP_CAT"]["AL"].append(level)
                    data_dict["STEP_CAT"]["SL"].append(step)
                    
                    ## Incremental and accumlating planning times
                    data_dict["STEP_CAT"]["S_GT"].append(current_stat.grounding_time)
                    data_dict["STEP_CAT"]["S_ST"].append(current_stat.solving_time)
                    data_dict["STEP_CAT"]["S_TT"].append(current_stat.total_time)
                    data_dict["STEP_CAT"]["C_GT"].append(grounding_time_sum := grounding_time_sum + current_stat.grounding_time)
                    data_dict["STEP_CAT"]["C_ST"].append(solving_time_sum := solving_time_sum + current_stat.solving_time)
                    data_dict["STEP_CAT"]["C_TT"].append(total_time_sum := total_time_sum + current_stat.total_time)
                    
                    ## Incremental and maximal memory
                    data_dict["STEP_CAT"]["T_RSS"].append(current_stat.memory.rss)
                    data_dict["STEP_CAT"]["T_VMS"].append(current_stat.memory.vms)
                    data_dict["STEP_CAT"]["M_RSS"].append(rss_max := max(rss_max, current_stat.memory.rss))
                    data_dict["STEP_CAT"]["M_VMS"].append(vms_max := max(vms_max, current_stat.memory.vms))
                    
                    ## Conformance mapping
                    current_sgoals_index: int = 1
                    is_matching_child: bool = False
                    is_trailing_plan: bool = False
                    if concatenated_plan.is_refined:
                        current_sgoals_index = concatenated_plan.conformance_mapping.current_sgoals.get(step, -1)
                        is_matching_child = step in concatenated_plan.conformance_mapping.sgoals_achieved_at.values()
                        is_trailing_plan = current_sgoals_index == -1
                    if is_trailing_plan:
                        current_sgoals_index = concatenated_plan.conformance_mapping.constraining_sgoals_range.last_index
                    data_dict["STEP_CAT"]["C_TACHSGOALS"].append(current_sgoals_index if is_matching_child else current_sgoals_index - 1)
                    data_dict["STEP_CAT"]["S_SGOALI"].append(current_sgoals_index)
                    data_dict["STEP_CAT"]["IS_MATCHING"].append(is_matching_child)
                    data_dict["STEP_CAT"]["IS_TRAILING"].append(is_trailing_plan)
                    
                    ## Accumulating expansion factor
                    index_range = range(1, current_sgoals_index + 1)
                    step_factor: Planner.Expansion = concatenated_plan.get_expansion_factor(index_range, accu_step=step)
                    step_deviation: Planner.Expansion = concatenated_plan.get_expansion_deviation(index_range, accu_step=step)
                    step_balance: Planner.Expansion = concatenated_plan.get_degree_of_balance(index_range, accu_step=step)
                    data_dict["STEP_CAT"]["C_CP_EF_L"].append(step_factor.length)
                    data_dict["STEP_CAT"]["C_CP_EF_A"].append(step_factor.action)
                    data_dict["STEP_CAT"]["C_SP_ED_L"].append(step_deviation.length)
                    data_dict["STEP_CAT"]["C_SP_ED_A"].append(step_deviation.action)
                    data_dict["STEP_CAT"]["C_SP_EB_L"].append(step_balance.length)
                    data_dict["STEP_CAT"]["C_SP_EB_A"].append(step_balance.action)
                    
                    ## Problem divisions
                    division_points: list[DivisionPoint] = []
                    if concatenated_plan.is_refined:
                        division_points = hierarchical_plan.get_division_points(level + 1)
                    reached_point: DivisionPoint = None
                    committed_point: DivisionPoint = None
                    for point in division_points:
                        if is_matching_child and point.index == current_sgoals_index:
                            reached_point = point
                        if step == point.committed_step:
                            committed_point = point
                    data_dict["STEP_CAT"]["IS_DIV_APP"].append(reached_point is not None) ## TODO Add the sequence number of the division point
                    data_dict["STEP_CAT"]["IS_INHERITED"].append(reached_point is not None and reached_point.inherited)
                    data_dict["STEP_CAT"]["IS_PROACTIVE"].append(reached_point is not None and reached_point.proactive)
                    data_dict["STEP_CAT"]["IS_INTERRUPT"].append(reached_point is not None and reached_point.interrupting)
                    data_dict["STEP_CAT"]["PREEMPTIVE"].append(reached_point is not None and reached_point.preemptive != 0)
                    data_dict["STEP_CAT"]["IS_DIV_COM"].append(committed_point is not None)
                    data_dict["STEP_CAT"]["DIV_COM_APP_AT"].append(committed_point.index if committed_point is not None else -1)
                    
                    ## Sub-plan majority action type
                    sub_plan_type: Planner.ActionType = concatenated_plan.get_action_type(step)
                    data_dict["STEP_CAT"]["IS_LOCO"].append(sub_plan_type == Planner.ActionType.Locomotion)
                    data_dict["STEP_CAT"]["IS_MANI"].append(sub_plan_type == Planner.ActionType.Manipulation)
                    data_dict["STEP_CAT"]["IS_CONF"].append(sub_plan_type == Planner.ActionType.Configuration)
                
                ## Index-wise
                if concatenated_plan.is_refined:
                    conformance_mapping: Planner.ConformanceMapping = concatenated_plan.conformance_mapping
                    constraining_sgoals: dict[int, list[Planner.SubGoal]] = conformance_mapping.constraining_sgoals
                    
                    for index in constraining_sgoals:
                        data_dict["INDEX_CAT"]["RU"].append(run)
                        data_dict["INDEX_CAT"]["AL"].append(level)
                        data_dict["INDEX_CAT"]["INDEX"].append(index)
                        
                        ## Number of sub-goal literals in the stage
                        data_dict["INDEX_CAT"]["NUM_SGOALS"].append(len(constraining_sgoals[index]))
                        
                        ## Final and sequential yield achievement step of the stage
                        data_dict["INDEX_CAT"]["ACH_AT"].append(conformance_mapping.sgoals_achieved_at[index])
                        yield_step: int = -1
                        if (yield_steps := conformance_mapping.sequential_yield_steps) is not None:
                            yield_step = yield_steps[index]
                        data_dict["INDEX_CAT"]["YLD_AT"].append(yield_step)
                        
                        ## Problem divisions
                        division_points: list[DivisionPoint] = []
                        if concatenated_plan.is_refined:
                            division_points = hierarchical_plan.get_division_points(level + 1)
                        
                        division_point: Optional[DivisionPoint] = None
                        for point in division_points:
                            if point.index == index:
                                division_point = point
                        data_dict["INDEX_CAT"]["IS_DIV"].append(division_point is not None)
                        data_dict["INDEX_CAT"]["IS_INHERITED"].append(division_point is not None and division_point.inherited)
                        data_dict["INDEX_CAT"]["IS_PROACTIVE"].append(division_point is not None and division_point.proactive)
                        data_dict["INDEX_CAT"]["IS_INTERRUPT"].append(division_point is not None and division_point.interrupting)
                        data_dict["INDEX_CAT"]["PREEMPTIVE"].append(division_point is not None and division_point.preemptive != 0)
                        
                        ## Sub-plan wise planning times
                        inc_stats: dict[int, Statistics] = concatenated_plan.planning_statistics.incremental
                        sub_plan_steps: list[int] = conformance_mapping.current_sgoals(index)
                        inc_stats = {step : inc_stats.get(step, Statistics(0.0, 0.0)) for step in sub_plan_steps}
                        data_dict["INDEX_CAT"]["SP_RE_GT"].append(sum(stat.grounding_time for stat in inc_stats.values()))
                        data_dict["INDEX_CAT"]["SP_RE_ST"].append(sum(stat.solving_time for stat in inc_stats.values()))
                        data_dict["INDEX_CAT"]["SP_RE_TT"].append(sum(stat.total_time for stat in inc_stats.values()))
                        
                        ## Refined sub-plan quality
                        index_factor: Planner.Expansion = concatenated_plan.get_expansion_factor(index)
                        data_dict["INDEX_CAT"]["SP_START_S"].append(min(sub_plan_steps))
                        data_dict["INDEX_CAT"]["SP_END_S"].append(max(sub_plan_steps))
                        data_dict["INDEX_CAT"]["SP_L"].append(index_factor.length)
                        data_dict["INDEX_CAT"]["SP_A"].append(index_factor.action)
                        
                        ## Sub-plan interleaving quantity
                        data_dict["INDEX_CAT"]["INTER_Q"].append(concatenated_plan.interleaving_quantity(index))
                        
                        ## Sub-plan majority action type
                        sub_plan_type: Planner.ActionType = concatenated_plan.get_sub_plan_type(index)
                        data_dict["INDEX_CAT"]["IS_LOCO"].append(sub_plan_type == Planner.ActionType.Locomotion)
                        data_dict["INDEX_CAT"]["IS_MANI"].append(sub_plan_type == Planner.ActionType.Manipulation)
                        data_dict["INDEX_CAT"]["IS_CONF"].append(sub_plan_type == Planner.ActionType.Configuration)
                
                ## Partial-Plans
                if hierarchical_plan.is_hierarchical_refinement:
                    for problem_number, iteration in enumerate(hierarchical_plan.partial_plans[level], start=1):
                        partial_plan: Planner.MonolevelPlan = hierarchical_plan.partial_plans[level][iteration]
                        partial_totals: Planner.ASH_Statistics = partial_plan.planning_statistics.grand_totals
                        data_dict["PAR"]["RU"].append(run)
                        data_dict["PAR"]["AL"].append(level)
                        data_dict["PAR"]["IT"].append(iteration)
                        data_dict["PAR"]["PN"].append(problem_number)
                        
                        ## Raw timing statistics
                        data_dict["PAR"]["GT"].append(partial_totals.grounding_time)
                        data_dict["PAR"]["ST"].append(partial_totals.solving_time)
                        data_dict["PAR"]["OT"].append(partial_totals.overhead_time)
                        data_dict["PAR"]["TT"].append(partial_totals.total_time)
                        
                        ## Online hierarchical planning statistics
                        data_dict["PAR"]["YT"].append(hierarchical_plan.get_yield_time(level, iteration))
                        data_dict["PAR"]["WT"].append(hierarchical_plan.get_wait_time(level, iteration))
                        data_dict["PAR"]["ET"].append(hierarchical_plan.get_minimum_execution_time(level, iteration))
                        
                        ## Required memory usage
                        data_dict["PAR"]["RSS"].append(partial_totals.memory.rss)
                        data_dict["PAR"]["VMS"].append(partial_totals.memory.vms)
                        
                        ## Partal plan quality
                        data_dict["PAR"]["LE"].append(partial_plan.plan_length)
                        data_dict["PAR"]["AC"].append(partial_plan.total_actions)
                        data_dict["PAR"]["CF"].append(partial_plan.compression_factor)
                        data_dict["PAR"]["PSG"].append(partial_plan.total_produced_sgoals)
                        data_dict["PAR"]["START_S"].append(partial_plan.action_start_step)
                        data_dict["PAR"]["END_S"].append(partial_plan.end_step)
                        
                        ## Conformance constraints
                        problem_size: int = 0
                        sgoal_literals_total: int = 0
                        sgoals_range = SubGoalRange(1, 1)
                        if partial_plan.is_refined:
                            problem_size = partial_plan.conformance_mapping.problem_size
                            sgoal_literals_total = partial_plan.conformance_mapping.total_constraining_sgoals
                            sgoals_range = partial_plan.conformance_mapping.constraining_sgoals_range
                        data_dict["PAR"]["SIZE"].append(problem_size)
                        data_dict["PAR"]["SGLITS_T"].append(sgoal_literals_total)
                        data_dict["PAR"]["FIRST_I"].append(sgoals_range.first_index)
                        data_dict["PAR"]["LAST_I"].append(sgoals_range.last_index)
                        
                        ## Final-goal preemptive achievement
                        data_dict["PAR"]["TOT_CHOICES"].append(partial_plan.total_choices)
                        data_dict["PAR"]["PRE_CHOICES"].append(partial_plan.preemptive_choices)
        
        ## Create a Pandas dataframe from the data dictionary
        # for key in data_dict:
        #     for _key in data_dict[key]:
        #         print(f"{_key}: {len(data_dict[key][_key])}")
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
        
        dataframes["GLOBALS"].to_excel(writer, sheet_name="Globals")
        
        dataframes["PROBLEM_SEQUENCE"].to_excel(writer, sheet_name="Problem Sequence")
        
        # dataframes["SCENARIOS"].to_excel(writer, sheet_name="Division Scenarios")
        
        dataframes["DIVISIONS"].to_excel(writer, sheet_name="Division Points")
        
        dataframes["CAT"].to_excel(writer, sheet_name="Cat Plans")
        self.cat_level_wise_means.to_excel(writer, sheet_name="Cat Level-Wise Aggregates", startrow=1)
        self.cat_level_wise_stdev.to_excel(writer, sheet_name="Cat Level-Wise Aggregates", startrow=(self.__plans[-1].top_level + 4))
        worksheet = writer.sheets["Cat Level-Wise Aggregates"]
        worksheet.write(0, 0, "Means")
        worksheet.write(self.__plans[-1].top_level + 3, 0, "Standard Deviation")
        
        dataframes["PAR"].to_excel(writer, sheet_name="Partial Plans")
        self.par_level_wise_means.to_excel(writer, sheet_name="Par Level-Wise Aggregates", startrow=1)
        self.par_level_wise_stdev.to_excel(writer, sheet_name="Par Level-Wise Aggregates", startrow=(self.__plans[-1].top_level + 4))
        worksheet = writer.sheets["Par Level-Wise Aggregates"]
        worksheet.write(0, 0, "Means")
        worksheet.write(self.__plans[-1].top_level + 3, 0, "Standard Deviation")
        
        dataframes["STEP_CAT"].to_excel(writer, sheet_name="Concat Step-wise")
        self.step_wise_means.to_excel(writer, sheet_name="Concat Step-wise Mean") # (2 + len(dataframes["STEP_CAT"]))
        self.step_wise_stdev.to_excel(writer, sheet_name="Concat Step-wise Stdev") # (2 + (len(dataframes["STEP_CAT"]) * 2))
        
        dataframes["INDEX_CAT"].to_excel(writer, sheet_name="Concat Index-wise")
        self.index_wise_means.to_excel(writer, sheet_name="Concat Index-wise Mean") # (2 + len(dataframes["STEP_CAT"]))
        self.index_wise_stdev.to_excel(writer, sheet_name="Concat Index-wise Stdev") # (2 + (len(dataframes["STEP_CAT"]) * 2))
        
        writer.save()

class Experiment:
    "Encapsulates an experiment to be ran."
    
    __slots__ = ("__planner",
                 "__planning_function",
                 "__bottom_level",
                 "__top_level",
                 "__initial_runs",
                 "__experimental_runs",
                 "__enable_tqdm")
    
    def __init__(self,
                 planner: Planner.HierarchicalPlanner,
                 planning_function: Callable[[], Any],
                 bottom_level: int,
                 top_level: int,
                 initial_runs: int,
                 experimental_runs: int,
                 enable_tqdm: bool
                 ) -> None:
        
        self.__planner: Planner.HierarchicalPlanner = planner
        self.__planning_function: Callable[[], Any] = planning_function
        self.__bottom_level: int = bottom_level
        self.__top_level: int = top_level
        self.__initial_runs: int = initial_runs
        self.__experimental_runs: int = experimental_runs
        self.__enable_tqdm: bool = enable_tqdm
    
    def run_experiments(self) -> Results:
        "Run the encapsulated experiments and return a result object containing obtained statistics."
        results: Results = self.__run_all()
        dataframes = results.process()
        columns: list[str] = ["RU", "AL", "GT", "ST", "OT", "TT", "LT", "CT", "WT", "RSS", "VMS", "LE", "AC", "CF", "PSG"]
        _EXP_logger.info("\n\n" + center_text("Experimental Results", framing_width=40, centering_width=60)
                         + "\n\n" + center_text("Concatenated Plans", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + dataframes["CAT"].to_string(index=False, columns=columns)
                         + "\n\n" + center_text("Level-wise Means", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.cat_level_wise_means.to_string(index=False, columns=columns[1:])
                         + "\n\n" + center_text("Level-wise Standard Deviation", frame_after=False, framing_char='~', framing_width=30, centering_width=60)
                         + "\n" + results.cat_level_wise_stdev.to_string(index=False, columns=columns[1:])
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
        hierarchical_plan: Planner.HierarchicalPlan = self.__planner.get_hierarchical_plan(bottom_level=self.__bottom_level,
                                                                                           top_level=self.__top_level)
        
        ## Ensure that the planner is purged after reach run
        self.__planner.purge_solutions()
        
        run_total_time: float = time.perf_counter() - run_start_time
        
        return hierarchical_plan, run_total_time

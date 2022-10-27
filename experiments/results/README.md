# Experimental Results

This directory contains the results from all experimental trials.
- Sub-directories `initial` and `main` are the raw results from the first and second sets of experiments in the thesis;
    - xlsx (Excel) files contain the full results,
    - dat files contain just results for concatenated monolevel plans in space seperated value format,
    - png files contain summary graphs displaying basic performance data only.
- Sub-directory `aggregate` contains the processed aggregrate results, including all tables and graphs presented in the thesis.
    - The cli command for generating each aggregate result set is given below.

## Raw Results Format and Column Headers

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the plan, step, or index | Integer |
| GT | Grounding time | Time taken to ground the logic program | Seconds |
| ST | Solving time | Time taken to solve the logic program | Seconds |
| OT | Overhead time | Time taken operate the sequential yield planning algorithm | Seconds |
| TT | Total time | Sum of all; grounding, solving, and overhead times | Seconds |
| LT | Latency time | The execution latency, yield time of the initial partial-plan | Seconds |
| CT | Completion time | The completion time, yield time of the final partial-plan | Seconds |
| WT | Wait time | The average wait time per partial-plan | Seconds |
| WT_PA | Wait time per action | The average wait time per action | Seconds |
| MET | Minimum execution time | The average minimum execution time per partial-plan | Seconds |
| MET_PA | Minimum execution time per action | The average minimum execution time per action | Seconds |
| RRS | Resident set size | The Resident Set Size, the non-swapped physical memory a process has used | Mega-bytes |
| VMS | Virtual memory size | The Virtual Memory Size, the total amount of virtual memory used by the process | Mega-bytes |
| LE | Plan length | The length (number of steps) of the plan | Integer |
| AC | Total actions | The total number of actions in a plan | Integer |
| CF | Compression factor | The percentage reduction in the plan length achieved by concurrent action planning | Ratio |
| PSG | Total produced sub-goals | The total number of sub-goal literals produced from the plan | Integer |
| SIZE | Problem size | The number of goals the problem achieves (number of sub-goal stages for refinement problems) | Integer |
| SGLITS_T | Total sub-goal literals | Total number of sub-goal literals in the plan's conformance constraint | Integer |
| QL_SCORE | Quality score |  |  |
| LT_SCORE | Latency score |  |  |
| CT_SCORE | Completion score |  |  |
| AW_SCORE | Average wait score |  |  |
| AW_PA_SCORE | Average wait per action score |  |  |
| AME_SCORE | Average minimum execution score |  |  |
| AME_PA_SCORE | Average minimum execution per action score |  |  |
| TI_SCORE | Overall time score |  |  |
| LT_GRADE | Latency grade |  |  |
| CT_GRADE | Completion grade |  |  |
| AW_GRADE | Average wait grade |  |  |
| AW_PA_GRADE | Average wait per action grade |  |  |
| AME_GRADE | Average minimum execution grade |  |  |
| AME_PA_GRADE | Average minimum execution per action grade |  |  |
| GRADE | Overall grade |  |  |
| HAS_TRAILING | Whether the (partial) monolevel plan has a trailing sub-plan |  |  |
| TOT_CHOICES | Total choices |  |  |
| PRE_CHOICES | Total pre-emptive final-goal achievement heuristic choices |  |  |
| FGOALS_ORDER | Whether the final-goal intermediate ordering preference was achieved |  |  |
| CP_EF_L | Complete plan length expansion factor |  |  |
| CP_EF_A | Complete plan action expansion factor |  |  |
| SP_ED_L | Sub-plan length expansion deviation |  |  |
| SP_ED_A | Sub-plan action expansion deviation |  |  |
| SP_EB_L | Sub-plan length expansion balance |  |  |
| SP_EB_A | Sub-plan action expansion balance |  |  |
| SP_EBS_L | Sub-plan length expansion balance score |  |  |
| SP_EBS_A | Sub-plan action expansion balance score |  |  |
| SP_MIN_L | Minimum sub-plan length |  |  |
| SP_MIN_A | Minimum sub-plan actions |  |  |
| SP_LOWER_L | Lower quartile sub-plan length |  |  |
| SP_LOWER_A | Lower quartile sub-plan actions |  |  |
| SP_MED_L | Median sub-plan length |  |  |
| SP_MED_A | Median sub-plan actions |  |  |
| SP_UPPER_L | Upper quartile sub-plan length |  |  |
| SP_UPPER_A | Upper quartile sub-plan actions |  |  |
| SP_MAX_L | Maximum sub-plan length |  |  |
| SP_MAX_A | Maximum sub-plan actions |  |  |
| T_INTER_SP | Total interleaved sub-plans |  |  |
| P_INTER_SP | Percentage of interleaved sub-plans |  |  |
| T_INTER_Q | Total interleaved plan steps |  |  |
| P_INTER_Q | Percentage interleaved plan steps |  |  |
| M_CHILD_RMSE | Root-mean-squared-error of matching child steps |  |  |
| M_CHILD_RMSE_SCORE | RMSE score |  |  |
| M_CHILD_NRMSE | Normalised RMSE of matching child steps |  |  |
| M_CHILD_NRMSE_SCORE | NRMSE score |  |  |
| M_CHILD_MAE |  |  |  |
| M_CHILD_MAE_SCORE |  |  |  |
| M_CHILD_NMAE |  |  |  |
| M_CHILD_NMAE_SCORE |  |  |  |
| DIV_INDEX_RMSE |  |  |  |
| DIV_INDEX_RMSE_SCORE |  |  |  |
| DIV_INDEX_NRMSE |  |  |  |
| DIV_INDEX_NRMSE_SCORE |  |  |  |
| DIV_INDEX_MAE |  |  |  |
| DIV_INDEX_MAE_SCORE |  |  |  |
| DIV_INDEX_NMAE |  |  |  |
| DIV_INDEX_NMAE_SCORE |  |  |  |
| DIV_STEP_RMSE |  |  |  |
| DIV_STEP_RMSE_SCORE |  |  |  |
| DIV_STEP_NRMSE |  |  |  |
| DIV_STEP_NRMSE_SCORE |  |  |  |
| DIV_STEP_MAE |  |  |  |
| DIV_STEP_MAE_SCORE |  |  |  |
| DIV_STEP_NMAE |  |  |  |
| DIV_STEP_NMAE_SCORE |  |  |  |
| DS_T |  |  |  |
| DIVS_T |  |  |  |
| DS_TD_MEAN |  |  |  |
| DS_TD_STD |  |  |  |
| DS_TD_CD |  |  |  |
| DS_TD_MIN |  |  |  |
| DS_TD_LOWER |  |  |  |
| DS_TD_MED |  |  |  |
| DS_TD_UPPER |  |  |  |
| DS_TD_MAX |  |  |  |
| DS_TS_MEAN |  |  |  |
| DS_TS_STD |  |  |  |
| DS_TS_CD |  |  |  |
| DS_TS_MIN |  |  |  |
| DS_TS_LOWER |  |  |  |
| DS_TS_MED |  |  |  |
| DS_TS_UPPER |  |  |  |
| DS_TS_MAX |  |  |  |
| PR_T |  |  |  |
| PR_TS_MEAN |  |  |  |
| PR_TS_STD |  |  |  |
| PR_TS_CD |  |  |  |
| PR_TS_MIN |  |  |  |
| PR_TS_LOWER |  |  |  |
| PR_TS_MED |  |  |  |
| PR_TS_UPPER |  |  |  |
| PR_TS_MAX |  |  |  |
| PP_LE_MEAN |  |  |  |
| PP_AC_MEAN |  |  |  |
| PP_LE_STD |  |  |  |
| PP_AC_STD |  |  |  |
| PP_LE_CD |  |  |  |
| PP_AC_CD |  |  |  |
| PP_LE_MIN |  |  |  |
| PP_AC_MIN |  |  |  |
| PP_LE_LOWER |  |  |  |
| PP_AC_LOWER |  |  |  |
| PP_LE_MED |  |  |  |
| PP_AC_MED |  |  |  |
| PP_LE_UPPER |  |  |  |
| PP_AC_UPPER |  |  |  |
| PP_LE_MAX |  |  |  |
| PP_AC_MAX |  |  |  |
| PP_ED_L |  |  |  |
| PP_ED_A |  |  |  |
| PP_EB_L |  |  |  |
| PP_EB_A |  |  |  |
| PP_EBS_L |  |  |  |
| PP_EBS_A |  |  |  |
| PP_EF_LE_MIN |  |  |  |
| PP_EF_AC_MIN |  |  |  |
| PP_EF_LE_LOWER |  |  |  |
| PP_EF_AC_LOWER |  |  |  |
| PP_EF_LE_MED |  |  |  |
| PP_EF_AC_MED |  |  |  |
| PP_EF_LE_UPPER |  |  |  |
| PP_EF_AC_UPPER |  |  |  |
| PP_EF_LE_MAX |  |  |  |
| PP_EF_AC_MAX |  |  |  |

## Aggregate Results Format



## Generating Aggregate Result Sets



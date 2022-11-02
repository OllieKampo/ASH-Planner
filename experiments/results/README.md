# Experimental Results

This directory contains the results from all experimental trials.
- Sub-directories `initial` and `main` are the raw results from the first and second sets of experiments in the thesis;
    - xlsx (Excel) files contain the full results,
    - dat files contain just results for concatenated monolevel plans in space seperated value format,
    - png files contain summary graphs displaying basic performance data only.
- Sub-directory `aggregate` contains the processed aggregrate results, including all tables and graphs presented in the thesis.
    - The cli command for generating each aggregate result set is given below.

__IMPORTANT:__ Due to a bug in the experiment system;
- In the globals for the initial and improved initial experiments, the average wait time per action is erroneously small. The time scores and grades are still correct, as the average wait time per action is not used for calculating those statistics.
- In the concatenated plans for the initial and improved initial experiments, the average wait time per action, and the average minimum execution time per action are all erroneously small. Therefore, the concatenated plan time scores and grades for all online experiments under these categories may be incorrect and must be ignored, and only the global time scores and grades are valid.
- In all results, action expansion factors, deviations, and balance may have small errors (length expansion factors etc are correct). These has resultantly been omitted from the thesis.

## Raw Results Format and Column Headers

The following are the column headers for all data in the raw results.
For columns headers for aggregate results, see the `aggregate` sub-directory.

### Globals

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| BL_LE |  |  |  |
| BL_AC |  |  |  |
| EX_T | Execution latency time | Yield time of the initial partial-plan |  |
| HA_T | Hierarchical absolution time | The time to generate an absolute hierarchical plan, for monolevel classical problems this is the ground-level monolevel planning time |  |  |
| AW_T |  |  |  |
| AW_T_PA |  |  |  |
| AME_T |  |  |  |
| AME_T_PA |  |  |  |
| QL_SCORE |  |  |  |
| EX_SCORE |  |  |  |
| HA_SCORE |  |  |  |
| AW_SCORE |  |  |  |
| AW_PA_SCORE |  |  |  |
| AME_SCORE |  |  |  |
| AME_PA_SCORE |  |  |  |
| TI_SCORE |  |  |  |
| EX_GRADE |  |  |  |
| HA_GRADE |  |  |  |
| AW_GRADE |  |  |  |
| AW_PA_GRADE |  |  |  |
| AME_GRADE |  |  |  |
| AME_PA_GRADE |  |  |  |
| GRADE |  |  |  |

### Problem Sequence

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| SN | The hierarchical problem sequence number |  |  |
| AL | Abstraction level | The abstraction level of the monolevel plan | Integer |
| IT |  |  |  |
| PN | The monolevel problem sequence number |  |  |
| START_S |  |  |  |
| IS_INITIAL |  |  |  |
| IS_FINAL |  |  |  |
| SIZE |  |  |  |
| SGLITS_T |  |  |  |
| FIRST_I |  |  |  |
| LAST_I |  |  |  |

### Division Points

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the problem division | Integer |
| DN | Division sequence number | Ordinal number of the problem division | Integer |
| APP_INDEX | The index the division is applied at | This is the actual index of the division | Integer |
| COM_INDEX | The index a reactive division was committed at | This is always the same as APP_INDEX, and was included to support a feature that was never used, for proactive division this is undefined taking a value of -1 | Integer |
| COM_STEP | The step a reactive division was committed at | This is the plan step at which the reactive division was committed during monolevel planning, for proactive division this is undefined taking a value of -1 | Integer |
| L_BLEND | The left blend quantity | This is the number of sub-goal stages that the true division index is extended to the left, the partial-problem to the right of the division revises the existing plan that refined the sub-goal stages in the left blend, this keeps their achievement non-greedy with respect to the sub-goal stages in the right problem | Integer |
| R_BLEND | The right blend quantity | This is the number of sub-goal stages that the true division index is extended to the right, the partial-problem to the left of the division is solved inclusive of the sub-goal stages in the right blend, this keeps the achievement of the sub-goal stages in the left problem non-greedy with respect the sub-goal stages in the right blend | Integer |
| IS_INHERITED | Whether the division is inherited | An inherited division is a division that is propagated from the previous abstraction level due to the effect of the online planning method on the construction and traversal of the problem division tree | Boolean |
| IS_PROACTIVE | Whether the division was committed proactively | A proactive division is committed over the combined refinement problem of an abstract plan immediately after the plan is generated and beofre it is refined, otherwise the division is reactive and was committed during refinement planning | Boolean |
| IS_INTERRUPT | Whether the division was an interrupting reactive division | An interrupting reactive division causes the monolevel planning algorithm to return when committed, affecting the hierarchical planning algorithm and the problem division tree, otherwise the division was continuous and is dealt with entirely within the monolevel planning algorithm, this will be false if the division was proactive | Boolean |
| PREEMPTIVE | Whether the reactive division was committed pre-emptively | A pre-emptive reactive division is one that is not committed on a step at which a sub-goal stage was minimally uniquely achieved | Boolean |

### Concatenated Plans (Cat Plans)

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the monolevel plan | Integer |
| GT | Grounding time | Time taken to ground the logic program | Seconds |
| ST | Solving time | Time taken to solve the logic program | Seconds |
| OT | Overhead time | Time taken operate the sequential yield planning algorithm | Seconds |
| TT | Total time | The total planning time, sum of all; grounding, solving, and overhead times | Seconds |
| LT | Latency time | The execution latency time, the yield time of the initial partial-plan | Seconds |
| CT | Completion time | The completion time, yield time of the final partial-plan | Seconds |
| WT | Wait time | The average wait time per partial-plan, the average over all partial-plans, of the time difference between the yield time of the given partial-plan minus the yield time of the previous | Seconds |
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
| QL_SCORE | Quality score | The ratio of the classical optimal number of actions over the number of actions in the given monolevel plan | Ratio |
| LT_SCORE | Latency score | The execution latency time score, between 1.0 and 0.0; 1.0 if LT is less than 5.0 seconds, otherwise 1.0 - (log(LT - 4.0) / log(3600.0)) | Ratio |
| CT_SCORE | Completion score | The execution completion time score, between 1.0 and 0.0; 1.0 if CT is less than 5.0 seconds, otherwise 1.0 - (log(CT - 4.0) / log(3600.0)) | Ratio |
| AW_SCORE | Average wait score | The average wait time score, between 1.0 and 0.0; 1.0 if WT is less than 5.0 seconds, otherwise 1.0 - (log(WT - 4.0) / log(3600.0)) | Ratio |
| AW_PA_SCORE | Average wait per action score | The average wait time per action score, between 1.0 and 0.0; 1.0 if WT_PA is less than 1.0 seconds, otherwise 1.0 - (log(WT_PA - 1.0) / log(3600.0)) | Ratio |
| AME_SCORE | Average minimum execution score | The average minimum execution time score, between 1.0 and 0.0; 1.0 if MET is less than 5.0 seconds, otherwise 1.0 - (log(MET - 4.0) / log(3600.0)) | Ratio |
| AME_PA_SCORE | Average minimum execution per action score | The average minimum execution time per action score, between 1.0 and 0.0; 1.0 if MET_PA is less than 1.0 seconds, otherwise 1.0 - (log(MET_PA - 4.0) / log(3600.0)) | Ratio |
| TI_SCORE | Overall time score | For classical plans, this is the completion time score, for conformance refinement plans, this is the mean of the; latency, average non-initial wait time, and average minimum execution time per action scores | Ratio |
| LT_GRADE | Latency grade | The latency time score multiplied by the quality score | Ratio |
| CT_GRADE | Completion grade | The completion time score multiplied by the quality score | Ratio |
| AW_GRADE | Average wait grade | The average wait time score multiplied by the quality score | Ratio |
| AW_PA_GRADE | Average wait per action grade | The average wait time per action score multiplied by the quality score | Ratio |
| AME_GRADE | Average minimum execution grade | The average minimum execution time score multiplied by the quality score | Ratio |
| AME_PA_GRADE | Average minimum execution per action grade | The average minimum execution time per action score multiplied by the quality score | Ratio |
| GRADE | Overall grade | The overall time score multiplied by the quality score | Ratio |
| HAS_TRAILING | Whether the (partial) monolevel plan has a trailing sub-plan | A trailing sub-plan, is a sub-plan that extends beyond the achievement of the final sub-goal stage, needed to achieve a more specific final-goal when refining from an abstract model that uses a state abstraction | Boolean |
| TOT_CHOICES | Total choices | The total choices the ASP solver made when selecting the truth values for atoms during search | Integer |
| PRE_CHOICES | Total final-goal pre-emptive achievement choices | The total number of choices made according to the final-goal pre-emptive achievement domain heuristics | Integer |
| FGOALS_ORDER | Whether the final-goal intermediate achievement ordering preference were satisfied | If the final-goal literals in the final-goal intermediate achievement ordering preferences where actually achieved in the preferred order | Boolean |
| CP_EF_L | Complete plan length expansion factor | The factor by which the length of the refined plan expands over the abstract (partial) plan it refines | Ratio |
| CP_EF_A | Complete plan action expansion factor | The factor by which the total number of actions in the refined plan expands over the abstract (partial) plan it refines | Ratio |
| SP_ED_L | Sub-plan length expansion deviation | The standard deviation in the lengths of the sub-plans that form the monolevel plan | Ratio |
| SP_ED_A | Sub-plan action expansion deviation | The standard deviation in the number of actions in the sub-plans that form the monolevel plan | Ratio |
| SP_EB_L | Sub-plan length expansion balance | The normalised length expansion deviation, the length expansion deviation as a factor of the expansion factor, this is the same as the coefficient of deviation | Ratio |
| SP_EB_A | Sub-plan action expansion balance | The normalised action expansion deviation | Ratio |
| SP_EBS_L | Sub-plan length expansion balance score | The reciprocal exponential of the length expansion balance, 1.0 when the expansion balance is 0.0 and rapidly approaches 0.0 as the expansion balance increases | Ratio |
| SP_EBS_A | Sub-plan action expansion balance score | The reciprocal exponential of the action expansion balance | Ratio |
| SP_MIN_L | Minimum sub-plan length |  | Integer |
| SP_MIN_A | Minimum sub-plan actions |  | Integer |
| SP_LOWER_L | Lower quartile sub-plan length |  | Integer |
| SP_LOWER_A | Lower quartile sub-plan actions |  | Integer |
| SP_MED_L | Median sub-plan length |  | Integer |
| SP_MED_A | Median sub-plan actions |  | Integer |
| SP_UPPER_L | Upper quartile sub-plan length |  | Integer |
| SP_UPPER_A | Upper quartile sub-plan actions |  | Integer |
| SP_MAX_L | Maximum sub-plan length |  | Integer |
| SP_MAX_A | Maximum sub-plan actions |  | Integer |
| T_INTER_SP | Total interleaved sub-plans | The quantity of sub-plans whose length increased from the minimal unique achievement of its sub-goal stage after the achievement of a following sub-goal stages as a result of interleaving delaying the achievement of the earlier sub-goal stage to better prepare for achieving one of the following and therefore reduce the overall plan length | Integer |
| P_INTER_SP | Percentage of interleaved sub-plans | The ratio of the number of interleaved sub-plans to the total number of sub-plans | Ratio |
| T_INTER_Q | Total interleaved plan steps | The sum over all sub-plans, of the increase in their length caused by interleaving | Integer |
| P_INTER_Q | Percentage interleaved plan steps | The ratio of the interleaving plan steps to the monolevel plan length | Ratio |
| M_CHILD_RMSE | Root-mean-squared-error of matching child steps | The error between the actual matching child steps (steps upon which a sub-goal stage was uniquely achieved in the monolevel plan) and the theoretically "perfectly" evenly spread matching child steps that would achieve an expansion deviation/balance of 0.0 (i.e. perfectly balanced refinement trees), measured as the root of the mean of the squared differences between each matching child's actual step and the ``perfect'' step, all M_CHILD... measures below are similar |  |
| M_CHILD_RMSE_SCORE | RMSE score |  |  |
| M_CHILD_NRMSE | Normalised RMSE | The M_CHILD_RMSE as a factor of the ``perfect'' sub-plan length that would achieve perfectly balanced refinement trees, all M_CHILD... normalised measures below are similar |  |
| M_CHILD_NRMSE_SCORE | NRMSE score |  |  |
| M_CHILD_MAE | Mean absolute error of matching child steps |  |  |
| M_CHILD_MAE_SCORE | MAE score |  |  |
| M_CHILD_NMAE | Normalised MAE | M_CHILD_MAE |  |
| M_CHILD_NMAE_SCORE | NMAE score |  |  |
| DIV_INDEX_RMSE | Root-mean-squared-error of division indices | The error between the actual division indices and the theoretically "perfectly" evenly spread indices that would achieve a perfectly homogenous problem sequence across the combined refinement problem this monolevel plan solves, measured as the root of the mean of the squared differences between each actual division index and the ``perfect'' index, all measures below are similar |  |
| DIV_INDEX_RMSE_SCORE |  |  |  |
| DIV_INDEX_NRMSE |  |  |  |
| DIV_INDEX_NRMSE_SCORE |  |  |  |
| DIV_INDEX_MAE |  |  |  |
| DIV_INDEX_MAE_SCORE |  |  |  |
| DIV_INDEX_NMAE |  |  |  |
| DIV_INDEX_NMAE_SCORE |  |  |  |
| DIV_STEP_RMSE | Root-mean-squared-error of division steps | The error between the actual division steps (the steps where the division indices were achieved) and the theoretically "perfectly" evenly spread steps that would achieve a perfectly homogenous partial-plan sequence that form this monolevel plan, measured as the root of the mean of the squared differences between each actual achievement steps and the ``perfect'' step, all measures below are similar |  |
| DIV_STEP_RMSE_SCORE |  |  |  |
| DIV_STEP_NRMSE |  |  |  |
| DIV_STEP_NRMSE_SCORE |  |  |  |
| DIV_STEP_MAE |  |  |  |
| DIV_STEP_MAE_SCORE |  |  |  |
| DIV_STEP_NMAE |  |  |  |
| DIV_STEP_NMAE_SCORE |  |  |  |
| DS_T | Total division scenarios |  |  |
| DIVS_T | Total divisions |  |  |
| DS_TD_MEAN | Mean divisions per scenario |  |  |
| DS_TD_STD | Standard deviation of divisions per scenario |  |  |
| DS_TD_CD | Coefficient of deviation of division per scenario |  |  |
| DS_TD_MIN | Minimum divisions per scenario |  |  |
| DS_TD_LOWER | Lower-quartile divisions per scenario |  |  |
| DS_TD_MED | Median divisions per scenario |  |  |
| DS_TD_UPPER | Upper-quartile divisions per scenario |  |  |
| DS_TD_MAX | Maximum divisions per scenario |  |  |
| DS_TS_MEAN | Mean size of division scenarios |  |  |
| DS_TS_STD | Standard deviation in size of division scenarios |  |  |
| DS_TS_CD | Coefficient of deviation in size of division scenarios |  |  |
| DS_TS_MIN |  |  |  |
| DS_TS_LOWER |  |  |  |
| DS_TS_MED |  |  |  |
| DS_TS_UPPER |  |  |  |
| DS_TS_MAX |  |  |  |
| PR_T | Total partial problems |  |  |
| PR_TS_MEAN | Mean partial-problem size |  |  |
| PR_TS_STD | Standard deviation in partial-problem size |  |  |
| PR_TS_CD | Coefficient of deviation in partial-problem size |  |  |
| PR_TS_MIN |  |  |  |
| PR_TS_LOWER |  |  |  |
| PR_TS_MED |  |  |  |
| PR_TS_UPPER |  |  |  |
| PR_TS_MAX |  |  |  |
| PP_LE_MEAN | Mean length of partial-plans | Meaningful only if multiple partial-plans were concatenated to form this monolevel plan (i.e. if PR_T > 0) |  |
| PP_AC_MEAN | Mean total actions of partial-plans |  |  |
| PP_LE_STD |  |  |  |
| PP_AC_STD |  |  |  |
| PP_LE_CD |  |  |  |
| PP_AC_CD |  |  |  |
| PP_LE_MIN |  |  | Integer |
| PP_AC_MIN |  |  | Integer |
| PP_LE_LOWER |  |  | Integer |
| PP_AC_LOWER |  |  | Integer |
| PP_LE_MED |  |  | Integer |
| PP_AC_MED |  |  | Integer |
| PP_LE_UPPER |  |  | Integer |
| PP_AC_UPPER |  |  | Integer |
| PP_LE_MAX |  |  | Integer |
| PP_AC_MAX |  |  | Integer |
| PP_ED_L | Partial-plan length expansion deviation |  | Ratio |
| PP_ED_A | Partial-plan action expansion deviation |  | Ratio |
| PP_EB_L | Partial-plan length expansion balance |  | Ratio |
| PP_EB_A | Partial-plan action expansion balance |  | Ratio |
| PP_EBS_L | Partial-plan length expansion balance score |  | Ratio |
| PP_EBS_A | Partial-plan action expansion balance score |  | Ratio |
| PP_EF_LE_MIN | Minimum partial-plan length expansion factor |  | Ratio |
| PP_EF_AC_MIN | Minimum partial-plan action expansion factor |  | Ratio |
| PP_EF_LE_LOWER | Lower-quartile partial-plan length expansion factor |  | Ratio |
| PP_EF_AC_LOWER | Lower-quartile partial-plan action expansion factor |  | Ratio |
| PP_EF_LE_MED | Median partial-plan length expansion factor |  | Ratio |
| PP_EF_AC_MED | Median partial-plan action expansion factor |  | Ratio |
| PP_EF_LE_UPPER | Upper-quartile partial-plan length expansion factor |  | Ratio |
| PP_EF_AC_UPPER | Upper-quartile partial-plan action expansion factor |  | Ratio |
| PP_EF_LE_MAX | Maximum partial-plan length expansion factor |  | Ratio |
| PP_EF_AC_MAX | Maximum partial-plan action expansion factor |  | Ratio |

### Partial Plans

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the partial-plan | Integer |
| IT | Online increment number |  | Integer |
| PN | Problem sequence number |  | Integer |
| GT |  |  |  |
| ST |  |  |  |
| OT |  |  |  |
| TT |  |  |  |
| YT |  |  |  |
| WT |  |  |  |
| ET |  |  |  |
| RSS |  |  |  |
| VMS |  |  |  |
| LE |  |  |  |
| AC |  |  |  |
| CF |  |  |  |
| PSG |  |  |  |
| START_S | Problem start step |  |  |
| END_S | Problem end step |  |  |
| SIZE |  |  |  |
| SGLITS_T |  |  |  |
| FIRST_I | First sub-goal stage index |  |  |
| LAST_I | Last sub-goal stagey |  |  |
| PP_EF_L |  |  |  |
| PP_EF_A |  |  |  |
| SP_ED_L |  |  |  |
| SP_ED_A |  |  |  |
| SP_EB_L |  |  |  |
| SP_EB_A |  |  |  |
| SP_EBS_L |  |  |  |
| SP_EBS_A |  |  |  |
| TOT_CHOICES |  |  |  |
| PRE_CHOICES |  |  |  |

### Concatenated Plan Step-Wise (Concat Step-Wise)

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the plan | Integer |
| SL |  |  |  |
| S_GT |  |  |  |
| S_ST |  |  |  |
| S_TT |  |  |  |
| C_GT |  |  |  |
| C_ST |  |  |  |
| C_TT |  |  |  |
| T_RSS |  |  |  |
| T_VMS |  |  |  |
| M_RSS |  |  |  |
| M_VMS |  |  |  |
| C_TACHSGOALS |  |  |  |
| S_SGOALI |  |  |  |
| IS_MATCHING |  |  |  |
| IS_TRAILING |  |  |  |
| C_CP_EF_L |  |  |  |
| C_CP_EF_A |  |  |  |
| C_SP_ED_L |  |  |  |
| C_SP_ED_A |  |  |  |
| C_SP_EB_L |  |  |  |
| C_SP_EB_A |  |  |  |
| C_SP_EBS_L |  |  |  |
| C_SP_EBS_A |  |  |  |
| IS_DIV_APP |  |  |  |
| IS_INHERITED |  |  |  |
| IS_PROACTIVE |  |  |  |
| IS_INTERRUPT |  |  |  |
| PREEMPTIVE |  |  |  |
| IS_DIV_COM |  |  |  |
| DIV_COM_APP_AT |  |  |  |
| IS_LOCO |  |  |  |
| IS_MANI |  |  |  |
| IS_CONF |  |  |  |

### Concatenated Plan Index-Wise (Concat Index-Wise)

| Header | Name | Description | Unit |
|:-:|:-:|:-:|:-:|
| RU | Run number | Ordinal number of the experimental run | Integer |
| AL | Abstraction level | The abstraction level of the plan | Integer |
| INDEX |  |  |  |
| NUM_SGOALS |  |  |  |
| ACH_AT |  |  |  |
| YLD_AT |  |  |  |
| IS_DIV |  |  |  |
| IS_INHERITED |  |  |  |
| IS_PROACTIVE |  |  |  |
| IS_INTERRUPT |  |  |  |
| PREEMPTIVE |  |  |  |
| SP_RE_GT |  |  |  |
| SP_RE_ST |  |  |  |
| SP_RE_TT |  |  |  |
| SP_START_S |  |  |  |
| SP_END_S |  |  |  |
| SP_L |  |  |  |
| SP_A |  |  |  |
| INTER_Q |  |  |  |
| IS_LOCO |  |  |  |
| IS_MANI |  |  |  |
| IS_CONF |  |  |  |

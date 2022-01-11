Final-goal preemptive achievement testing
-----------------------------------------

Tested in: heuristic and optimise mode.
For problems: small[1-3].
Configurations: two best performing online planning configurations from initial experiments adpated to include min-bound and sequential yield planning modes.

Sequential yield is tested again despite perfoming worse that min-bound in offline planning, because sequential yield must be used when making in reative divisions.
Hence, we need to see if there is a difference in which preemptive achievement mode is most effective for both min-bound and sequential yield.
The expectation is that optimise will be better for min-bound, since heuristic can detriment the search speed, and optimisation only has to be preformed on the single executable plan yield step.
Sequential yield however, has to optimise on every sequential yield step, due to the possibility of a reactive division being made and that plan being accepted as the partial solution up to the achievement of the most recently achieved sub-goal stage.
In this case, heuristic may perform better, as to overhead of optimising might be more than the loss of search speed caused by the heuristic modification to the search.
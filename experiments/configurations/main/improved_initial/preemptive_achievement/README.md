# Final-Goal Preemptive Achievement

Applicable only for online planning.

Tested in: heuristic and optimise mode.
For problems: small[1-3].
Configurations: two best performing online planning configurations from initial experiments according to following metrics; the 2-4 (best average overall grade) and the 4-4 (best average execution latency score) adpated to include min-bound and sequential yield planning modes.

The 4-4 configuration is tested, despite that it grades poorly, because it is the only configuration that consistently meets the minimum acceptable lag time, and the majority of the loss in plan quality appears to come from the unconsidered goal problem.
The conjecture is then, that if final-goal preemptive achievement works effectively, the average grade may exceed that of the other configurations.
Previously, there was little reason, to do more divisions, since the unconsidered goal problem had by far the biggest influence on plan quality.
Now that this problem has been mostly eliminated, the effects of the dependency problem can be more closely examined.

Sequential yield is tested again despite perfoming worse that min-bound in offline planning, because sequential yield must be used when making reative divisions.
Hence, we need to see if there is a difference in which preemptive achievement mode is most effective for both min-bound and sequential yield.
The expectation is that optimise will be better for min-bound, since heuristic can detriment the search speed, and optimisation only has to be preformed on the single executable plan yield step.
Sequential yield however, has to optimise on every sequential yield step, due to the possibility of a reactive division being made and that plan being accepted as the partial solution up to the achievement of the most recently achieved sub-goal stage.
In this case, heuristic may perform better, as to overhead of optimising might be more than the loss of search speed caused by the heuristic modification to the search

## Heuristic


## Optimise

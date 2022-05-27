# Modified Hierarchy Structures

These experimental configurations test various modifications to the planning domain definition's abstraction hierarchy structure used in the initial experiments.
Each of these different structures attempts to overcome the limitations of conformance refinement for solving the respective planning problem from the initial experiments.

For online experiments, the following constraints on the configurations are applied to reduce the number of overall experiments that need to be ran;
    - At least 4 ground-level partial problems must be obtained,
    - Cannot create more partial-problems per abstract plan combined problem division (creation of a division scenario) at the lower levels than at the higher levels,
    - Because we now have more levels in the hierarchy, to avoid the exponential increase in partial-problems, we allow for the option of no divisions being made over the combined refinement problem of an abstract plan (because of the previous constraint, this will only ever happen at the most abstract levels, and thus refinement problem will remain complete until at least 2 partial problems are created (by commiting at least 1 division)), and limit the maximum number of partial-problems created to be 3.

## Small problem 3 - Tasking model hierarchy:


## Small problem 3 - Split-hierarchy structure:
The split hierarchy structure splits the condensed and relaxed models, into two condensed and two relaxed models (giving a total of five abstraction levels in the hierachy), based on the type of action affected by the abstraction.
Manipulation and configuration actions are refined first, and locomotive actions are refined second.
The conjecture, is that this will achieve more balanced refinements whereby; all actions affected (whose constraints are removed/generalised by) an abstract model will have similar length sub-plans in the respective refinement, and all actions not affected will have unit length "trivial" refined sub-plans.

These are not tested for online planning, as this is not the intention behind the experimentation of this hierarchy structure, and there is not a good correspondence between the configurations used in the initial experiments and those that would be used in these experiments, because the number of hierarchy levels is increased there is not clear way to decide upon the number of divisions that should be commited per level, and how we would compare between these different possible configurations.

## Large problem 1 - Tasking model hierarchy:


## Large problem 2 - Double condensed model hierarchy:


## Large problem 3 - Tasking model and double condensed model hierachy:
Only included for offline planning for convenience, as we don't want to have to do any more offline planning beyond these experiments.
This problem is tested for online planning in the proactive and reactive division strategy experiments.
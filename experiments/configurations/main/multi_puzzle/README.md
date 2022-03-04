These experiments test the scalability of the approach to problems with much longer minimal plan lengths.
Some of the best performing configurations are tested for the larger multiple puzzle versions of the small and large problems.
Their performance relative to the single puzzle variants indicates how well this approach can performing when planning with large repetative problems.

Whilst the plan length compression achieved by concurrent action planning was able to overcome the limiting complexity of solving the top-level of large problem 1, this only alleviates the issue.
When the problems are extended by adding more puzzles, the plan length still becomes intractable, so the extra tasking level above the top-level is now needed, along with final-goal intermediate ordering preferences, to have the capacity to divide the problem at that level, and reduce the plan lengths to a point were they are tractable.

The original hierachy configurations are there simply to show that the top-level of the hierarchy is intractable to solve with such a large problem, and problem division is needed at that level, enabled by the new tasking level.

Likely if we added more problems, the tasking plans would begin to also become intractable to solve.
This hints at an important point, the number and extent of the abstraction necessitated/warranted ultimately most heavily impacted by the nature of the problem to be solved.

Much larger problems will require even more elaborate and extensive abstractions, which allow handling of many repetative tasks such as those involved in these multi-puzzle problems, perhaps by grouping/bundling them into even more abstract meta-level tasks.
Existing work has explored such a concept in a slightly different context and implementation in ASP based planning.
These could not currently be supported by the current HCR planning theory, because abstraction mappings between entities (in condensed models) are always disjunctive, rather than conjuctive.
A conjuctive mapping would be needed for an action whose effect was to move a set of objects to a particular location, as this should be achieved only when all those objects are in the location, rather than when any of them are in the location as would happen with a disjunctive mapping.
Therefore, to have meta-level tasking actions that act on abstract indentifiers that represent sets of entities, would demand support for conjunctive abstraction mappings.
A potential work around could involve adding defined fluents to define the conjunction mapping with state relations, but this could introduce problems between the connections between inertial and defined fluents at different levels of abstraction, and the capacity to reasoning about plan conformance and structural similarity of plans at different levels of abstraction may break down.
Of course, mappings between the codomain (value set) of fluents cannot be conjunctive, because fluents can only take unique values, but mappings between the domain (argument sets) of fluents could be conjunctive.
For example, a set X of objects are in location L, iff all x in X are in L.
The complexity comes in that the location of X becomes fuzzy when not all of x in X are in the same place, so it is not always possible to assign some meaningful unique value to the abstract fluent when planning at the original level, since there is not clear definition of where the set X of objects are.
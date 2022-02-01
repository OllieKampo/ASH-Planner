# Modified Hierarchy Structures

These experimental configurations test various modifications to the planning domain definition's abstraction hierarchy structure used in the initial experiments.
Each of these different structures attempts to overcome the limitations of conformance refinement for solving the respective planning problem from the initial experiments.

## Small problem 3 - Split-hierarchy structure:
The split hierarchy structure splits the condensed and relaxed models, into two condensed and two relaxed models (giving a total of five abstraction levels in the hierachy), based on the type of action affected by the abstraction.
Manipulation and configuration actions are refined first, and locomotive actions are refined second.

## Large problem 1 - Tasking model hierarchy:


## Large problem 2 - Double condensed model hierarchy:


## Large problem 3 - Tasking model and double condensed model hierachy:


## Offline Planning
Offline planning is tested only for sequential action planning and sequential sub-goal achievement with the minimum search length bound enabled.

## Online Planning
Online planning
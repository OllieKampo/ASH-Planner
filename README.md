# ASH - The Answer Set Programming based Hierarchical Conformance Refinement Planner for Intelligent Autonomous Robots

ASH is a planning system developed for automation of complex tasks and problems in the real world involving autonomous robotic agents.
ASH uses a novel conformance refinement approach to hierarchical planning, founded on an abstraction based method.
ASH is a general framework, that does not require any prescriptive knowledge from the designer.
ASH can find and yield only a partial plan initially, allowing the robot(s) to begin execution exponentially sooner than generating a complete plan prior to execution.
ASH then maintains and extends this partial solution over time, progressively yielding further contiguous partial solutions, towards eventual achievement of the final-goal.

## Structure

[ASH Components Dependency Diagram]

https://guides.github.com/features/mastering-markdown/

## Hierarchical Conformance Refinement Planning Problems

Conformance refinement planning problems are characterised by three aspects:
* An initial state - 
* A final-goal test - A set of positive and negative fluent state literals that must be simultaneously satisfied in the goal state,
* A sequence of sub-goal stages - 

A planning domains has been developed to test the proposed approach and its implementation.
__The Blocks World Plus (BWP)__ - An extension of the classic blocks world domain. A single robot named Talos must solve block world puzzles, in a combined logistics and manipulation planning domain.

Abstraction hierarchies are built by removing, generalising, or redefining system laws, in order to obtain simplified abstract models of the domain and problem.
There are three such abstract models currently supported by our theory and implementation.
* __Condensed Models__ - The state space is reduced, by automatically combining sets of detailed entities into abstract descriptors, this reduces the number of actions and state variables needed to represent the problem, and generalises planning constraints. Abstraction mappings are generated automatically.
* __Relaxed Models__ - A sub-set of action preconditions are removed, this removes significant constraints on planning. Abstraction mappings are generated automatically.
* __Tasking Models__ - The system laws are redefined to create a system representation that deals with abstract task descriptions, the resulting plan is a sequence of tasks to be completed in order. Abstraction mappings must be given manually by the designer, and tell the planner how it can complete tasks by reaching states of the original model.

Any discrete determinisitic planning domain and problem can be solved via conformance refinement, and can be represented by ASH.
The laws of a dynamic system are expressed axiomatically via non-monotonic logic rules.
These give the robot and understanding of the physical laws that govern its reality, and give it the descriptive knowledge it needs to reason for itself, and formulate plans.
* __Action Effects__ - "When a robot moves, its location changes" `effect(pl, R, move(L), in(R), L) :- action(pl, _, R, move(L)), fluent(pl, _, in(R), L), instance_of(pl, robot, R), instance_of(pl, location, L).`
* __Action Preconditions__ - "A robot can only grasp objects that share its location" `precond()`
* __State Variable Relations__ - "Grasped objects continue to share a robot's location as it moves" `holds(sl, in(O), L, t) :- holds(sl, in(R), L, t), holds(sl, grasping(R), O, t)`
This is a simple, intuitive, and yet highly expressive way to represent planning problems.

## Results

A small sub-set of our results are summarised in the table below.
Values given are as a percentage of the time taken by the classical approach to solving the problem.
Values in brackets are the raw times.

Planning Domain | Problem Instance | Execution Latency | Planning Time | Plan Quality
--------------- | ---------------- | ----------------- | ------------- | ------------
 | | | |
 | | | |

IMPORTANT: Due to a bug in the experiment system;
- The globals for the initial and improved initial experiments, the average wait time per action is erroneously small. The time scores and grades are still correct, as the average wait time per action is not used for calculating those statistics.
- The concatenated plans for the initial and improved initial experiments, the average wait time per action, and the average minimum execution time per action are all erroneously small. Therefore, the concatenated plan time scores and grades for all online experiments under these categories may be incorrect and must be ignored, and only the global time scores and grades are valid.

IMPORTANT: Due to an oversight, in all results, action expansion factors, deviations, and balance may have small errors. These has resultantly been omitted from the thesis.

## Installation

The frozen version of ASH has not been published as a python package.
This is because this version is only a prototype, and in the future a full version will be published.
Instead, to install ASH, you will need to download the repository.

ASH requires Python version 3.9.5, there is no guarantee it will be compatible on later versions, it is incompatible on 3.8.X or below.
It is dependent upon the following packages:
1. clingo
2. pandas
3. matplotlib
4. tqdm
These should be installed in order using pip or anaconda.

## Disclaimer

Some features of the planner are incomplete or not fully tested,
as they were cut from the thesis due to time constraints.
These were mostly removed from the implementation,
but some supporting code and documentation may still remain.

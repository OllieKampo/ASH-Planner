# ASH - The Answer Set Programming based Hierarchical Conformance Refinement Planner for Intelligent Autonomous Robots

ASH is a planning system developed for automation of complex tasks and problems in the real world involving autonomous robotic agents.
ASH uses a novel conformance refinement approach to hierarchical planning, founded on an abstraction based method.
ASH is a general framework, that does not require any prescriptive knowledge from the designer.
ASH can find and yield only a partial plan initially, allowing the robot(s) to begin execution exponentially sooner than generating a complete plan prior to execution.
ASH then maintains and extends this partial solution over time, progressively yielding further contiguous partial solutions, towards eventual achievement of the final-goal.

Conformance refinement planning problems are characterised by three aspects:
* An initial state - 
* A final-goal test - A set of positive and negative fluent state literals that must be simultaneously satisfied in the goal state,
* A sequence of sub-goal stages - 

Three domains have been developed to test the proposed approach and its implementation.
* __The Blocks World Plus (BWP)__ - An extension of the classic blocks world domain. A single robot named Talos must solve block world puzzles, in a combined logistics and manipulation planning domain.

## Conformance Refinement Domain Models

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

Important Note: Due to a bug, in the results for the initial experiments and improved initial, the average wait time per action in globals is erroneously small, and the average wait time per action, the average minimum execution time per action, and thus the time score and grade for online, in concatenated plans is also erroneously small.
Important Note: Due to an oversight, in all results, action expansion factors, deviations, and balance all erroneously large.

## Installation

ASH requires Python version 3.9.5, there is no guarantee it will be compatible on later versions, it is incompatible on 3.8.X or below.
It is dependent upon the following packages:
1. clingo
2. pandas
3. matplotlib
4. tqdm
These should be installed in order using the anaconda installer (not pip).

ASH is available via the conda package manager.
Doing this will also install all its dependencies automatically.
Simply use the following in the desired anaconda environment:
```
conda activate <desired_virtual_environment>
conda install ASH
```

Congratualations, you now have ASH installed, and you are ready to start planning.
To test your install you can run the following command to run the easiest problem instance in the BWP planning domain (it should take no more than a few seconds to complete).

```
python ASH_Launch.py "./test_domains/blocks_world_plus/BWP_loader.json" --laws=simple --world=small --prob=easy
```

Alternatively, you can simply clone this repository.
Please note the copyright notice attached to this repository.

## Example Usage

```
import ASH

planner = ASH.Planning.Planner.HierarchicalPlanner(silent=True)
planner.tmol_load("./domains/blocks_world_plus/BWP_loader.json", system_laws="simple", world_structure="small", problem_instance="easy")

plan: ASH.Planning.Plans.HierarchicalPlan = planner.generate_hierarchical_plan(strategy=ASH.Planning.Strategies.Steady(bound=5))
plan.pretty_print()
```

## Disclaimer

Should features of the planner are incomplete or untested.
Unfortunately, some features were cut from the thesis due to time constraints.
These were removed from the implementation, but some supporting code still remains.

## Structure

[ASH Components Dependency Diagram]

https://guides.github.com/features/mastering-markdown/
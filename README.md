# ASH - The Answer Set Programming based Hierarchical Conformance Refinement Planner for Robots

ASH is an online autonomous task and high-level action planning system for complex discrete deterministic planning problems, built in Answer Set Programming (ASP).

ASH uses a novel divide-and-conquer based approach to online hierarchical planning, which enables it to generate and incrementally yield partial plans throughout plan execution.
This ability can reduces execution latency and total planning times exponentially over the existing state-of-the-art ASP based planners, and for first time places ASP as a practical tool for real-world/time robotics problems.

The primary desirable characteristic of ASP is its intuitive and highly elaboration tolerent language for knowledge representation and reasoning.
It provides the ability to represent a dynamic system through a set of intuitve axiomatic rules with define the fundamental physical laws of a that system.
This give a robot an understanding of the constraints that govern its reality and enable it to reason for itself about how to formulate plans.
* __Action Effects__ - "When a robot moves, its location changes" `effect(pl, R, move(L), in(R), L) :- action(pl, _, R, move(L)), fluent(pl, _, in(R), L), instance_of(pl, robot, R), instance_of(pl, location, L).`
* __Action Preconditions__ - "A robot can only grasp objects that share its location" `precond()`
* __State Variable Relations__ - "Grasped objects continue to share a robot's location as it moves" `holds(sl, in(O), L, t) :- holds(sl, in(R), L, t), holds(sl, grasping(R), O, t)`

In order to enable HCR planning, an abstraction hierarchy must be constructed by defining a series of abstract domain models.
An abstract domain model may; remove, generalise, or redefine system laws, in order to obtain a simplified description of the domain and problem.
There are three such abstract models currently supported by the theory and implementation.
* __Condensed Models__ - The state space is reduced, by automatically combining sets of detailed entities into abstract descriptors, this reduces the number of actions and state variables needed to represent the problem, and generalises planning constraints. Abstraction mappings are generated automatically.
* __Relaxed Models__ - A sub-set of action preconditions are removed, this removes significant constraints on planning. Abstraction mappings are generated automatically.
* __Tasking Models__ - The system laws are redefined to create a system representation that deals with abstract task descriptions, the resulting plan is a sequence of tasks to be completed in order. Abstraction mappings must be given manually by the designer, and tell the planner how it can complete tasks by reaching states of the original model.

# Planner Configurations for Initial Experiments

This directory contains planner configuration files for the initial experiments for evaluating the performance of the basic methods for conformance refinement planning.
The test problem structures, planner configurations, and global results are overviewed below, for more details see Sections  (on Pages ) of the thesis respectively.

## Problems Overview

Ground-level optimum plan lengths are given in the table below.
The classical optimum is the minimal possible length sequence of actions in a classical plan, that is one that transitions the state from in initial state to end in a goal-satisfying state (under no additional constraints).
The true refinement optimum is the minimal length sequence of actions in a conformance refinement plan, that is one that transitions the state from in initial state, through a sequence of sub-goal stage satisfying states, and ending in a goal-satisfying state.

A possibly concatenated complete conformance refinement plan is globally optimal for a given hierarchical conformance refinement planning diagram at some non-top-abstraction-level, if it is in the set of minimal possible length conformance refinement plans at that level, relative to the entire chosen conformance constraint at the previous level (i.e. the complete sequence of sub-goal stages).
A plan that solves a complete combined conformance refinement problem is guaranteed to be globally optimal, since all sub-goal stages are considered simultaneously (allowed to interleave and non-greedily achieved) and only the final-goal must be minimally achieved.

However, since the quality of conformance refinement plans are subject to the quality of the conformance constraint it maps to and was applied to the problem it solves, even a complete combined plan will be the global optimum in the context of a particular refinement diagram (relative to the plans and decisions made at the higher levels which are fixed and cannot be changed), but will not be the true optimum relative to all possible refinement diagrams.

The true optimum of a given hierarchical conformance refinement planning problem at some non-top-abstraction-level, is the minimum possible (possibly concatenated) conformance refinement plan length, over all possible refinement diagrams.
In other words, it is the minimum of the global minimums over all possibly conformance constraints that could be obtained from the previous level.



Planning Problem  | Classical Optimum Plan Length | True Conformance Refinement Optimum Plan Length
----------------- | ----------------------------- | -----------------------------------------------
Small problem 1   | 39                            | 39
Small problem 1.5 | 39                            | 
Small problem 2   | 54                            | 54
Small problem 3   | 67                            | 69
Large problem 1   | 85                            | 
Large problem 2   | 129 (estimated)               | 
Large problem 3   | 147 (estimated)               | 



## Planner Configurations Overview

- Classical Planning:
- Offline Conformance Refinement Planning:
    - Sub-goal achievement types:
        - Sequential:
        - Simultaneous:
    - Incremental Search Modes:
        - Standard:
        - Minimum Search Length Bound:
        - Sequential Yield:
- Online Conformance Refinement Planning:
    - Bound Configurations:

## Results and Evaluation Overview



Planning Mode | Planning Problem | Plan Length | Quality Score | Execution Latency | Ground-Level Completion Time | Time Score | Overall Grade
------------- | ---------------- | ----------- | ------------- | ----------------- | ---------------------------- | ---------- | -------------
Classical     | Problem 1        | | | | | | 
Offline       | Problem 1        | | | | | | 
Online        | Problem 1        | | | | | | 



Three general reasoning problems were identified:
- The Ignorance Problem:
- The Dependency Problem:
- The Unconsidered Final-Goal Problem:
For more detail and examples see Chapter 3 Section  Page  of the thesis.
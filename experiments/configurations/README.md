# Experimental Configurations

This folder contains configuration files for ASH corresponding to each Blocks World Plus (BWP) experimental problem included in the thesis.

## Directory Structure

The structure is as follows (see inner readmes for detailed break-down of configurations).

- **initial** contains configurations for all experiments used in chapter 3 of the thesis.
- **main** contains configurations for all experiments used in chapter 5 of the thesis.
- **test** contains some basic testing configurations and configurations for running the impetuous and adaptive reactive division strategies, and the multiple-puzzle version of the BWP, which weren't experimentally tested in the thesis due to time and space constraints.

## Naming Conventions

File names define the planning configuration settings, these are of the form:

    <problem>_<planning type>_<planning mode>_<strategy>_<bound type>_<online bounds>_<search mode>_<achievement type>_<action planning>_<preach type>_<blend direction>_<blend type>_<blend quantity>_<online method>

Where the headers are:
- **problem:**          The problem instance; e.g. PS1, PL2, etc.
- **planning type:**    The planning type; mcl, hcl, hcr.
- **planning mode:**    The planning mode; classical, offline, online.
- **strategy:**         The division strategy; e.g. basic, hasty, steady, etc.
- **bound type:**       The bound type; abs, per, sl, cumt.
- **online bounds:**    The online bounds; a vector of numbers.
- **search mode:**      The search mode; standard, min_bound, yield.
- **achievement type:** The sub-goal achievement type; sima, seqa.
- **action planning:**  The action planning type; simultaneous, sequential.
- **preach type:**      The final-goal pre-emptive achievement type; heur, opt.
- **blend direction:**  The blend direction; left, right.
- **blend type:**       The blend type; abs, per.
- **blend quantity:**   The blend quantity; a number.
- **online method:**    The online method; ground-first, complete-first, hybrid.

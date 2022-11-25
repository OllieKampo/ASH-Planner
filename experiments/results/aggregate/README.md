# Aggregate Results



## Aggregate Results Format



## Generating Aggregate Result Sets



### Initial Experiments



#### Affect of Achievement Type



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\achievement_type\ach_type_problem -combine all -diff achievement_type -same problem -filter planning_mode=offline -breakf achievement_type -breaks problem -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\achievement_type\ach_type_seach_mode -combine all -diff achievement_type -same search_mode -filter planning_mode=offline -breakf achievement_type -breaks search_mode -p False -show False
```

#### Affect of Interleaving



#### Performance on Large Problems



#### Affect of Online Bounds



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\online_bounds\bounds -combine all -diff online_bounds -same problem -filter planning_mode=online search_mode=minbound -breakf online_bounds -breaks problem -p False -show False
```

#### Studying Plan and Problem Balancing and Expansions



#### Affect of Planning Modes



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\planning_modes\modes -combine all -diff planning_mode -same problem -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)" -allow_none all -breakf planning_mode -breaks problem -percent_classical True -p False -show False
```

#### Search Modes



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\search_modes\search -combine all -diff search_mode -same problem -filter planning_mode=offline achievement_type=seqa -breakf search_mode -breaks problem -p False -show False
```

#### Unconsidered Final-Goal Problem



### Main Experiments



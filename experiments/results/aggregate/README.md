# Aggregate Results



## Aggregate Results Format



## Generating Aggregate Result Sets



### Initial Experiments



#### Affect of Planning Modes



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\planning_modes\all\all_modes -combine all -diff planning_mode -same problem -allow_none all -breakf planning_mode -breaks problem -percent_classical True -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\planning_modes\focused\modes -combine all -diff planning_mode -same problem -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)" -allow_none all -breakf planning_mode -breaks problem -percent_classical True -p False -show False
```

#### Affect of Achievement Type and Search Mode



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\ach_type_search_mode\ach\ach -combine all -diff achievement_type -same problem -filter planning_mode=offline -breakf achievement_type -breaks problem -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\ach_type_search_mode\search\search -combine all -diff search_mode -same problem -filter planning_mode=offline -breakf search_mode -breaks problem -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\ach_type_search_mode\both\both -combine all -diff achievement_type -same search_mode -filter planning_mode=offline -breakf achievement_type -breaks search_mode -p False -show False
```

#### Affect of Online Bounds and Unconsidered Final-Goal Problem



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\online_bounds\bounds -combine all -diff online_bounds -same problem -filter planning_mode=online search_mode=minbound -breakf online_bounds -breaks problem -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\additional .\results\initial\offline\additional .\results\initial\online\additional -out .\results\aggregate\initial\online_bounds\ufg\bounds_ufg -combine all -diff planning_mode -same problem -filter problem=PS15 search_mode=minbound -breakf planning_mode -breaks problem -plots grades quality time -p False -show False
```

#### Studying Plan and Problem Balancing, Expansions, and Interleaving



```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\balance_expansion_interleaving\modes\bal_modes -combine all -filter planning_mode=offline,online search_mode=yield achievement_type=seqa online_bounds="(2~ 2)" -breakf planning_mode -breaks problem -plot balance -p False -show False
```

```
python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\balance_expansion_interleaving\bounds\bal_bounds -combine all -filter planning_mode=online search_mode=yield achievement_type=seqa -breakf online_bounds -breaks problem -plot balance -p False -show False
```

#### Performance on Large Problems



### Main Experiments



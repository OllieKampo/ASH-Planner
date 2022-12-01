REM Affect of Planning Modes



REM Affect of Achievement Type and Search Mode

python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\ -out .\results\aggregate\initial\ach_type_search_mode\both\both -combine all -diff achievement_type -same search_mode -filter planning_mode=offline -breakf achievement_type -breaks search_mode -p False -show False

REM Affect of Online Bounds and Unconsidered Final-Goal Problem



REM Studying Plan and Problem Balancing, Expansions, and Interleaving

python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\yield -out .\results\aggregate\initial\balance_expansion_interleaving\modes\bal_modes -combine all -filter planning_mode=offline,online search_mode=yield achievement_type=seqa online_bounds="(2~ 2)" -breakf planning_mode -breaks problem -plots balance -p False -show False

python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ .\results\initial\online\yield -out .\results\aggregate\initial\balance_expansion_interleaving\bounds\bal_bounds -combine all -filter planning_mode=online search_mode=yield achievement_type=seqa -breakf online_bounds -breaks problem -plots balance -p False -show False

REM Performance on Large Problems



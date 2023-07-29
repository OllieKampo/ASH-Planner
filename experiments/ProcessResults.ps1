param([Parameter(Mandatory=$True, Position=0, HelpMessage="Results to process; modes, ach_search, online, blend, large, pro, react")] [string[]] $process)

Write-Output "Processing results..."
Start-Sleep -Seconds 2

function make_directories {
    param([string]$parent, [string[]]$children)

    $path = ".\results\aggregate\$($parent)"
    if (!(test-path $path)) {
        mkdir $path
    } else {
        Get-ChildItem -Path $path -Include *.* -File -Recurse | ForEach-Object { $_.Delete() }
    }
    
    foreach ($child in $children) {
        $path = ".\results\aggregate\$($parent)\$($child)"
        if (!(test-path $path)) {
            mkdir $path
        } else {
            Get-ChildItem -Path $path -Include *.* -File -Recurse | ForEach-Object { $_.Delete() }
        }
    }
}

if ($process -contains "modes") {
    Write-Output "Processing: Affect of Planning Modes for Small Problems and Different Action Planning..."
    Start-Sleep -Seconds 1
    make_directories -parent planning_modes -children all_sequ, all_sequ_bal, all_conc, all_conc_bal

    # Sequential Action Planning
    python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\planning_modes\all_sequ\all_sequ -combine all -diff planning_mode -same problem -filter search_mode=minbound achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -percent_classical True -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\planning_modes\all_sequ_bal\all_sequ_bal -combine all -diff planning_mode -same problem -filter search_mode=yield achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots balance -p False -show False

    # Concurrent Action Planning
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\classical\ .\results\main\improved_initial\action_concurrency\offline\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\planning_modes\all_conc\all_conc -combine all -diff planning_mode -same problem -filter search_mode=minbound achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -percent_classical True -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\offline\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\planning_modes\all_conc_bal\all_conc_bal -combine all -diff planning_mode -same problem -filter search_mode=yield achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots balance -p False -show False
}

if ($process -contains "ach_search") {
    Write-Output "Processing: Affect of Achievement Type and Search Mode..."
    Start-Sleep -Seconds 1
    make_directories -parent ach_type_search_mode -children ach, search, both

    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\ach\ach -combine all -diff achievement_type -same search_mode problem -filter planning_mode=offline -breakf achievement_type -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\search\search -combine all -diff search_mode -same achievement_type problem -filter planning_mode=offline -breakf search_mode -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\both\both -combine all -diff problem -same search_mode achievement_type -filter planning_mode=offline -breakf achievement_type -breaks search_mode -plots grades quality time -p False -show False
}

if ($process -contains "online") {
    Write-Output "Processing: Basic Strategy - Affect of Online Bounds, Saved Groundings, Final-Goal Pre-emptive Achievement, and Unconsidered Final-Goal Problem..."
    Start-Sleep -Seconds 1
    make_directories -parent online_bounds -children bounds_std, bounds_preach, bounds_preach_bal, preach_best_bounds, preach_all_bounds, savedg, ufg

    # Bounds with and without Pre-emptive Achievement
    python .\ProcessResults.py .\results\initial\online\ -out .\results\aggregate\online_bounds\bounds_std\bounds_std -combine all -diff online_bounds -same problem -filter search_mode=minbound -breakf online_bounds -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online_bounds\bounds_preach\bounds_preach -combine all -diff online_bounds -same problem -filter search_mode=minbound -breakf online_bounds -breaks problem -plots grades quality time -p False -show False

    # Bounds Balance
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online_bounds\bounds_preach_bal\bounds_preach_bal -combine all -diff online_bounds -same problem -filter search_mode=yield -breakf online_bounds -breaks problem -plots balance -p False -show False

    # Final-Goal Pre-emptive Achievement Comparison
    python .\ProcessResults.py .\results\initial\online\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online_bounds\preach_best_bounds\preach_best_bounds -combine all -diff preach_type -same problem -filter search_mode=minbound online_bounds="(2~ 2)" -allow_none all -breakf preach_type -breaks problem -plots grades quality time -excel False -p False -show False
    python .\ProcessResults.py .\results\initial\online\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online_bounds\preach_all_bounds\preach_all_bounds -combine all -diff preach_type -same problem -filter search_mode=minbound -allow_none all -breakf preach_type -breaks online_bounds -plots grades quality time -excel False -p False -show False

    # Saved Groundings
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\saved_groundings\ -out .\results\aggregate\online_bounds\savedg\savedg -combine all -diff online_bounds -same problem -filter search_mode=minbound -breakf online_bounds -breaks problem -plots grades quality time -p False -show False

    # Unconsidered Final-Goal Problem
    python .\ProcessResults.py .\results\initial\classical\additional\ .\results\initial\offline\additional\ .\results\main\improved_initial\preemptive_achievement\additional\ -out .\results\aggregate\online_bounds\ufg\bounds_ufg -combine all -diff planning_mode -same problem -filter problem=ps15 search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)" -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -p False -show False
}

if ($process -contains "blend") {
    Write-Output "Processing: Affect of Partial-Problem Blending with Final-Goal Pre-emptive Achievement..."
    Start-Sleep -Seconds 1
    make_directories -parent problem_blending -children blend_sequ, blend_conc

    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\problem_blending\sequ_action_planning\ -out .\results\aggregate\blending\blend_sequ\blend_sequ -combine all -diff blend_quantity -same problem online_bounds -filter search_mode=minbound achievement_type=seqa blend_type=abs -allow_none all -breakf blend_quantity -breaks online_bounds -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\online\ .\results\main\improved_initial\problem_blending\conc_action_planning\ -out .\results\aggregate\blending\blend_conc\blend_conc -combine all -diff blend_quantity -same problem online_bounds -filter search_mode=minbound achievement_type=seqa blend_type=abs -allow_none all -breakf blend_quantity -breaks online_bounds -plots grades quality time -p False -show False
}

if ($process -contains "large") {
    Write-Output "Processing: Performance on Large Problems for Standard and Modified Hierarchies..."
    Start-Sleep -Seconds 1
    make_directories -parent large_problems -children lpsh_sequ, lpsh_conc, lpmh_sequ, lpmh_conc

    # Standard Hierarchies
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\additional\ -out .\results\aggregate\large_problems\lpsh_sequ\lpsh_sequ -combine all -diff online_bounds -same problem -filter problem=pl1,pl2 search_mode=minbound achievement_type=seqa -allow_none all -breakf online_bounds -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\online\additional\ -out .\results\aggregate\large_problems\lpsh_conc\lpsh_conc -combine all -diff online_bounds -same problem -filter problem=pl1,pl2 search_mode=minbound achievement_type=seqa -allow_none all -breakf online_bounds -breaks problem -plots grades quality time -p False -show False

    # Modified Hierarchies
    python .\ProcessResults.py .\results\main\modified_hierarchies\online\sequ_action_planning\ -out .\results\aggregate\large_problems\lpmh_sequ\lpmh_sequ -combine all -diff online_bounds -same problem -filter problem=pl1ts,pl2dc search_mode=minbound achievement_type=seqa -allow_none all -breakf online_bounds -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\main\modified_hierarchies\online\conc_action_planning\ -out .\results\aggregate\large_problems\lpmh_conc\lpmh_conc -combine all -diff online_bounds -same problem -filter problem=pl1ts,pl2dc search_mode=minbound achievement_type=seqa -allow_none all -breakf online_bounds -breaks problem -plots grades quality time -p False -show False
}

# TODO: Remove online methods from the following.
if ($process -contains "pro") {
    Write-Output "Processing: Proactive Sized-Bound Strategies with Final-Goal Pre-emptive Achievement for all Small Problems and Different Online Bounds and Online Methods..."
    Start-Sleep -Seconds 1
    make_directories -parent proactive_strategies -children strategies, problems, bounds_cf, bounds_gf, bounds_hy

    # Difference between Strategies and Online Methods averaged over bounds and problems
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\strategies\pro_strategies -combine all -diff strategy -same problem,online_bounds,online_method -filter problem=ps3,ps3ts strategy=hasty,steady -allow_none all -breakf strategy -breaks online_method -excel False -p False -show False

    # Difference between Problems (PS3 and PS3TS) and Online Methods averaged over bounds and strategies
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\problems\pro_problems -combine all -diff problem -same strategy,online_bounds,online_method -filter problem=ps3,ps3ts strategy=hasty,steady -allow_none all -breakf problem -breaks online_method -excel False -p False -show False

    # Difference between Bound Values for PS3 for each online method
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_cf\pro_bounds_cf -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=cf strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_gf\pro_bounds_gf -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=gf strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_hy\pro_bounds_hy -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=hy strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
}

if ($process -contains "react") {
    Write-Output "Processing: Interrupting Reactive Strategies with Final-Goal Pre-emptive Achievement for Small Problems and Different Bound Type and Pre-Emptive Division Enabled/Disabled..."
    Start-Sleep -Seconds 1
    make_directories -parent reactive_strategies -children problems, bounds_sl, bounds_st

    # Difference between Problems (PS3 and PS3TS) averaged over bounds
    python .\ProcessResults.py .\results\main\reactive_strategies\interrupting\length\ .\results\main\reactive_strategies\interrupting\time\ -out .\results\aggregate\reactive_strategies\problems\react_problems -combine all -diff problem -same online_bounds,bound_type -filter problem=ps3,ps3ts strategy=relentless -allow_none all -breakf problem -breaks bound_type -excel False -p False -show False

    # Difference between Bound Values for PS3 for each bound type
    python .\ProcessResults.py .\results\main\reactive_strategies\interrupting\length\ .\results\main\reactive_strategies\interrupting\time\ -out .\results\aggregate\reactive_strategies\bounds_sl\react_bounds_sl -combine all -diff online_bounds -filter problem=ps3 bound_type=sl strategy=relentless -allow_none all -breakf online_bounds -breaks problem -excel False -p False -show False
    python .\ProcessResults.py .\results\main\reactive_strategies\interrupting\length\ .\results\main\reactive_strategies\interrupting\time\ -out .\results\aggregate\reactive_strategies\bounds_st\react_bounds_st -combine all -diff online_bounds -filter problem=ps3 bound_type=cumt strategy=relentless -allow_none all -breakf online_bounds -breaks problem -excel False -p False -show False
}

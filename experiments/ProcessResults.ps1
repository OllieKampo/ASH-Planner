param([Parameter(Mandatory=$True, Position=0, HelpMessage="Results to process; paper, modes, ach_search, online, blend, large, pro, react")] [string[]] $process)

Write-Output "Processing results..."
Start-Sleep -Seconds 2

function make_directories {
    param([string]$parent, [string[]]$children)

    $path = ".\results\aggregate\$($parent)"
    if (!(test-path $path)) {
        mkdir $path
    }
    
    $path = ".\results\aggregate\$($parent)\_final_"
    if (!(test-path $path)) {
        mkdir $path
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

# if ($process -contains "paper") {
#     Start-Sleep -Seconds 1
#     make_directories -parent paper -children paper
    
#     python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\paper\paper\paper -combine all -diff planning_mode -same problem -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)" -allow_none all -breakf planning_mode -breaks problem -plots grades quality time balance -percent_classical True -p False -show False
# }

if ($process -contains "modes") {
    Write-Output "Processing: Affect of Planning Modes for Small Problems and Different Action Planning..."
    Start-Sleep -Seconds 1
    make_directories -parent planning_modes -children all_sequ, all_sequ_bal, all_conc, all_conc_bal, online_combined_bal

    # Sequential Action Planning
    python .\ProcessResults.py .\results\initial\classical\ .\results\initial\offline\sequential_achievement\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\planning_modes\all_sequ\all_sequ -combine all -diff planning_mode online_bounds -same problem -filter search_mode=minbound achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -percent_classical True -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\planning_modes\all_sequ_bal\all_sequ_bal -combine all -diff planning_mode -same problem -filter search_mode=yield achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots balance -p False -show False

    # Concurrent Action Planning
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\classical\ .\results\main\improved_initial\action_concurrency\offline\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\planning_modes\all_conc\all_conc -combine all -diff planning_mode online_bounds -same problem -filter search_mode=minbound achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -actions True -percent_classical True -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\offline\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\planning_modes\all_conc_bal\all_conc_bal -combine all -diff planning_mode -same problem -filter search_mode=yield achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots balance -actions True -p False -show False

    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\planning_modes\online_combined_bal\online_combined_bal -combine all -diff action_planning -same problem -filter search_mode=minbound achievement_type=seqa planning_mode=online -allow_none all -breakf action_planning -breaks problem -plots balance -actions True -p False -show False
}

if ($process -contains "ach_search") {
    Write-Output "Processing: Affect of Achievement Type and Search Mode..."
    Start-Sleep -Seconds 1
    make_directories -parent ach_type_search_mode -children ach, search, search_ps3, both

    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\ach\ach -combine all -diff achievement_type -same search_mode problem -filter planning_mode=offline -breakf achievement_type -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\search\search -combine all -diff search_mode -same achievement_type problem -filter planning_mode=offline -breakf search_mode -breaks problem -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\both\both -combine all -diff problem -same search_mode achievement_type -filter planning_mode=offline -breakf achievement_type -breaks search_mode -plots grades quality time -p False -show False
    python .\ProcessResults.py .\results\initial\offline\sequential_achievement\ .\results\initial\offline\simultaneous_achievement\ -out .\results\aggregate\ach_type_search_mode\search_ps3\search_ps3 -combine all -diff search_mode -same achievement_type problem -filter problem=ps3 planning_mode=offline -breakf search_mode -breaks problem -plots time -tables False -excel False -p False -show False
}

if ($process -contains "online") {
    Write-Output "Processing: Basic Strategy - Affect of Online Bounds, Final-Goal Pre-emptive Achievement, Saved Groundings, Action Concurrency, and Unconsidered Final-Goal Problem..."
    Start-Sleep -Seconds 1
    make_directories -parent online -children bounds_std, bounds_preach, bounds_std_bal, bounds_std_bal_problems, bounds_preach_bal, bounds_preach_bal_problems, preach_problems, preach_bounds_ps3, ufg, savedg_problems, savedg_bounds_ps3, conc_problems, conc_bounds_ps3

    # Bounds with and without Pre-emptive Achievement
    python .\ProcessResults.py .\results\initial\online\ -out .\results\aggregate\online\bounds_std\bounds_std -combine all -diff online_bounds -same problem -filter search_mode=minbound -breakf online_bounds -breaks problem -plots grades quality time balance -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online\bounds_preach\bounds_preach -combine all -diff online_bounds -same problem -filter search_mode=minbound -breakf online_bounds -breaks problem -plots grades quality time balance -p False -show False

    # Bounds Balance
    python .\ProcessResults.py .\results\initial\online\yield\ -out .\results\aggregate\online\bounds_std_bal\bounds_std_bal -combine all -diff online_bounds -same problem -filter search_mode=yield -breakf online_bounds -breaks problem -plots balance -p False -show False
    python .\ProcessResults.py .\results\initial\online\yield\ -out .\results\aggregate\online\bounds_std_bal_problems\bounds_std_bal_problems -combine all -diff problem -same online_bounds -filter search_mode=yield -breakf problem -breaks online_bounds -plots balance -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online\bounds_preach_bal\bounds_preach_bal -combine all -diff online_bounds -same problem -filter search_mode=yield -breakf online_bounds -breaks problem -plots balance -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online\bounds_preach_bal_problems\bounds_preach_bal_problems -combine all -diff problem -same online_bounds -filter search_mode=yield -breakf problem -breaks online_bounds -plots balance -p False -show False

    # Final-Goal Pre-emptive Achievement Comparison
    python .\ProcessResults.py .\results\initial\online\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online\preach_problems\preach_problems -combine all -diff preach_type -same problem -filter search_mode=minbound -allow_none all -breakf preach_type -breaks problem -plots grades quality time -excel False -p False -show False
    python .\ProcessResults.py .\results\initial\online\ .\results\main\improved_initial\preemptive_achievement\optimise\ -out .\results\aggregate\online\preach_bounds_ps3\preach_bounds_ps3 -combine all -diff preach_type -same online_bounds -filter problem=ps3 search_mode=minbound -allow_none all -breakf preach_type -breaks online_bounds -plots grades quality time -excel False -p False -show False

    # Unconsidered Final-Goal Problem
    python .\ProcessResults.py .\results\initial\classical\ .\results\initial\classical\additional\ .\results\initial\offline\sequential_achievement\ .\results\initial\offline\additional\ .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\preemptive_achievement\additional\ -out .\results\aggregate\online\ufg\bounds_ufg -combine all -diff planning_mode -same problem -filter problem=ps1,ps15 search_mode=minbound achievement_type=seqa -allow_none all -breakf planning_mode -breaks problem -plots grades quality time -p False -show False

    # Saved Groundings
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\preemptive_achievement\saved_groundings\ -out .\results\aggregate\online\savedg_problems\savedg_problems -combine all -diff grounding -same problem -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" -breakf grounding -breaks problem -plots grades time -tables False -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\preemptive_achievement\saved_groundings\ -out .\results\aggregate\online\savedg_bounds_ps3\savedg_bounds_ps3 -combine all -diff grounding -same online_bounds -filter problem=ps3 search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" -breakf grounding -breaks online_bounds -plots grades time -tables False -p False -show False
    
    # Action Concurrency
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\online\conc_problems\conc_problems -combine all -diff action_planning -same problem -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" -breakf action_planning -breaks problem -plots grades quality time balance -tables False -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\action_concurrency\online\ -out .\results\aggregate\online\conc_bounds_ps3\conc_bounds_ps3 -combine all -diff action_planning -same online_bounds -filter problem=ps3 search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" -breakf action_planning -breaks online_bounds -plots grades quality time -tables False -p False -show False
}

if ($process -contains "blend") {
    Write-Output "Processing: Affect of Partial-Problem Blending with Final-Goal Pre-emptive Achievement..."
    Start-Sleep -Seconds 1
    make_directories -parent problem_blending -children blend_sequ, blend_conc, blend_problems
    
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\problem_blending\sequ_action_planning\ -out .\results\aggregate\problem_blending\blend_sequ\blend_sequ -combine all -diff blend_quantity -same problem online_bounds -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" blend_type=abs -allow_none all -breakf blend_quantity -breaks online_bounds -plots grades quality time -excel False -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\action_concurrency\online\ .\results\main\improved_initial\problem_blending\conc_action_planning\ -out .\results\aggregate\problem_blending\blend_conc\blend_conc -combine all -diff blend_quantity -same problem online_bounds -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" blend_type=abs -allow_none all -breakf blend_quantity -breaks online_bounds -plots grades quality time -excel False -p False -show False
    python .\ProcessResults.py .\results\main\improved_initial\preemptive_achievement\optimise\ .\results\main\improved_initial\problem_blending\sequ_action_planning\ .\results\main\improved_initial\action_concurrency\online\ .\results\main\improved_initial\problem_blending\conc_action_planning\ -out .\results\aggregate\problem_blending\blend_problems\blend_problems -combine all -diff blend_quantity action_planning -same problem online_bounds -filter search_mode=minbound achievement_type=seqa online_bounds="(2~ 2)","(2~ 4)","(4~ 2)","(4~ 4)" blend_type=abs -allow_none all -breakf blend_quantity -breaks problem -plots grades quality time -excel False -p False -show False
}

if ($process -contains "pro") {
    Write-Output "Processing: Proactive Sized-Bound Strategies with Final-Goal Pre-emptive Achievement for all Small Problems and Different Online Bounds and Online Methods..."
    Start-Sleep -Seconds 1
    make_directories -parent proactive_strategies -children strategies, methods_bal, bounds_cf, bounds_gf, bounds_hy

    # Difference between Strategies and Online Methods for PS3 averaged over bounds
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\strategies\pro_strategies -combine all -diff strategy -same online_bounds,online_method -filter problem=ps3 strategy=hasty,steady -allow_none all -breakf strategy -breaks online_method -excel False -p False -show False
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\methods_bal\pro_methods_bal -combine all -diff online_method -same strategy,online_bounds -filter problem=ps3 strategy=hasty,steady -allow_none all -breakf online_method -breaks strategy -plots balance -excel False -p False -show False

    # Difference between Bound Values for PS3 for each online method
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_cf\pro_bounds_cf -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=cf strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_gf\pro_bounds_gf -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=gf strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
    python .\ProcessResults.py .\results\main\proactive_strategies\complete_first\hasty\ .\results\main\proactive_strategies\complete_first\steady\ .\results\main\proactive_strategies\ground_first\hasty\ .\results\main\proactive_strategies\ground_first\steady\ .\results\main\proactive_strategies\hybrid\hasty\ .\results\main\proactive_strategies\hybrid\steady\ -out .\results\aggregate\proactive_strategies\bounds_hy\pro_bounds_hy -combine all -diff strategy -same online_bounds -filter problem=ps3 online_method=hy strategy=hasty,steady -allow_none all -breakf online_bounds -breaks strategy -excel False -p False -show False
}

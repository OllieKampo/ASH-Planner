import ASP_Parser as ASP
import logging

logging.getLogger("").setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(levelname)-4s :: %(name)-12s >> %(message)s\n"))
logging.getLogger("").addHandler(console_handler)

program = ASP.LogicProgram("""
                           #program step(t).
                           #external query(t).
                           #program check(t).
                           test(T) :- T = t, query(t).
                           :- query(t), t < 10.
                           """, silent=False)

answer: ASP.Answer = program.solve(solve_incrementor=ASP.SolveIncrementor(), count_multiple_models=True)
print(answer.inc_models)
input(answer)

solve_incrementor = ASP.SolveIncrementor(step_end_max=11, stop_condition=ASP.SolveResult.Satisfiable)
solve_signal: ASP.SolveSignal
with program.start() as solve_signal:
    step: int; increment: int; feedback: ASP.Feedback
    for i in range(3):
        for feedback in solve_signal.yield_run(increments=5):
            print(f"Increment = {feedback.increment} :: Result = {feedback.solve_result.name}")
        print(f"Incrementing halted :: Reason = {solve_signal.halt_reason}")
    solve_signal.holding = True

input()

solve_incrementor = ASP.SolveIncrementor(step_end_max=20, stop_condition=None)
with program.resume(solve_incrementor=solve_incrementor) as solve_signal:
    step: int; increment: int; feedback: ASP.Feedback
    for i in range(3):
        solve_signal.run_for(increments=5)
    solve_signal.holding = True

input()

solve_incrementor = ASP.SolveIncrementor(step_end_max=None, stop_condition=None)
with program.resume(solve_incrementor=solve_incrementor) as solve_signal:
    step: int; increment: int; feedback: ASP.Feedback
    for i in range(3):
        solve_signal.run_while(lambda feedback: feedback.cumulative_statistics.total_time < 30.0)
    solve_signal.holding = False

#%%
import math
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True, order=True)
class DivisionPoint:
    index: int
    left_blend: int
    right_blend: int
    
    @property
    def sgoals_range(self) -> range:
        return range(self.index - self.left_blend, self.index + self.right_blend)

plan_length = 10
size_bound = 2
if isinstance(size_bound, float):
    _size_bound = round(plan_length * size_bound)
else: _size_bound = size_bound
print(_size_bound)
blend_quantity = 3

n_total_groups: int = math.floor(plan_length/_size_bound)
n_small_groups: int = n_total_groups - (plan_length % n_total_groups)
n_large_groups: int = n_total_groups - n_small_groups
small_size: int = plan_length//n_total_groups
large_size: int = small_size + 1

print(n_small_groups)
print(n_large_groups)

def make_groups(number_small_groups: int, number_large_groups: int,
                small_group_size: int, large_group_size: int) -> list[DivisionPoint]:
    division_points: list[DivisionPoint] = []
    def get_size(division_number: int) -> int:
        if division_number <= number_small_groups:
            size: int = small_group_size
        else: size: int = large_group_size
        return size
    current_index: int = 0
    for division_number in range(1, number_small_groups + number_large_groups):
        size = get_size(division_number)
        prev_index = current_index
        current_index += size
        next_index = current_index + get_size(division_number + 1)
        left_blend = max(current_index - blend_quantity, prev_index)
        right_blend = min(current_index + blend_quantity, next_index)
        division_points.append(DivisionPoint(current_index, left_blend, right_blend))
    return division_points

print(*make_groups(n_small_groups, n_large_groups, small_size, large_size), sep="\n")

#%%

#%%

import ASP_Parser

logic_program = ASP_Parser.LogicProgram("#heuristic a : b. [1, true] {a;c}. b.")
answer = logic_program.solve(solver_options=["-n", "0", "--heuristic=Domain", "--stats"])
print(answer)

#%%

#%%

import ASP_Parser as ASP
import clingo
import re
program = ASP.LogicProgram("""
                           #program step(t).
                           :- query(t), t < 10.
                           #program check(t).
                           #external query(t).
                           """)

answer: ASP.Answer = program.solve(solve_incrementor=ASP.SolveIncrementor())
answer

#%%

#%%

import ASP_Parser as ASP
import clingo
import re
program = ASP.LogicProgram("""
                           occurs(move(robot, library), 0).
                           occurs(grasp(robot, book), 1).
                           -occurs(grasp(robot, book), 0).
                           -occurs(move(robot, library), 1).
                           holds(in(robot, office), 0).
                           holds(grasping(robot, book), 2).
                           holds(in(robot, library), 1).
                           """)

answer: ASP.Answer = program.solve()
print(answer)

#%%

# Extract positive atoms with name 'occurs' and arity 2. Note that the output's order is arbitrary and not necessarily the same order the atoms occur in the program.
print(*answer.fmodel.get_atoms("occurs", 2, True), sep="\n")
# [occurs(grasp(robot,book),1), occurs(move(robot,library),0)]



#%%

class Action(ASP.Atom):
    """
    Represents an action literal.
    Whose encoding as an ASP symbol (an atom) of the form:
            occurs(action, step)
    
    Fields
    ------
    `A : str` - A non-empty string defining the action itself, usually a function symbol of the form `name(arg_1, arg_2, ... arg_n)`.
    
    `S : int` - An integer, greater than zero, defining the discrete time step the action is planned to occur at.
    """
    
    @classmethod
    def default_params(cls) -> tuple[str]:
        return ('A', 'S')
    
    @classmethod
    def predicate_name(cls) -> str:
        return "occurs"

print(*answer.fmodel.query(Action, truth=None, group_by=["S"], sort_by=["S", "A"], add_truth=bool, cast_to={"A" : str, "S" : [str, int]}).items(), sep="\n")

#%%



#%%
# Extract positive atoms with name 'holds' and arity 2, sort by the second argument.
# answer.fmodel.get_atoms("holds", 2, True, sort_by=1, group_by=1)

answer.fmodel.query("holds", ["F", "V"], True, select=["F", "V"], sort_by=["V", "F"], group_by=["V", "F"], convert_to=str)
# [holds(in(robot,office),0), holds(in(robot,library),1), holds(grasping(robot,book),2)]
#%%

# Extract negative atoms with name 'occurs', arity 2 and whose second argument is 1.
answer.fmodel.get_atoms("occurs", 2, False, param_constrs={1 : [0, 1]}, group_by=1, convert_keys=lambda item: int(str(item)), as_strings=True)
# [-occurs(move(robot,library),1)]

#%%
# Extract atoms regards of truth value with name 'occurs', arity 2 and whose first argument starts with the string 'move'.
answer.fmodel.get_atoms("occurs", 2, None, param_constrs={0 : (re.compile(r"move"), ASP.Model.ParseMode.Match)})
# [-occurs(move(robot,library),1), occurs(move(robot,library),0)]
#%%
# Extract positive atoms whose name contains the letter 's' and which have arity 2, sort first by the first argument and then by the second, return the atoms as strings.
answer.fmodel.get_atoms((re.compile(r"s"), ASP.Model.ParseMode.Search), 2, True, as_strings=True, sort_by=[1, 0])
# ['holds(in(robot,office),0)', 'occurs(move(robot,library),0)', 'occurs(grasp(robot,book),1)', 'holds(in(robot,library),1)', 'holds(grasping(robot,book),2)']

#%%
import ASP_Parser as ASP
import logging

logging.getLogger("").setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(levelname)-4s :: %(name)-12s >> %(message)s\n"))
logging.getLogger("").addHandler(console_handler)

program = ASP.LogicProgram.from_files("test_problems/blocks_world_plus/blocks_world_plus_tasking_large.lp")
answer: ASP.Answer = program.solve(base_parts=[ASP.BasePart("entities")])

print(*map(str, answer.fmodel.get_atoms("entity", 2, sort_by=[0, 1])), sep="\n")
print(*map(str, answer.fmodel.get_atoms("ancestry_relation", 2, sort_by=[0, 1])), sep="\n")
import clingo
import ASP_Parser as ASP
import random

def make_delivery_domain(domain_name: str, total_nodes: int, delivery_nodes: int, connectedness: int = 2) -> None:
    delivery_nodes_list: list[int] = []
    
    while len(delivery_nodes) < delivery_nodes:
        if (node := random.randint(1, total_nodes)) not in delivery_nodes_list:
            delivery_nodes_list.append(node)
    
    def is_delivery_node(node: clingo.Symbol) -> clingo.Symbol:
        if int(str(node)) in delivery_nodes_list:
            return clingo.Function("true")
        return clingo.Function("false")
    
    # context = type("context", (object,), {is_delivery_node.__name__: is_delivery_node})
    
    logic_program = ASP.LogicProgram("""
                                     #program declare_domain(total_nodes, connectedness).
                                     
                                     %% Declare graph nodes.
                                     node(1..total_nodes).
                                     
                                     %% Choose the delivery nodes randomly.
                                     delivery_node(X) :- node(X), true = @is_delivery_node(X).
                                     
                                     %% Generate arcs to create the graph.
                                     { arc(X, Y) } :- node(X), node(Y), X != Y.
                                     
                                     %% An arc is connected to the graph if there is a number of arcs coming into and out of it equal to the connectedness.
                                     connected(X) :- node(X),
                                                     #count { Y : arc(X, Y), node(Y) } = connectedness,
                                                     #count { Z : arc(Z, X), node(Z) } = connectedness.
                                     :- node(X), not connected(X).
                                     
                                     %% Each node must be connected to the graph such that the graph is fully connected.
                                     connection_to(X, Y) :- node(X), node(Y), arc(X, Y).
                                     connection_to(X, Z) :- node(X), node(Y), arc(X, Y), connection_to(Y, Z).
                                     :- node(X), node(Y), not connection_to(X, Y), X != Y.
                                     """)
    
    ## Make 100 different versions of the domain
    answer: ASP.Answer = logic_program.solve(solver_options=[ASP.Options.models(100)],
                                             context=[is_delivery_node],
                                             base_parts=[ASP.BasePart("declare_domain",
                                                                      (total_nodes, connectedness))])
    
    print("Domain generated:")
    print(answer, end="\n\n")
    
    ## Choose from the 100 randomly
    model = answer.base_models[random.randint(0, len(answer.base_models) - 1)]
    
    print("Delivery nodes:")
    print(*model.get_atoms("delivery_node", 1), sep="\n", end="\n\n")
    
    arcs = model.query("arc", ["from", "to"], sort_by=["from", "to"], group_by="from", cast_to=[str, int])
    print(f"Arcs: [total={len(arcs)}]")
    print(*[f"{from_} => {[to['to'] for to in tos]}" for from_, tos in arcs.items()], sep="\n")
    
    with open(f"./test_problems/delivery/Delivery_{domain_name}_T{total_nodes}_D{delivery_nodes}_C{connectedness}.lp", "w") as file:
        file.write("#program entities.")
        for node in model.get_atoms("node", 1, as_strings=True):
            file.write(f"{node}.")
        for node in model.get_atoms("delivery_node", 1, as_strings=True):
            file.write(f"{node}.")
        for arc in model.get_atoms("arc", 2, as_strings=True):
            file.write(f"{arc}.")
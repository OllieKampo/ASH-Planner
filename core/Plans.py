from abc import abstractclassmethod, abstractmethod
import _collections_abc
from Helpers import AbstractionHierarchy, SequenceDataClass
import clingo
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, NamedTuple, Union, Optional
import ASP_Parser as ASP

class Literal(SequenceDataClass):
    """
    Abstract base class for all state and action literals used in hierarchical conformance refinment planning.
    
    Fields
    ------
    `al : int` - The abstraction level of the literal.
    
    Example Usage
    -------------
    >>> from ASH.core import Plans
    >>> import clingo
    
    >>> fluent_literal = Plans.FluentLiteral(1, 'in(talos)', 'puzzle_room', 1)
    >>> action_literal = Plans.ActionLiteral(1, 'talos', 'move(a)', 1)
    
    >>> fluent_literal
    Plans.FluentLiteral(al=1, fluent='in(talos)', value='puzzle_room', step=1)
    
    >>> print(action_literal)
    'occurs(1, talos, move(a), 1)'
    
    Fields are accessible by name or index;
    >>> fluent_literal.fluent
    'in(talos)'
    >>> fluent_literal[0:4]
    (1, 'in(talos)', 'puzzle_room', 1)
    
    Unpacking of fields is also supported;
    >>> al, fluent, value, step = fluent_literal
    
    To convert a fluent literal to a fluent atom use any of;
    >>> fluent_atom: clingo.Symbol = fluent_literal.symbol
    >>> fluent_atom
    holds(1,in(talos),puzzle_room,1)
    
    To convert an Clingo symbol symbol to an fluent literal;
    >>> fluent_literal = Plans.FluentLiteral.from_symbol(fluent_atom)
    
    
    >>> action_literal
    ASH.ActionLiteral(al=1, robot='talos', action='move(a)', step=1)
    >>> str(action_literal)
    
    
    Fields are accessible by name;
    >>> action_literal.robot
    'talos'
    
    Or by index;
    >>> action_literal[0:4]
    (1, 'talos', 'move(a)', 1)
    
    Unpacking of fields is also supported;
    >>> al, robot, action, step = action_literal
    
    To convert an action literal to an action symbol;
    >>> action_symbol: clingo.Symbol = action_literal.symbol
    >>> action_symbol
    occurs(1,talos,move(a),1)
    
    Which is equivalent to;
    >>> action_symbol: clingo.Symbol = clingo.parse_term(str(action_literal))
    
    To convert an action symbol to an action literal;
    >>> action_literal = ASH.ActionLiteral.from_symbol(*action_symbol.arguments)
    """
    al: int
    
    def __post_init__(self) -> None:
        validity: Optional[str] = self.validate()
        if validity is not None:
            raise ValueError(validity)
    
    def __str__(self) -> str:
        return f"{self.get_predicate_name()}({', '.join([str(field_) for field_ in self])})"
    
    @abstractclassmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> "Literal":
        """
        Instantiate a literal from a Clingo Symbol.
        This abstract class method must be overridden in sub-classes.
        
        Fields
        ------
        `symbol : clingo.Symbol` - The Clingo symbol to convert to a literal object.
        
        Returns
        -------
        `Literal` - A new literal.
        """
        raise NotImplementedError
    
    @abstractclassmethod
    def predicate_name(cls) -> str:
        """
        Get the name of the predicate that encode literals of this type.
        
        Returns
        -------
        `str` - A string defining the predicate name.
        """
        raise NotImplementedError
    
    @property
    def symbol(self) -> clingo.Symbol:
        """
        Get this literal as a Clingo symbol.
        
        Returns
        -------
        `clingo.Symbol` - The Clingo symbol form of the literal.
        """
        return clingo.parse_term(str(self))
    
    @abstractmethod
    def validate(self) -> Optional[str]:
        """
        Check that the literal's field values are valid, and if they are invalid return a string describing why.
        This method is called automatically after a literal is instantiated, if the literal is invalid an exception is raised containing the returned string.
        This method should be overridden by sub-classes that add fields to a literal.
        
        Returns
        -------
        `{str | None}` - Either None if the literal's field values are valid, otherwise a string describing why they are not valid.
        """
        if not isinstance(self.al, int) or self.al < 1:
            return "Abstraction level 'al' must be greater than or equal to 1."
        return None

class FluentLiteral(Literal):
    """
    Represents a fluent literal as a typed four-tuple.
    Fluents are function symbols declaring dynamic state variables.
    Fluent literals are fluent function literals defining the current value of a state variable at a given time step.
    
    Fields
    ------
    `al : int` - An integer, greater than zero, defining the abstraction level of the fluent.
    
    `fluent : str` - A non-empty string defining the fluent symbol itself, usually a function symbol of the form `name(arg_1, arg_2, ... arg_n)`.
    
    `value : str` - A non-empty string defining the value assigned to the fluent.
    
    `step : int` - An integer, greater than or equal to zero, defining the discrete time step the fluent holds the given value at.
    """
    fluent: str
    value: str
    step: int
    
    @classmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> "FluentLiteral":
        return cls(al=int(symbol.arguments[0].number), fluent=str(symbol.arguments[1]),
                   value=str(symbol.arguments[2]), step=int(symbol.arguments[3].number))

    @classmethod
    def predicate_name(cls) -> str:
        return "holds"
    
    def validate(self) -> Optional[str]:
        super_: Optional[str] = super().validate()
        if super_ is not None:
            return super_
        elif not isinstance(self.fluent, str) or not self.fluent:
            return "Fluents must be non-empty strings."
        elif not isinstance(self.value, str) or not self.value:
            return "Fluent values must be non-empty strings."
        elif not isinstance(self.step, int) or self.step < 0:
            return "Step values must be integers greater than or equal to zero."
        return None

class ActionLiteral(Literal):
    """
    Represents an action literal as a typed four-tuple of the form:
            < al, robot, action, step >
    Whose encoding as an ASP symbol (an atom) of the form:
            occurs(al, robot, action, step)
    
    Actions are function symbols declaring operators usable by robots.
    Action literals are function symbols defining that robot has planned an action at a given abstraction level and time step.
    
    Fields
    ------
    `al : int` - An integer, greater than zero, defining the abstraction level of the action literal.
    
    `robot : str` - A non-empty string defining the name of the executing robot of the action literal.
    
    `action : str` - A non-empty string defining the action itself, usually a function symbol of the form `name(arg_1, arg_2, ... arg_n)`.
    
    `step : int` - An integer, greater than zero, defining the discrete time step the action is planned to occur at.
    """
    robot: str
    action: str
    step: int
    
    @classmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> "ActionLiteral":
        return cls(al=int(symbol.arguments[0].number), robot=str(symbol.arguments[1]),
                   action=str(symbol.arguments[2]), step=int(symbol.arguments[3].number))
    
    @classmethod
    def predicate_name(cls) -> str:
        return "occurs"

class SubGoalLiteral(Literal):
    robot: str
    action: str
    fluent: str
    value: str
    index: int
    
    @classmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> "SubGoalLiteral":
        return cls(al=int(symbol.arguments[0].number), robot=str(symbol.arguments[1]),
                   action=str(symbol.arguments[2]), fluent=str(symbol.arguments[3]),
                   value=str(symbol.arguments[4]), step=int(symbol.arguments[5].number))
    
    @classmethod
    def predicate_name(cls) -> str:
        return "sgoal"

class FinalGoalLiteral(Literal):
    fluent: str
    value: str
    truth: bool
    
    @classmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> "FinalGoalLiteral":
        return cls(al=int(symbol.arguments[0].number), fluent=str(symbol.arguments[1]),
                   value=str(symbol.arguments[2]), truth=str(symbol.arguments[3]) == "true")
    
    @classmethod
    def predicate_name(cls) -> str:
        return "fgoal"

class State(_collections_abc.Set):
    literals: FluentLiteral

@dataclass(frozen=True)
class State(SequenceDataClass):
    abstract: set[FluentLiteral]
    original: set[FluentLiteral]
    
    @property
    def encoding(self) -> set[clingo.Symbol]:
        return {fluent.symbol for state in self for fluent in state}
    
    def __contains__(self, fluent: FluentLiteral) -> bool:
        return fluent in self.ul or fluent in self.pl
    
    def __iter__(self) -> Iterator[FluentLiteral]:
        for fluent in (self.ul | self.pl):
            yield fluent
    
    def __len__(self) -> int:
        return len(self.ul) + len(self.pl)

@dataclass
class ActionSet(_collections_abc.Set):
    actions: set[ActionLiteral]
    
    def __post_init__(self) -> None:
        if not self.actions:
            raise ValueError("Action sets must contain at least one action.")
    
    @property
    def level(self) -> int:
        self.actions[0].level
    
    @property
    def step(self) -> int:
        self.actions[0].step
    
    @staticmethod
    def from_model(model: ASP.Model) -> dict[int, "ActionSet"]:
        actions: dict[int, list[dict[str, Union[int, str]]]] = model.query("occurs", ["L", "R", "A", "I"], True, sort_by="I", group_by="I", convert_to={"L" : int, "R" : str, "A" : str, "I" : int})
        action_sets: dict[int, ActionSet] = {}
        for step in actions:
            action_sets[step] = ActionSet({ActionLiteral(*action.values()) for action in actions[step]})
        return action_sets

@dataclass(order=True, frozen=True)
class FinalGoal(_collections_abc.Set):
    goals: FrozenSet[FinalGoalLiteral] = field(compare=False)
    al: int = field(default=None, compare=True)
    
    def satisfied_in(self, state: State) -> bool:
        return all(((FluentLiteral(goal.al, goal.fluent, goal.value, state.step) in state) if goal.truth else
                    (FluentLiteral(goal.al, goal.fluent, goal.value, state.step) not in state)) for goal in self.goals)
    
    def __contains__(self, goal: FinalGoalLiteral) -> bool:
        return goal in self.goals
    
    def __iter__(self) -> Iterator[FinalGoalLiteral]:
        for goal in self.goals:
            yield goal
    
    def __len__(self) -> int:
        return len(self.goals)

class SubGoalStage(_collections_abc.Set):
    subgoals: frozenset[SubgoalLiteral] = field(compare=False)
    
    def achieved_simultaneously_by(self, transition: "StateTransition") -> bool:
        pass
    
    def achieved_sequentially_by(self, monolevel_plan: "MonolevelPlan") -> bool:
        pass
    
    def encode(self, as_strings: bool = False) -> Union[set[clingo.Symbol], set[str]]:
        if as_strings: return {str(literal) for literal in self.actions}
        else: return {literal.symbol for literal in self.actions}
    
    def __contains__(self, subgoal: SubgoalLiteral) -> bool:
        return subgoal in self.subgoals
    
    def __iter__(self) -> Iterator[SubgoalLiteral]:
        for subgoal in self.subgoals:
            yield subgoal
    
    def __len__(self) -> int:
        return len(self.subgoals)

@dataclass(frozen=True, order=True)
class StateTransition:
    """
    Represents a state transition as a three-tuple of the form:
            < states, actions, states >
    A transition defines a state change resulting from the execution of an action set.
    
    Fields
    ------
    `start_state : StatePair` - The original state in which the transition starts.
    
    `action_set : ActionSet` - The action set planned that causes this state transition and produces its sub-goals.
    
    `end_state : StatePair` - The resulting state in which the transition ends.
    
    `sub_goal_stage : SubGoalStage` - The sub-stage produced by this state transition.
    This contains a set of sub-goal literals defined by the effects of the action set in the start state.
    """
    start_state: StatePair
    action_set: ActionSet
    end_state: StatePair
    sub_goal_stage: SubGoalStage
    
    @property
    def al(self) -> int:
        """An integer defining the abstraction level of this state transition."""
        return self.start_states.cl.al
    
    @property
    def step(self) -> int:
        """An integer defining the discrete time step of this state transition."""
        return self.start_states.cl.step

class RefinementTree:
    """
    A tree structure that shows how actions are refined, i.e. the subplans that achieve the same effects.
    
    These are extracted from hierarchical refinement diagrams, and allow us to look at what actions are
    needed to achieve the same effects as the head, under the increased planning constraints at the lower
    levels in the hierarchy.
    
    We can also understand more easily, how greedy subgoal stage achievement works,
    how interleaving can increase plan quality of the lower levels are solved as combined problems, and
    where problem divisions can be made. They can also let us see how final goal preferences can affect choices made in earlier partial-problems of online planning.
    
    Action refinement trees only care about the actions, their effects,
    how those effects create subgoal stages (sets of positive goal literals), and how lower level action effects
    map to and achieve some subgoals and thus the effects of the higher level actions, but otherwise they don't care about states.
    
    Contains all the children (a sub-plan) of a given abstract state transition, these are the actions that uniquely achieve the sub-goal stage produced from it.
    
    Matching Child: The original level state transition that achieved the sub-goal stage generated from this abstract state transition.
    
    Works on parents (head) and child (leaf) nodes, the most right-hand action's (the matching child's action) effects map upwards to have a conforming sub-goal state.
    
             __________
            |          |
            |   Head   |
            |__________|
                  v
         _____v____
        |          |
        |   Leaf   | ... ->
        |__________|
    
    """
    head: StateTransition
    sub_goal_stage: SubGoalStage
    children: list["RefinementTree"]

# Finding dependencies:
#   - The planner determines if dependencies exist, and stores the result back in the hierarchical plan
#   - A refinement tree extracted from a hierarchical plan
# Planner.detect_interleaving(diagram_or_tree) and Planner.detect_dependencies(hierarchical_plan: HierarchicalPlan)
#   - solves as sub-problems and look for missing actions
#   - each sub-problem starts from the state the previous subgoal stage was achieved, has no end state, and must just achieve one subgoal stage
#   - i.e. we are looking for the minimal greedy achievement of the subgoal stage

## Add division number and increment number of monolevel plan class - Division number (defined by input in online_plan) and increment number (defined internally my the top-bottom increment and the division strategy) are not the same thing!
## The increment number is the increment upon which that division number was solved.
## In fast downwards, there is a number of online planning increments at each level equal to the number of divisions $n$ where $div(CP^{pl}, n)$ is the divided problem at that level, and a total number of increments equal to the number of ground level divisions.

class MonolevelPlan:
    """
    Represents a monolevel plan as a sequence of state transitions.
    
    Fields
    ------
    `level : int` -
    
    `planning_increment : int` -
    """
    
    __slots__ = ("__final", # access: private, type: bool
                 "__states", # access: private, type: dict[int, State], maps: step -> action-set
                 "__actions", # access: private, type: dict[int, ActionSet], maps: step -> action-set
                 "__produced_sgoals", # access: private, type: dict[int, SubGoalStage], maps: index -> sub-goal-stage
                 "__current_sgoals", # access: private, type: dict[int, int], maps: step -> index
                 "__sgoals_achieved_at") # access: private, type: dict[int, int], maps: index -> step
    
    def __init__(self, problem: MonolevelProblem, planning_increment: int, final: bool, model: ASP.Model) -> None:
        self.__problem: MonolevelProblem = problem
        self.__planning_increment: int = planning_increment
        self.__final: bool = final
        self.__states: dict[int, State] = State.from_model(model)
        self.__actions: dict[int, Actions] = Actions.from_model(model)
        self.__produced_sgoals: dict[int, SubGoalStage] = SubGoalStage.from_model(model)
        self.__current_sgoals: dict[int, int]
        self.__sgoals_achieved_at: dict[int, int]
    
    def get_conformance_constraint(self, sgoals_slice: slice) -> list[SubGoalStage]:
        if sgoals_slice is not None:
            raise ValueError(f"Sub-goal stage slices must be contiguous (step value is None), got {sgoals_slice}.")
        return {index : self.__produced_sgoals[index] for index in list(self.__produced_sgoals)[sgoals_slice]}
    
    @property
    def level(self) -> int:
        return self.__problem.level
    
    @property
    def first_step(self) -> int:
        return self.__states.keys[0]
    
    @property
    def last_step(self) -> int:
        return self.__states.keys[-2]
    
    @property
    def solves_problem(self) -> MonolevelProblem:
        return self.__problem
    
    @property
    def division_number(self) -> int:
        return self.__problem.division_number
    
    @property
    def increment_number(self) -> int:
        return self.__increment_number
    
    @property
    def is_final(self) -> bool:
        return self.__final

class RefinementDiagram(AbstractionHierarchy):
    """
    Stores a very large amount of information regarding the solution to a hierarchical planning problem.
    Shows how initial states and final goal states conform.
    Higher level plans are parents, lower level plans are children, each parent's children are a sub-plan (each child is a state transition rather than just an action as n refinement trees),
    the last of which achieves its subgoal stage uniquely (and minimally if a division was made just after) and is called the matching child.
    """
    ## Better to keep the reference to the hierarchical problem in the monolevel problem class and only attach the monolevel problem to the hierarchical when the solution is given.
    
    __slots__ = ("__hierarchical_problem", # access: private, type: HierarchicalProblem
                 "__monolevel_plans", # access: private, type: dict[int, MonolevelPlan]
                 "__revised_plans", # access: private, type: dict[int, list[MonolevelPlan]]
                 "__monolevel_problems" # access: private, type: dict[int, dict[int, ProblemSolution]] maps : level X index -> (problem, plan)
                #  "__complete_plan",
                #  "__current_sgoals",
                #  "__sgoals_achieved_at"
                )
    
    def __init__(self, hierarchical_problem: HierarchicalProblem) -> None:
        self.__hierarchical_problem: HierarchicalProblem = hierarchical_problem
        self.__monolevel_plans: dict[int, MonolevelPlan] = {}
    
    def create_problem(self, level: int, sub_goal_stage_range: range) -> "MonolevelProblem":
        """Construct a monolevel planning problem from this refinement diagram."""
        
        if not self.in_range(level):
            raise ValueError(f"Abstraction level {level} is not in the hierarchy.")
        
        ## Find the start state of monolevel problem:
        ##      - Get the matching child of the previous sub-goal stage (one lower than the minimum of the range),
        ##          - This is the state transition that minimally uniquely achieved the stage,
        ##      - Its end state is the sub-goal stage satisfying state from which we wish to state planning.
        start_state: State = self.get_matching_child_of(min(sub_goal_stage_range) - 1).end_state
        
        ## Find the conformance constraint trimmed over the subgoal stage range
        conformance_constraint: list[SubGoalStage] = self.get_current_plan(level).get_conformance_constraint(sub_goal_stage_range)
        
        ## Determine whether the planning problem should achieve the final goal
        finalise: bool = self.is_complete(level + 1) and max(sub_goal_stage_range) == self.final_sub_goal_stage.index
        
        return MonolevelProblem(self.__hierarchical_problem, start_state, conformance_constraint, finalise)
    
    def attach_plan(self, monolevel_plan: MonolevelPlan) -> None:
        """Attach a monolevel plan to the diagram."""
        
        ## Check the monolevel plan is relevant
        if self.__hierarchical_problem != monolevel_plan.solution_to.hierarchical_problem:
            raise ValueError(f"The monolevel plan {monolevel_plan} is not related to {self}.")
        
        ## Update the plan
        
        
        ## Update conformance mappings
        
        
        ## Update whether the level is complete
        if monolevel_plan.is_final:
            self.__complete_plan[monolevel_plan.level] = True
        
        return None
    
    def get_current_plan(self, level: int) -> Optional[MonolevelPlan]:
        """Get the currently stored monolevel plan at the given abstraction level."""
        return self.__monolevel_plans.get(level, None)
    
    def contains_plan(self, level: int) -> bool:
        return self.get_current_plan(level) is not None
    
    def is_complete(self, level: int) -> bool:
        """Check if the currently stored plan at the given abstraction level is complete."""
        return self.__complete.get(level, False)
    
    def unachieved_sgoals_at(self, level: int) -> bool:
        raise NotImplementedError
    
    def lowest_unachieved_sgoals_at(self) -> Optional[int]:
        for level in self.level_range:
            if self.unachieved_sgoals_at(level):
                return level
        return None

class RefinementSchema:
    """
    Refinement schemas contain the sub-goal stages, but not the intermediate start states of the partial problems.
    The intermediate start states (because it stores the entire plans (needed because we might be doing blending) and the division scenarios (showing how the sub-goals are split up) are only stored in the refinement diagrams.
    This is because since these are known only as solving progresses/propagates through the seequence of partial problems.
    They are blueprints for forming the same conformance refinement hierarchical planning structure, i.e. the conformance will be the same with the schema.
    
    Refinement schemas store information about conformance constraints generated in abstract domain models.
    This allows us to form refinement planning problems from hierarchical planning problems, which usually would not be possible, since hierarchical problems do not store sub-goal stages.
    Sub-goal stages can only be found by solving abstract problems.
    
    An omni-refinement diagram stores and maps multiple plans at each abstraction level, to a range of (or possibly all) possible refinements of those plans at the next level
    """
    pass

## Minimum step bound - min_step_bound:
##      Estimator = Optional[Estimator] = Simple = {
##          Explicit(allow custom estimators using a callback function that takes IT and AL as arguments and returns an integer), <- This means that planning increment will have to be instance variable
##          Simple(makes basic estimate of minimum possible plan length, i.e. plan_from + num_sgoals),
##          Predict(type={cautious, balanced, reckless(requires optimisation for steps)} makes dynamic estimates based on previous increments)}

## Incrementor = {Fixed(num: int), Dynamic(type={Decaying(rate: float), Stepwise(step: int)})} anything other than "Static(num=1)" requires optimisation for steps or returned plans will not be optimal}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Constants
%**% #program constants.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Maximum abstraction level
#const abstraction_max = 5.

%% Maximum planning horizon
#const steps_max = 20.

#const redefinition_level = 5.
#const reduction_level = 4.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Class Hierarhcy
%**% #program class_hierarchy.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Class Type Declarations - class(AL, CLS) declares a class CLS at abstraction level AL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class(5, robot).
class(5, armed_robot).
class(5, transport_robot).
class(5, place).
class(5, room).
class(5, object).
class(5, graspable).
class(5, placeable).
class(5, surface).
class(5, block).
class(5, table).
class(5, null).
class(5, colour).

class(4, component).
class(4, manipulator_arm).
class(4, grasper).

class(3, configurable). %% Can be safely but manually pruned from the class hierarchy due to the reduction making configuration states irrelavent
class(3, extensible).

class(2, cell).

class(1, manipulator_limb).
class(1, manipulator_end).
class(1, side).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Class Type Inheritance Relations - super_class(C1, C2) defines C1 as a super class of C2 if class(AL_1, CLS_1), class(AL_2, CLS_2), AL_1 >= AL_2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

super_class(robot, armed_robot).
super_class(robot, transport_robot).

super_class(place, room).
super_class(place, cell).

super_class(object, robot).
super_class(object, manipulator_arm).
super_class(object, manipulator_limb).
super_class(object, manipulator_end).
super_class(object, block).
super_class(object, table).
super_class(object, side).

super_class(component, cell).
super_class(component, manipulator_arm).
super_class(component, manipulator_limb).
super_class(component, manipulator_end).
super_class(component, side).

super_class(configurable, extensible).
super_class(configurable, grasper).

super_class(extensible, manipulator_arm).
super_class(extensible, manipulator_limb).

super_class(grasper, manipulator_arm).
super_class(grasper, manipulator_end).

super_class(graspable, block).

super_class(placeable, block).

super_class(surface, table).
super_class(surface, side).
super_class(surface, block).

super_class(surface, null).
super_class(component, null).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Class Type Overrides - overrides_type(CLS_1, CLS_2, CLS_3) deletes the CLS_3 type of CLS_1 when for components of type CLS_2 exist at AL >= plan_at
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% End-effectors can grasp objects
overrides_type(manipulator_arm, manipulator_end, grasper).

%% Manipulator limbs are extensible
overrides_type(manipulator_arm, manipulator_limb, extensible).

%% The cells of rooms are places
overrides_type(room, cell, place).

%% The sides of a table are surfaces
overrides_type(table, side, surface).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Entities, Component Relations, and Configuration States
%**% #program entities.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%s%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Entity Instance Declarations - entity(CLS, EN) declares an entity EN of class CLS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

entity(armed_robot, talos).
entity(transport_robot, bastion).

entity(manipulator_arm, manipulator_arm_1).
entity(manipulator_limb, manipulator_limb_1).
entity(manipulator_end, manipulator_end_1).

entity(manipulator_arm, manipulator_arm_2).
entity(manipulator_limb, manipulator_limb_2).
entity(manipulator_end, manipulator_end_2).

number(1..9).
entity(block, (block, N)) :- number(N).

entity(room, starting_room).
entity(room, store_room).
entity(room, puzzle_room).
entity(room, hallway).

x(0..2).
size(ROOM, 2) :- entity(room, ROOM), ROOM != hallway.
size(hallway, 3).
entity(cell, (ROOM, X)) :- entity(room, ROOM), size(ROOM, MAX), X < MAX, x(X).

entity(null, nothing).

entity(table, puzzle_room_table).

entity(side, puzzle_room_table_left).
entity(side, puzzle_room_table_middle).
entity(side, puzzle_room_table_right).

entity(colour, red).
entity(colour, yellow).
entity(colour, blue).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Entity Component Relationships - component_relation(EN, COMP) delcares that entity EN has a component COMP
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

component_relation(talos, manipulator_arm_1).
component_relation(talos, manipulator_arm_2).

component_relation(manipulator_arm_1, manipulator_limb_1).
component_relation(manipulator_arm_2, manipulator_limb_2).

component_relation(manipulator_arm_1, manipulator_end_1).
component_relation(manipulator_arm_2, manipulator_end_2).

component_relation(ROOM, (ROOM, X)) :- entity(room, ROOM), entity(cell, (ROOM, X)), x(X).

component_relation(nothing, nothing).

component_relation(puzzle_room_table, puzzle_room_table_left).
component_relation(puzzle_room_table, puzzle_room_table_middle).
component_relation(puzzle_room_table, puzzle_room_table_right).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Entity Configuration State Declarations - state(CLS, S) declares a state S for class CLS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

state(AL, extensible, extended) :- AL < reduction_level, abstraction_level(AL).
state(AL, extensible, retracted) :- AL < reduction_level, abstraction_level(AL).

state(AL, manipulator_end, aligned_with(OBJ)) :- instance_of(AL, graspable, OBJ), class(AL, manipulator_end), AL < reduction_level, abstraction_level(AL).
state(AL, manipulator_end, aligned_with(nothing)) :- class(AL, manipulator_end), AL < reduction_level, abstraction_level(AL).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Domain Properties and Actions
%**% #program domain_properties_and_actions.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Statics - Define the static domain properties here
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Statics are given in the form - static(abstraction_level, static)

%% Places can be connected
static(AL, connected(P_1, P_2)) :- instance_of(AL, place, P_1),
                                   instance_of(AL, place, P_2),
                                   abstraction_level(AL).

%% Blocks have colours
static(AL, colour_of(BLOCK, COLOUR)) :- instance_of(AL, block, BLOCK),
                                        instance_of(AL, colour, COLOUR),
                                        abstraction_level(AL).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Fluents - Define the fluent domain properties here
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Fluents are given in the form - fluent(abstraction_level, fluent_type, fluent, value)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Inertial Fluents

%% All objects must be located in a place
fluent(AL_1, physical, inertial, location(OBJ), P) :- instance_of(AL_2, object, OBJ),
                                                      instance_of(AL_1, place, P),
                                                      state_representation_level(AL_2),
                                                      state_representation_level(AL_1),
                                                      AL_2 >= AL_1.

%% Objects can be placed on other surfaces
fluent(AL_1, physical, inertial, on(OBJ), SURFACE) :- OBJ != SURFACE,
                                                      instance_of(AL_2, placeable, OBJ),
                                                      instance_of(AL_1, surface, SURFACE),
                                                      state_representation_level(AL_2),
                                                      state_representation_level(AL_1),
                                                      AL_2 >= AL_1.

%% Graspable objects can be grasped by a grasper that is a component of a robot
fluent(AL_1, physical, inertial, grasping(ROBO, COMP, OBJ), B) :- descendant_of(AL_1, ROBO, COMP),
                                                                  instance_of(AL_3, armed_robot, ROBO),
                                                                  instance_of(AL_2, grasper, COMP),
                                                                  instance_of(AL_1, graspable, OBJ),
                                                                  AL_3 < redefinition_level,
                                                                  AL_2 < redefinition_level,
                                                                  AL_1 < redefinition_level,
                                                                  state_representation_level(AL_3),
                                                                  state_representation_level(AL_2),
                                                                  state_representation_level(AL_1),
                                                                  AL_2 >= AL_1, AL_3 >= AL_1,
                                                                  boolean(B).

%% All of a robot's reconfigurable components must have a configuration
fluent(AL_1, physical, inertial, configuration(ROBO, COMP), STATE) :- descendant_of(AL_1, ROBO, COMP),
                                                                      state_of(AL_1, COMP, STATE),
                                                                      instance_of(AL_3, armed_robot, ROBO),
                                                                      instance_of(AL_2, configurable, COMP),
                                                                      AL_3 < reduction_level,
                                                                      AL_2 < reduction_level,
                                                                      AL_1 < reduction_level,
                                                                      state_representation_level(AL_3),
                                                                      state_representation_level(AL_2),
                                                                      state_representation_level(AL_1),
                                                                      AL_2 >= AL_1, AL_3 >= AL_1.

%% In the redefined model robots can be transporting objects
fluent(AL_1, physical, inertial, transporting(ROBO, OBJ), B) :- instance_of(AL_2, armed_robot, ROBO),
                                                                instance_of(AL_1, graspable, OBJ),
                                                                AL_1 >= redefinition_level,
                                                                state_representation_level(AL_2),
                                                                state_representation_level(AL_1),
                                                                AL_2 >= AL_1,
                                                                boolean(B).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Defined Fluents

%% A block that is on a table is the base of a tower
fluent(AL, physical, defined, tower_base(BASE), B) :- instance_of(AL, block, BASE),
                                                      state_representation_level(AL),
                                                      boolean(B).

%% A block that is the base of a tower or placed upon another block that is in a tower also in the same tower
fluent(AL, physical, defined, in_tower(BASE, BLOCK), B) :- instance_of(AL, block, BASE),
                                                           instance_of(AL, block, BLOCK),
                                                           state_representation_level(AL),
                                                           boolean(B).

%% A tower that is not stacked in descending order from top to bottom is unordered
fluent(AL, physical, defined, unordered_tower(BASE), B) :- instance_of(AL, block, BASE),
                                                           state_representation_level(AL),
                                                           boolean(B).

%% A tower is complete if all the blocks that form it are the same colour and they are stacked in descending order from top to bottom
fluent(AL, physical, defined, complete(COLOUR), B) :- instance_of(AL, colour, COLOUR),
                                                      state_representation_level(AL),
                                                      boolean(B).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Actions - Define the available actions here
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Actions are given in the form - action(abstraction_level, action_type, actor, action)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Agent Actions

%% All robots can move between locations
action(AL, sequential, ROBO, move(P)) :- instance_of(AL, robot, ROBO),
                                         instance_of(AL, place, P),
                                         state_representation_level(AL).

%% Transport robots can push object between locations
action(AL, sequential, ROBO, push(OBJ, P)) :- instance_of(AL, transport_robot, ROBO),
                                              instance_of(AL, graspable, OBJ),
                                              instance_of(AL, place, P),
                                              state_representation_level(AL).

%% Armed robots can grasp objects with their graspers
action(AL, concurrent, ROBO, grasp(COMP, OBJ)) :- descendant_of(AL, ROBO, COMP),
                                                  instance_of(AL, armed_robot, ROBO),
                                                  instance_of(AL, grasper, COMP),
                                                  instance_of(AL, graspable, OBJ),
                                                  AL < redefinition_level,
                                                  state_representation_level(AL).

%% Robots can release objects from their graspers
action(AL, concurrent, ROBO, release(COMP, OBJ)) :- descendant_of(AL, ROBO, COMP),
                                                    instance_of(AL, armed_robot, ROBO),
                                                    instance_of(AL, grasper, COMP),
                                                    instance_of(AL, graspable, OBJ),
                                                    AL < redefinition_level,
                                                    state_representation_level(AL).

%% Robots can put objects on surfaces
action(AL, concurrent, ROBO, put(COMP, OBJ, SURFACE)) :- OBJ != SURFACE,
                                                         SURFACE != nothing,
                                                         descendant_of(AL, ROBO, COMP),
                                                         instance_of(AL, armed_robot, ROBO),
                                                         instance_of(AL, grasper, COMP),
                                                         instance_of(AL, placeable, OBJ),
                                                         instance_of(AL, surface, SURFACE),
                                                         AL < redefinition_level,
                                                         state_representation_level(AL).

%% Robots can lift objects off of surfaces
action(AL, concurrent, ROBO, lift(COMP, OBJ)) :- descendant_of(AL, ROBO, COMP),
                                                 instance_of(AL, armed_robot, ROBO),
                                                 instance_of(AL, grasper, COMP),
                                                 instance_of(AL, placeable, OBJ),
                                                 AL < redefinition_level,
                                                 state_representation_level(AL).

%% Robots can set the configuration state of their configurable components
action(AL, concurrent, ROBO, configure(COMP, STATE)) :- descendant_of(AL, ROBO, COMP),
                                                        instance_of(AL, armed_robot, ROBO),
                                                        instance_of(AL, configurable, COMP),
                                                        state_of(AL, COMP, STATE),
                                                        AL < reduction_level,
                                                        state_representation_level(AL).

%% In the redefined model robots can collect objects
action(AL, concurrent, ROBO, collect(OBJ)) :- instance_of(AL, armed_robot, ROBO),
                                              instance_of(AL, graspable, OBJ),
                                              AL >= redefinition_level,
                                              state_representation_level(AL).

%% In the redefined model robots can deposit objects
action(AL, concurrent, ROBO, deposit(OBJ)) :- instance_of(AL, armed_robot, ROBO),
                                              instance_of(AL, graspable, OBJ),
                                              AL >= redefinition_level,
                                              state_representation_level(AL).

%% In the redefined model robots can pick up and put down objects with a single action
action(AL, concurrent, ROBO, pick_and_put(OBJ, SURFACE)) :- instance_of(AL, armed_robot, ROBO),
                                                            instance_of(AL, placeable, OBJ),
                                                            instance_of(AL, surface, SURFACE),
                                                            AL >= redefinition_level,
                                                            state_representation_level(AL).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Domain Specific Rules - The domain's dynamic behaviour is defined here
%**% #program domain_rules.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Agent Action Effects
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% When a robot moves its location changes
effect(AL, ROBO, move(P), location(ROBO), P, I) :- instance_of(AL, robot, ROBO),
                                                   instance_of(AL, place, P),
                                                   planning_level(AL),
                                                   step(I).

effect(AL, ROBO, push(OBJ, P), location(ROBO), P, I) :- instance_of(AL, robot, ROBO),
                                                        instance_of(AL, graspable, OBJ),
                                                        instance_of(AL, place, P),
                                                        planning_level(AL),
                                                        step(I).

effect(AL, ROBO, push(OBJ, P), location(OBJ), P, I) :- instance_of(AL, robot, ROBO),
                                                       instance_of(AL, graspable, OBJ),
                                                       instance_of(AL, place, P),
                                                       planning_level(AL),
                                                       step(I).

%% When a robot grasps an object the object becomes grasped
effect(AL, ROBO, grasp(COMP, OBJ), grasping(ROBO, COMP, OBJ), true, I) :- descendant_of(AL, ROBO, COMP),
                                                                          instance_of(AL, armed_robot, ROBO),
                                                                          instance_of(AL, grasper, COMP),
                                                                          instance_of(AL, graspable, OBJ),
                                                                          AL < redefinition_level,
                                                                          planning_level(AL),
                                                                          step(I).

%% When a robot releases an object the object is no longer grasped
effect(AL, ROBO, release(COMP, OBJ), grasping(ROBO, COMP, OBJ), false, I) :- descendant_of(AL, ROBO, COMP),
                                                                             instance_of(AL, armed_robot, ROBO),
                                                                             instance_of(AL, grasper, COMP),
                                                                             instance_of(AL, graspable, OBJ),
                                                                             AL < redefinition_level,
                                                                             planning_level(AL),
                                                                             step(I).

%% When a robot releases an object from an end effector it is no longer aligned with that object
effect(AL, ROBO, release(END, OBJ), configuration(ROBO, END), aligned_with(nothing), I) :- descendant_of(AL, ROBO, END),
                                                                                           instance_of(AL, armed_robot, ROBO),
                                                                                           instance_of(AL, manipulator_end, END),
                                                                                           instance_of(AL, graspable, OBJ),
                                                                                           AL < redefinition_level,
                                                                                           planning_level(AL),
                                                                                           step(I).

%% When a robot configures a component it causes the state of that component to change
effect(AL, ROBO, configure(COMP, STATE), configuration(ROBO, COMP), STATE, I) :- descendant_of(AL, ROBO, COMP),
                                                                                 instance_of(AL, robot, ROBO),
                                                                                 instance_of(AL, configurable, COMP),
                                                                                 state_of(AL, COMP, STATE),
                                                                                 AL < redefinition_level,
                                                                                 planning_level(AL),
                                                                                 step(I).

%% When a robot retracts a manipulator arm any end effector attached to that arm is no longer aligned with any objects unless it is grasping an object
effect(AL, ROBO, configure(ARM, retracted), configuration(ROBO, END), aligned_with(nothing), I) :- 0 = #count { OBJ : holds(AL, grasping(ROBO, END, OBJ), true, I),
                                                                                                                      instance_of(AL, graspable, OBJ) },
                                                                                                   descendant_of(AL, ROBO, ARM),
                                                                                                   descendant_of(AL, ROBO, END),
                                                                                                   siblings(AL, ARM, END),
                                                                                                   instance_of(AL, armed_robot, ROBO),
                                                                                                   instance_of(AL, extensible, ARM),
                                                                                                   instance_of(AL, manipulator_end, END),
                                                                                                   AL < redefinition_level,
                                                                                                   planning_level(AL),
                                                                                                   step(I).

%% When a robot puts an object on a surface the object is on that surface
effect(AL, ROBO, put(COMP, OBJ, SURFACE), on(OBJ), SURFACE, I) :- OBJ != SURFACE,
                                                                  SURFACE != nothing,
                                                                  descendant_of(AL, ROBO, COMP),
                                                                  instance_of(AL, armed_robot, ROBO),
                                                                  instance_of(AL, grasper, COMP),
                                                                  instance_of(AL, placeable, OBJ),
                                                                  instance_of(AL, surface, SURFACE),
                                                                  AL < redefinition_level,
                                                                  planning_level(AL),
                                                                  step(I).

%% When a robot lifts an object the object is on nothing
effect(AL, ROBO, lift(COMP, OBJ), on(OBJ), nothing, I) :- descendant_of(AL, ROBO, COMP),
                                                          instance_of(AL, armed_robot, ROBO),
                                                          instance_of(AL, grasper, COMP),
                                                          instance_of(AL, placeable, OBJ),
                                                          AL < redefinition_level,
                                                          planning_level(AL),
                                                          step(I).

%% When a robot collects and object it is transporting that object
effect(AL, ROBO, collect(OBJ), transporting(ROBO, OBJ), true, I) :- instance_of(AL, armed_robot, ROBO),
                                                                    instance_of(AL, graspable, OBJ),
                                                                    AL >= redefinition_level,
                                                                    planning_level(AL),
                                                                    step(I).

%% When a robot collects an object the object is on nothing
effect(AL, ROBO, collect(OBJ), on(OBJ), nothing, I) :- instance_of(AL, armed_robot, ROBO),
                                                       instance_of(AL, graspable, OBJ),
                                                       AL >= redefinition_level,
                                                       planning_level(AL),
                                                       step(I).

%% When a robot deposits an object it is no longer transporting that object
effect(AL, ROBO, deposit(OBJ), transporting(ROBO, OBJ), false, I) :- instance_of(RL, armed_robot, ROBO),
                                                                     instance_of(RL, graspable, OBJ),
                                                                     AL >= redefinition_level,
                                                                     planning_level(AL),
                                                                     step(I).

%% When a robot picks up and puts down an object on a surface the object is on that surface
effect(AL, ROBO, pick_and_put(OBJ, SURFACE), on(OBJ), SURFACE, I) :- OBJ != SURFACE,
                                                                     SURFACE != nothing,
                                                                     instance_of(AL, armed_robot, ROBO),
                                                                     instance_of(AL, placeable, OBJ),
                                                                     instance_of(AL, surface, SURFACE),
                                                                     AL >= redefinition_level,
                                                                     planning_level(AL),
                                                                     step(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Agent Action Preconditions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% A robot can only move between locations that are connected
precondition(AL, ROBO, move(P_2), location(ROBO), P_1, false, I) :- -is(AL, connected(P_1, P_2)),
                                                                    P_1 != P_2,
                                                                    instance_of(AL, robot, ROBO),
                                                                    instance_of(AL, place, P_1),
                                                                    instance_of(AL, place, P_2),
                                                                    AL < reduction_level,
                                                                    planning_level(AL),
                                                                    step(I).

%% A robot can only move if all of its extensible components are retracted
precondition(AL, ROBO, move(P), configuration(ROBO, COMP), retracted, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                  instance_of(AL, armed_robot, ROBO),
                                                                                  instance_of(AL, extensible, COMP),
                                                                                  instance_of(AL, place, P),
                                                                                  planning_level(AL),
                                                                                  AL < reduction_level,
                                                                                  step(I).

precondition(AL, ROBO, push(OBJ, P_2), location(ROBO), P_1, false, I) :- -is(AL, connected(P_1, P_2)),
                                                                    P_1 != P_2,
                                                                    instance_of(AL, transport_robot, ROBO),
                                                                    instance_of(AL, graspable, OBJ),
                                                                    instance_of(AL, place, P_1),
                                                                    instance_of(AL, place, P_2),
                                                                    AL < reduction_level,
                                                                    planning_level(AL),
                                                                    step(I).

precondition(AL, ROBO, push(OBJ, P_1), location(ROBO), P_2, true, I) :- holds(AL, location(OBJ), P_2, I),
                                                                    instance_of(AL, transport_robot, ROBO),
                                                                    instance_of(AL, graspable, OBJ),
                                                                    instance_of(AL, place, P_1),
                                                                    instance_of(AL, place, P_2),
                                                                    planning_level(AL),
                                                                    step(I).

precondition(AL, ROBO, push(OBJ, P), on(OBJ), SURFACE, false, I) :- SURFACE != nothing,
                                                                    instance_of(AL, transport_robot, ROBO),
                                                                    instance_of(AL, graspable, OBJ),
                                                                    instance_of(AL, surface, SURFACE),
                                                                    instance_of(AL, place, P),
                                                                    planning_level(AL),
                                                                    step(I).

precondition(AL, ROBO_1, push(OBJ, P), grasping(ROBO_2, COMP, OBJ), false, true, I) :- descendant_of(AL, ROBO_2, COMP),
                                                                                       instance_of(AL, transport_robot, ROBO_1),
                                                                                       instance_of(AL, armed_robot, ROBO_2),
                                                                                       instance_of(AL, grasper, COMP),
                                                                                       instance_of(AL, graspable, OBJ),
                                                                                       instance_of(AL, place, P),
                                                                                       planning_level(AL),
                                                                                       step(I).

precondition(AL, ROBO_1, push(OBJ, P), transporting(ROBO_2, OBJ), false, true, I) :- instance_of(AL, transport_robot, ROBO_1),
                                                                                     instance_of(AL, armed_robot, ROBO_2),
                                                                                     instance_of(AL, graspable, OBJ),
                                                                                     instance_of(AL, place, P),
                                                                                     planning_level(AL),
                                                                                     step(I).

%% An armed robot can only grasp an object when it is in the same location as that object
precondition(AL, ROBO, grasp(COMP, OBJ), location(OBJ), P, true, I) :- holds(AL, location(ROBO), P, I),
                                                                       descendant_of(AL, ROBO, COMP),
                                                                       instance_of(AL, armed_robot, ROBO),
                                                                       instance_of(AL, grasper, COMP),
                                                                       instance_of(AL, graspable, OBJ),
                                                                       instance_of(AL, place, P),
                                                                       planning_level(AL),
                                                                       step(I).

precondition(AL, ROBO, grasp(COMP, OBJ), location(ROBO), P, true, I) :- holds(AL, location(OBJ), P, I),
                                                                        descendant_of(AL, ROBO, COMP),
                                                                        instance_of(AL, armed_robot, ROBO),
                                                                        instance_of(AL, grasper, COMP),
                                                                        instance_of(AL, graspable, OBJ),
                                                                        instance_of(AL, place, P),
                                                                        planning_level(AL),
                                                                        step(I).

%% An armed robot can only grasp an object with a given grasper if it is not currently grasping another object with that grasper
precondition(AL, ROBO, grasp(COMP, OBJ_1), grasping(ROBO, COMP, OBJ_2), false, true, I) :- OBJ_1 != OBJ_2,
                                                                                           descendant_of(AL, ROBO, COMP),
                                                                                           instance_of(AL, armed_robot, ROBO),
                                                                                           instance_of(AL, grasper, COMP),
                                                                                           instance_of(AL, graspable, OBJ_1),
                                                                                           instance_of(AL, graspable, OBJ_2),
                                                                                           instance_of(AL, place, P),
                                                                                           planning_level(AL),
                                                                                           step(I).

%% An armed robot cannot grasp an object that has another object on top of it
precondition(AL, ROBO, grasp(COMP, OBJ_1), on(OBJ_2), OBJ_1, false, I) :- OBJ_1 != OBJ_2,
                                                                          descendant_of(AL, ROBO, COMP),
                                                                          instance_of(AL, armed_robot, ROBO),
                                                                          instance_of(AL, grasper, COMP),
                                                                          instance_of(AL, placeable, OBJ_1),
                                                                          instance_of(AL, surface, OBJ_1),
                                                                          instance_of(AL, placeable, OBJ_2),
                                                                          planning_level(AL),
                                                                          step(I).

%% An armed robot can only grasp an object with a grasper that is extensible if it is extended
precondition(AL, ROBO, grasp(COMP, OBJ), configuration(ROBO, COMP), extended, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                          instance_of(AL, armed_robot, ROBO),
                                                                                          instance_of(AL, grasper, COMP),
                                                                                          instance_of(AL, extensible, COMP),
                                                                                          instance_of(AL, graspable, OBJ),
                                                                                          planning_level(AL),
                                                                                          AL < reduction_level,
                                                                                          step(I).

%% An armed robot can only grasp an object with a grasper that is not extensible but has extensible siblings is those siblings are extended
precondition(AL, ROBO, grasp(COMP_1, OBJ), configuration(ROBO, COMP_2), extended, true, I) :- descendant_of(AL, ROBO, COMP_1),
                                                                                              descendant_of(AL, ROBO, COMP_2),
                                                                                              siblings(AL, COMP_1, COMP_2),
                                                                                              instance_of(AL, armed_robot, ROBO),
                                                                                              instance_of(AL, grasper, COMP_1),
                                                                                              not instance_of(AL, extensible, COMP_1),
                                                                                              instance_of(AL, extensible, COMP_2),
                                                                                              instance_of(AL, graspable, OBJ),
                                                                                              planning_level(AL),
                                                                                              AL < reduction_level,
                                                                                              step(I).

%% An armed robot can only grasp an object with an end effector if that end effector is aligned with that object
precondition(AL, ROBO, grasp(END, OBJ), configuration(ROBO, END), aligned_with(OBJ), true, I) :- descendant_of(AL, ROBO, END),
                                                                                                 instance_of(AL, armed_robot, ROBO),
                                                                                                 instance_of(AL, manipulator_end, END),
                                                                                                 instance_of(AL, graspable, OBJ),
                                                                                                 state_of(AL, END, aligned_with(OBJ)),
                                                                                                 planning_level(AL),
                                                                                                 AL < reduction_level,
                                                                                                 step(I).

%% An armed robot can only release an object when it is grasping that object
precondition(AL, ROBO, release(COMP, OBJ), grasping(ROBO, COMP, OBJ), true, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                        instance_of(AL, armed_robot, ROBO),
                                                                                        instance_of(AL, grasper, COMP),
                                                                                        instance_of(AL, graspable, OBJ),
                                                                                        planning_level(AL),
                                                                                        step(I).

%% An armed robot can only release an object from a grasper that is extensible if it is extended
precondition(AL, ROBO, release(COMP, OBJ), configuration(ROBO, COMP), extended, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                            instance_of(AL, armed_robot, ROBO),
                                                                                            instance_of(AL, grasper, COMP),
                                                                                            instance_of(AL, extensible, COMP),
                                                                                            instance_of(AL, graspable, OBJ),
                                                                                            AL < reduction_level,
                                                                                            planning_level(AL),
                                                                                            step(I).

%% An armed robot can only release an object from a grasper that is not extensible but has extensible siblings is those siblings are extended
precondition(AL, ROBO, release(COMP_1, OBJ), configuration(ROBO, COMP_2), extended, true, I) :- descendant_of(AL, ROBO, COMP_1),
                                                                                                descendant_of(AL, ROBO, COMP_2),
                                                                                                siblings(AL, COMP_1, COMP_2),
                                                                                                instance_of(AL, armed_robot, ROBO),
                                                                                                instance_of(AL, grasper, COMP_1),
                                                                                                not instance_of(AL, extensible, COMP_1),
                                                                                                instance_of(AL, extensible, COMP_2),
                                                                                                instance_of(AL, graspable, OBJ),
                                                                                                planning_level(AL),
                                                                                                step(I).

%% An armed robot can only change the configuration of the descendant components of its manipulator arms if the extensible descendant sibling components of that arm are extended
precondition(AL, ROBO, configure(COMP_1, STATE), configuration(ROBO, COMP_2), extended, true, I) :- descendant_of(AL, ROBO, COMP_1),
                                                                                                    descendant_of(AL, ROBO, COMP_2),
                                                                                                    descendant_of(AL, ROBO, ARM),
                                                                                                    child_of(AL, ARM, COMP_1),
                                                                                                    child_of(AL, ARM, COMP_2),
                                                                                                    siblings(AL, COMP_1, COMP_2),
                                                                                                    instance_of(AL, armed_robot, ROBO),
                                                                                                    instance_of(AL, configurable, COMP_1),
                                                                                                    instance_of(AL, extensible, COMP_2),
                                                                                                    instance_of(AL, manipulator_arm, ARM),
                                                                                                    state_of(AL, COMP_1, STATE),
                                                                                                    AL < reduction_level,
                                                                                                    planning_level(AL),
                                                                                                    step(I).

%% An armed robot cannot align an end effector with an object if it is already grasping another object
precondition(AL, ROBO, configure(COMP, aligned_with(OBJ_1)), grasping(ROBO, COMP, OBJ_2), false, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                                             instance_of(AL, armed_robot, ROBO),
                                                                                                             instance_of(AL, manipulator_end, COMP),
                                                                                                             instance_of(AL, graspable, OBJ_1),
                                                                                                             instance_of(AL, graspable, OBJ_2),
                                                                                                             state_of(AL, COMP, aligned_with(OBJ_1)),
                                                                                                             planning_level(AL),
                                                                                                             step(I).

%% An armed robot can only put an object on a surface when it is in the same location as that surface
precondition(AL, ROBO, put(COMP, OBJ, SURFACE), location(SURFACE), P, true, I) :- holds(AL, location(ROBO), P, I),
                                                                                  descendant_of(AL, ROBO, COMP),
                                                                                  instance_of(AL, armed_robot, ROBO),
                                                                                  instance_of(AL, grasper, COMP),
                                                                                  instance_of(AL, placeable, OBJ),
                                                                                  instance_of(AL, surface, SURFACE),
                                                                                  instance_of(AL, place, P),
                                                                                  planning_level(AL),
                                                                                  step(I).

precondition(AL, ROBO, put(COMP, OBJ, SURFACE), location(ROBO), P, true, I) :- holds(AL, location(SURFACE), P, I),
                                                                               descendant_of(AL, ROBO, COMP),
                                                                               instance_of(AL, armed_robot, ROBO),
                                                                               instance_of(AL, grasper, COMP),
                                                                               instance_of(AL, placeable, OBJ),
                                                                               instance_of(AL, surface, SURFACE),
                                                                               instance_of(AL, place, P),
                                                                               planning_level(AL),
                                                                               step(I).

%% An armed robot cannot put an object on top of another object that already has some other object on top of it
precondition(AL, ROBO, put(COMP, OBJ_1, BLOCK), on(OBJ_2), BLOCK, false, I) :- OBJ_1 != OBJ_2,
                                                                               descendant_of(AL, ROBO, COMP),
                                                                               instance_of(AL, armed_robot, ROBO),
                                                                               instance_of(AL, grasper, COMP),
                                                                               instance_of(AL, placeable, OBJ_1),
                                                                               instance_of(AL, placeable, OBJ_2),
                                                                               instance_of(AL, block, BLOCK),
                                                                               planning_level(AL),
                                                                               step(I).

%% An armed robot can only put an object on a surface when it is grasping that object
precondition(AL, ROBO, put(COMP, OBJ, SURFACE), grasping(ROBO, COMP, OBJ), true, true, I) :- OBJ != SURFACE,
                                                                                             descendant_of(AL, ROBO, COMP),
                                                                                             instance_of(AL, armed_robot, ROBO),
                                                                                             instance_of(AL, grasper, COMP),
                                                                                             instance_of(AL, placeable, OBJ),
                                                                                             instance_of(AL, surface, SURFACE),
                                                                                             planning_level(AL),
                                                                                             step(I).

%% An armed robot cannot put an object on another object if any robot is grasping the other object with any of its graspers
precondition(AL, ROBO_1, put(COMP_1, OBJ_1, OBJ_2), grasping(ROBO_2, COMP_2, OBJ_2), false, true, I) :- OBJ_1 != OBJ_2, COMP_1 != COMP_2,
                                                                                                        descendant_of(AL, ROBO_1, COMP_1),
                                                                                                        descendant_of(AL, ROBO_2, COMP_2),
                                                                                                        instance_of(AL, armed_robot, ROBO_1),
                                                                                                        instance_of(AL, armed_robot, ROBO_2),
                                                                                                        instance_of(AL, grasper, COMP_1),
                                                                                                        instance_of(AL, grasper, COMP_2),
                                                                                                        instance_of(AL, placeable, OBJ_1),
                                                                                                        instance_of(AL, surface, OBJ_2),
                                                                                                        instance_of(AL, graspable, OBJ_2),
                                                                                                        planning_level(AL),
                                                                                                        step(I).

%% An armed robot can only grasp an object with a grasper that is extensible if it is extended
precondition(AL, ROBO, put(COMP, OBJ, SURFACE), configuration(ROBO, COMP), extended, true, I) :- descendant_of(AL, ROBO, COMP),
                                                                                                 instance_of(AL, armed_robot, ROBO),
                                                                                                 instance_of(AL, grasper, COMP),
                                                                                                 instance_of(AL, extensible, COMP),
                                                                                                 instance_of(AL, graspable, OBJ),
                                                                                                 instance_of(AL, surface, SURFACE),
                                                                                                 planning_level(AL),
                                                                                                 AL < reduction_level,
                                                                                                 step(I).

%% An armed robot can only grasp an object with a grasper that is not extensible but has extensible siblings is those siblings are extended
precondition(AL, ROBO, put(COMP_1, OBJ, SURFACE), configuration(ROBO, COMP_2), extended, true, I) :- descendant_of(AL, ROBO, COMP_1),
                                                                                              descendant_of(AL, ROBO, COMP_2),
                                                                                              siblings(AL, COMP_1, COMP_2),
                                                                                              instance_of(AL, armed_robot, ROBO),
                                                                                              instance_of(AL, grasper, COMP_1),
                                                                                              not instance_of(AL, extensible, COMP_1),
                                                                                              instance_of(AL, extensible, COMP_2),
                                                                                              instance_of(AL, graspable, OBJ),
                                                                                              instance_of(AL, surface, SURFACE),
                                                                                              planning_level(AL),
                                                                                              AL < reduction_level,
                                                                                              step(I).

%% An armed robot cannot lift a grasped object that has another object on top of it
precondition(AL, ROBO, lift(COMP, OBJ_1), on(OBJ_2), OBJ_1, false, I) :- OBJ_1 != OBJ_2,
                                                                         descendant_of(AL, ROBO, COMP),
                                                                         instance_of(AL, armed_robot, ROBO),
                                                                         instance_of(AL, grasper, COMP),
                                                                         instance_of(AL, placeable, OBJ_1),
                                                                         instance_of(AL, surface, OBJ_1),
                                                                         instance_of(AL, placeable, OBJ_2),
                                                                         planning_level(AL),
                                                                         step(I).

%% An armed robot can only lift a block that it is grasping
precondition(AL, ROBO, lift(COMP, OBJ), grasping(ROBO, COMP, OBJ), true, true, I) :- OBJ != SURFACE,
                                                                                     descendant_of(AL, ROBO, COMP),
                                                                                     instance_of(AL, armed_robot, ROBO),
                                                                                     instance_of(AL, grasper, COMP),
                                                                                     instance_of(AL, graspable, OBJ),
                                                                                     instance_of(AL, surface, SURFACE),
                                                                                     planning_level(AL),
                                                                                     step(I).

%% An armed robot can only collect an object when it is in the same location as that object
precondition(AL, ROBO, collect(OBJ), location(OBJ), P, true, I) :- holds(AL, location(ROBO), P, I),
                                                                   instance_of(AL, armed_robot, ROBO),
                                                                   instance_of(AL, graspable, OBJ),
                                                                   instance_of(AL, place, P),
                                                                   AL >= redefinition_level,
                                                                   planning_level(AL),
                                                                   step(I).

precondition(AL, ROBO, collect(OBJ), location(ROBO), P, true, I) :- holds(AL, location(OBJ), P, I),
                                                                    instance_of(AL, armed_robot, ROBO),
                                                                    instance_of(AL, graspable, OBJ),
                                                                    instance_of(AL, place, P),
                                                                    AL >= redefinition_level,
                                                                    planning_level(AL),
                                                                    step(I).

% precondition(AL, ROBO, collect(OBJ_1), transporting(ROBO, OBJ_2), false, true, I) :- holds(AL, location(OBJ), P, I),
%                                                                     instance_of(AL, armed_robot, ROBO),
%                                                                     instance_of(AL, graspable, OBJ),
%                                                                     instance_of(AL, place, P),
%                                                                     AL >= redefinition_level,
%                                                                     planning_level(AL),
%                                                                     step(I).

% %% A robot cannot transport more objects than it has manipulator arms
% :- N = #count { OBJ : holds(AL_1, transporting(ROBO, OBJ), true, I),
%                       instance_of(AL_1, graspable, OBJ) },
%    M = #count { ARM : descendant_of(AL_2, ROBO, ARM),
%                       instance_of(AL_2, manipulator_arm, ARM),
%                       abstraction_level(AL_2),
%                       AL_1 >= AL_2 },
%    N >= M - 1, number(N), number(M),
%    instance_of(AL_1, robot, ROBO),
%    AL_1 >= redefinition_level,
%    state_representation_level(AL_1),
%    step(I).

%% An armed robot can only deposit an object when it is transporting that object
precondition(AL, ROBO, deposit(OBJ), transporting(ROBO, OBJ), true, true, I) :- instance_of(AL, armed_robot, ROBO),
                                                                                instance_of(AL, graspable, OBJ),
                                                                                AL >= redefinition_level,
                                                                                planning_level(AL),
                                                                                step(I).

%% An armed robot can only pick up and put down an object on a surface when it is in the same location as both the object and the surface
precondition(AL, ROBO, pick_and_put(OBJ, SURFACE), location(SURFACE), P, true, I) :- holds(AL, location(ROBO), P, I),
                                                                                   instance_of(AL, armed_robot, ROBO),
                                                                                   instance_of(AL, placeable, OBJ),
                                                                                   instance_of(AL, surface, SURFACE),
                                                                                   instance_of(AL, place, P),
                                                                                   planning_level(AL),
                                                                                   step(I).

precondition(AL, ROBO, pick_and_put(OBJ, SURFACE), location(ROBO), P, true, I) :- holds(AL, location(SURFACE), P, I),
                                                                                instance_of(AL, armed_robot, ROBO),
                                                                                instance_of(AL, placeable, OBJ),
                                                                                instance_of(AL, surface, SURFACE),
                                                                                instance_of(AL, place, P),
                                                                                planning_level(AL),
                                                                                step(I).

precondition(AL, ROBO, pick_and_put(OBJ, SURFACE), location(OBJ), P, true, I) :- holds(AL, location(ROBO), P, I),
                                                                               instance_of(AL, armed_robot, ROBO),
                                                                               instance_of(AL, placeable, OBJ),
                                                                               instance_of(AL, surface, SURFACE),
                                                                               instance_of(AL, place, P),
                                                                               planning_level(AL),
                                                                               step(I).

precondition(AL, ROBO, pick_and_put(OBJ, SURFACE), location(ROBO), P, true, I) :- holds(AL, location(OBJ), P, I),
                                                                               instance_of(AL, armed_robot, ROBO),
                                                                               instance_of(AL, placeable, OBJ),
                                                                               instance_of(AL, surface, SURFACE),
                                                                               instance_of(AL, place, P),
                                                                               planning_level(AL),
                                                                               step(I).

%% An armed robot cannot pick up and put an object on a surface if there is another object on top of it
precondition(AL, ROBO, pick_and_put(OBJ_1, SURFACE), on(OBJ_2), OBJ_1, false, I) :- OBJ_1 != OBJ_2,
                                                                                    instance_of(AL, armed_robot, ROBO),
                                                                                    instance_of(AL, placeable, OBJ_1),
                                                                                    instance_of(AL, surface, OBJ_1),
                                                                                    instance_of(AL, surface, SURFACE),
                                                                                    instance_of(AL, placeable, OBJ_2),
                                                                                    planning_level(AL),
                                                                                    step(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% State Validity Constraints
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% A robot cannot grasp two different objects at the same time with the same grasper
:- holds(AL, grasping(ROBO, COMP, OBJ_1), true, I),
   holds(AL, grasping(ROBO, COMP, OBJ_2), true, I),
   OBJ_1 != OBJ_2,
   descendant_of(AL, ROBO, COMP),
   instance_of(AL, robot, ROBO),
   instance_of(AL, grasper, COMP),
   instance_of(AL, graspable, OBJ_1),
   instance_of(AL, graspable, OBJ_2),
   state_representation_level(AL).

%% If a robot is grasping an object with an end effector then that end effector must be aligned with the object
:- holds(AL, grasping(ROBO, END, OBJ), true, I),
   not holds(AL, configuration(ROBO, END), aligned_with(OBJ), I),
   descendant_of(AL, ROBO, END),
   instance_of(AL, robot, ROBO),
   instance_of(AL, manipulator_end, END),
   instance_of(AL, graspable, OBJ),
   state_of(AL, END, aligned_with(OBJ)),
   state_representation_level(AL).

%% A robot cannot be grasping an object that has another object on top of it
:- holds(AL, grasping(ROBO, COMP, OBJ_1), true, I),
   holds(AL, on(OBJ_2), OBJ_1, I),
   descendant_of(AL, ROBO, COMP),
   instance_of(AL, robot, ROBO),
   instance_of(AL, grasper, COMP),
   instance_of(AL, graspable, OBJ_1),
   instance_of(AL, surface, OBJ_1),
   instance_of(AL, placeable, OBJ_2),
   state_representation_level(AL).

%% If any of a robot's end effectors are aligned with an object then that object must share its location
:- holds(AL, configuration(ROBO, END), aligned_with(OBJ), I),
   holds(AL, location(ROBO), P, I),
   not holds(AL, location(OBJ), P, I),
   descendant_of(AL, ROBO, END),
   instance_of(AL, robot, ROBO),
   instance_of(AL, manipulator_end, END),
   instance_of(AL, graspable, OBJ),
   instance_of(AL, place, P),
   state_of(AL, END, aligned_with(OBJ)),
   state_representation_level(AL).

%% If an object is on a surface then that object shares the location of the surface
:- holds(AL, on(OBJ), SURFACE, I),
   holds(AL, location(SURFACE), P, I),
   not holds(AL, location(OBJ), P, I),                                 
   instance_of(AL, place, P),
   instance_of(AL, place, P),
   instance_of(AL, surface, SURFACE),
   instance_of(AL, object, OBJ),
   state_representation_level(AL),
   step(I).

%% A block cannot be on a block that is on nothing
:- holds(AL, on(BLOCK_1), BLOCK_2, I),
   holds(AL, on(BLOCK_2), nothing, I),
   instance_of(AL, block, BLOCK_1),
   instance_of(AL, block, BLOCK_2),
   state_representation_level(AL),
   step(I).

%% Two blocks cannot be on top of the same block
:- holds(AL, on(BLOCK_1), BLOCK_3, I),
   holds(AL, on(BLOCK_2), BLOCK_3, I),
   BLOCK_1 != BLOCK_2,
   instance_of(AL, block, BLOCK_1),
   instance_of(AL, block, BLOCK_2),
   instance_of(AL, block, BLOCK_3),
   state_representation_level(AL),
   step(I).

%% A robot cannot transport more objects than it has manipulator arms
:- N = #count { OBJ : holds(AL_1, transporting(ROBO, OBJ), true, I),
                      instance_of(AL_1, graspable, OBJ) },
   M = #count { ARM : descendant_of(AL_2, ROBO, ARM),
                      instance_of(AL_2, manipulator_arm, ARM),
                      abstraction_level(AL_2),
                      AL_1 >= AL_2 },
   N > M, number(N), number(M),
   instance_of(AL_1, robot, ROBO),
   AL_1 >= redefinition_level,
   state_representation_level(AL_1),
   step(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Fluent Definitions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% A block is the base of a tower if it is either:
%%      - On a table
%%      - On a descenant surface of a table
holds(AL, tower_base(BLOCK), true, I) :- holds(AL, on(BLOCK), TABLE, I),
                                         instance_of(AL, block, BLOCK),
                                         instance_of(AL, table, TABLE),
                                         state_representation_level(AL),
                                         step(I).

holds(AL, tower_base(BLOCK), true, I) :- holds(AL, on(BLOCK), SURFACE, I),
                                         has_ancestors_of_type(AL, SURFACE, table),
                                         instance_of(AL, block, BLOCK),
                                         instance_of(AL, surface, SURFACE),
                                         state_representation_level(AL),
                                         step(I).

%% A block is in a tower if it is either:
%%      - The base of the tower
%%      - On a block that is in the tower
holds(AL, in_tower(BLOCK, BLOCK), true, I) :- holds(AL, tower_base(BLOCK), true, I),
                                              instance_of(AL, block, BLOCK),
                                              state_representation_level(AL),
                                              step(I).

holds(AL, in_tower(BLOCK_1, BLOCK_2), true, I) :- holds(AL, on(BLOCK_2), BLOCK_3, I),
                                                  holds(AL, in_tower(BLOCK_1, BLOCK_3), true, I),
                                                  BLOCK_1 != BLOCK_2,
                                                  instance_of(AL, block, BLOCK_1),
                                                  instance_of(AL, block, BLOCK_2),
                                                  instance_of(AL, block, BLOCK_3),
                                                  state_representation_level(AL),
                                                  step(I).

%% A tower that is not stacked in descending order from top to bottom is unordered
holds(AL, unordered_tower(BASE), true, I) :- holds(AL, on(BLOCK_1), BLOCK_2, I),
                                             holds(AL, in_tower(BASE, BLOCK_1), true, I),
                                             holds(AL, in_tower(BASE, BLOCK_2), true, I),
                                             holds(AL, tower_base(BASE), true, I),
                                             BLOCK_1 = (block, N_1), number(N_1),
                                             BLOCK_2 = (block, N_2), number(N_2),
                                             BLOCK_1 != BLOCK_2, N_1 > N_2,
                                             instance_of(AL, block, BLOCK_1),
                                             instance_of(AL, block, BLOCK_2),
                                             instance_of(AL, block, BASE),
                                             state_representation_level(AL),
                                             step(I).

%% A tower is complete if all the blocks that form it are the same colour and they are stacked in descending order from top to bottom
holds(AL, complete(COLOUR), true, I) :- 3 = #count { BLOCK : holds(AL, in_tower(BASE, BLOCK), true, I),
                                                             is(AL, colour_of(BLOCK, COLOUR)),
                                                             instance_of(AL, block, BLOCK) },
                                        holds(AL, tower_base(BASE), true, I),
                                        holds(AL, unordered_tower(BASE), false, I),
                                        is(AL, colour_of(BASE, COLOUR)),
                                        instance_of(AL, colour, COLOUR),
                                        instance_of(AL, block, BASE),
                                        state_representation_level(AL),
                                        step(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Fluent Abstraction Rules - Rules defining mappings between the state represention between adjacent abstraction levels are defined here
%**% #program abstraction_rules.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% If an object is located in a place that is a descendant of some ancester place then that object is also located in the ancestor place at the current and higher abstractions
holds(AL_1, location(OBJ), P_1, I) :- holds(AL_2, location(OBJ), P_2, I),
                                      fluent(AL_1, physical, inertial, location(OBJ), P_1),
                                      fluent(AL_2, physical, inertial, location(OBJ), P_2),
                                      descendant_of(AL_2, P_1, P_2),
                                      instance_of(AL_1, place, P_1),
                                      instance_of(AL_2, place, P_2),
                                      instance_of(AL_3, object, OBJ),
                                      state_representation_level(AL_1),
                                      state_representation_level(AL_2),
                                      state_representation_level(AL_3),
                                      AL_1 >= AL_2, AL_3 >= AL_2,
                                      AL_3 >= AL_1,
                                      step(I).

%% If an object is located in a place then it is in that place at the current and higher abstractions
holds(AL_1, location(OBJ), P, I) :- holds(AL_2, location(OBJ), P, I),
                                    fluent(AL_1, physical, inertial, location(OBJ), P),
                                    fluent(AL_2, physical, inertial, location(OBJ), P),
                                    instance_of(AL_1, place, P),
                                    instance_of(AL_2, place, P),
                                    instance_of(AL_3, object, OBJ),
                                    state_representation_level(AL_1),
                                    state_representation_level(AL_2),
                                    state_representation_level(AL_3),
                                    AL_1 >= AL_2, AL_3 >= AL_2,
                                    AL_3 >= AL_1,
                                    step(I).

%% If an object has any descendant components then those components share the location of the object at the current and higher abstractions
holds(AL_1, location(COMP), P, I) :- holds(AL_2, location(OBJ), P, I),
                                     fluent(AL_1, physical, inertial, location(COMP), P),
                                     fluent(AL_2, physical, inertial, location(OBJ), P),
                                     descendant_of(AL_2, OBJ, COMP),
                                     instance_of(AL_1, place, P),
                                     instance_of(AL_2, place, P),
                                     instance_of(AL_3, object, OBJ),
                                     instance_of(AL_4, component, COMP),
                                     state_representation_level(AL_1),
                                     state_representation_level(AL_2),
                                     state_representation_level(AL_3),
                                     state_representation_level(AL_4),
                                     AL_1 >= AL_2, AL_3 >= AL_2,
                                     AL_4 >= AL_1,
                                     step(I).

%% If an object has any descendant components then the object shares the location of its components at the current and higher abstractions
holds(AL_1, location(OBJ), P, I) :- holds(AL_2, location(COMP), P, I),
                                    fluent(AL_1, physical, inertial, location(OBJ), P),
                                    fluent(AL_2, physical, inertial, location(COMP), P),
                                    descendant_of(AL_2, OBJ, COMP),
                                    instance_of(AL_1, place, P),
                                    instance_of(AL_2, place, P),
                                    instance_of(AL_3, object, OBJ),
                                    instance_of(AL_4, component, COMP),
                                    state_representation_level(AL_1),
                                    state_representation_level(AL_2),
                                    state_representation_level(AL_3),
                                    state_representation_level(AL_4),
                                    AL_1 >= AL_2, AL_3 >= AL_1,
                                    AL_4 >= AL_2,
                                    step(I).

%% If a robot is grasping an object then that object shares the location of the robot at the current and higher abstractions
holds(AL_1, location(OBJ), P, I) :- holds(AL_2, location(ROBO), P, I),
                                    holds(AL_3, grasping(ROBO, COMP, OBJ), true, I),
                                    fluent(AL_1, physical, inertial, location(OBJ), P),
                                    fluent(AL_2, physical, inertial, location(ROBO), P),
                                    fluent(AL_3, physical, inertial, grasping(ROBO, COMP, OBJ), true),
                                    instance_of(AL_1, place, P),
                                    instance_of(AL_2, place, P),
                                    instance_of(AL_3, graspable, OBJ),
                                    instance_of(AL_4, grasper, COMP),
                                    instance_of(AL_5, robot, ROBO),
                                    state_representation_level(AL_1),
                                    state_representation_level(AL_2),
                                    state_representation_level(AL_3),
                                    state_representation_level(AL_4),
                                    state_representation_level(AL_5),
                                    AL_1 >= AL_2, AL_3 >= AL_1,
                                    AL_4 >= AL_3, AL_5 >= AL_2,
                                    AL_5 >= AL_3,
                                    step(I).

%% If a robot is transporting an object then that object shares the location of the robot at the current and higher abstractions
holds(AL_1, location(OBJ), P, I) :- holds(AL_2, location(ROBO), P, I),
                                    holds(AL_3, transporting(ROBO, OBJ), true, I),
                                    fluent(AL_1, physical, inertial, location(OBJ), P),
                                    fluent(AL_2, physical, inertial, location(ROBO), P),
                                    fluent(AL_3, physical, inertial, transporting(ROBO, OBJ), true),
                                    instance_of(AL_1, place, P),
                                    instance_of(AL_2, place, P),
                                    instance_of(AL_3, graspable, OBJ),
                                    instance_of(AL_4, robot, ROBO),
                                    state_representation_level(AL_1),
                                    state_representation_level(AL_2),
                                    state_representation_level(AL_3),
                                    state_representation_level(AL_4),
                                    AL_1 >= AL_2, AL_3 >= AL_1,
                                    AL_4 >= AL_2, AL_4 >= AL_3,
                                    step(I).

%% If a robot is grasping a graspble object with any of its graspers which is a descendant of some ancestor graspable object then
%% the robot is also grasping the ancestor object with that grasper at the current and higher abstractions
holds(AL_1, grasping(ROBO, COMP, OBJ_1), true, I) :- holds(AL_2, grasping(ROBO, COMP, OBJ_2), true, I),
                                                     fluent(AL_1, physical, inertial, grasping(ROBO, COMP, OBJ_1), true),
                                                     fluent(AL_2, physical, inertial, grasping(ROBO, COMP, OBJ_2), true),
                                                     descendant_of(AL_2, ROBO, COMP),
                                                     descendant_of(AL_2, OBJ_1, OBJ_2),
                                                     instance_of(AL_1, graspable, OBJ_1),
                                                     instance_of(AL_2, graspable, OBJ_2),
                                                     instance_of(AL_3, grasper, COMP),
                                                     instance_of(AL_4, robot, ROBO),
                                                     state_representation_level(AL_1),
                                                     state_representation_level(AL_2),
                                                     state_representation_level(AL_3),
                                                     state_representation_level(AL_4),
                                                     AL_1 >= AL_2, AL_3 >= AL_2,
                                                     AL_3 >= AL_1, AL_4 >= AL_2,
                                                     AL_4 >= AL_1,
                                                     step(I).

%% If a robot is not grasping any graspable objects with a given grasper which are descendants of same ancestor graspable object then
%% the robot is not grasping the ancestor object with that grasper at the current and higher abstractions
holds(AL_1, grasping(ROBO, COMP, OBJ_1), false, I) :- 0 = #count { OBJ_2 : holds(AL_2, grasping(ROBO, COMP, OBJ_2), true, I),
                                                                           fluent(AL_2, physical, inertial, grasping(ROBO, COMP, OBJ_2), true),
                                                                           instance_of(AL_2, graspable, OBJ_2),
                                                                           descendant_of(AL_2, OBJ_1, OBJ_2) },
                                                      fluent(AL_1, physical, inertial, grasping(ROBO, COMP, OBJ_1), false),
                                                      has_descendants_of_type(AL_2, OBJ_1, graspable),
                                                      descendant_of(AL_2, ROBO, COMP),
                                                      instance_of(AL_1, graspable, OBJ_1),
                                                      instance_of(AL_3, grasper, COMP),
                                                      instance_of(AL_4, robot, ROBO),
                                                      state_representation_level(AL_1),
                                                      state_representation_level(AL_2),
                                                      state_representation_level(AL_3),
                                                      state_representation_level(AL_4),
                                                      AL_1 >= AL_2, AL_3 >= AL_2,
                                                      AL_3 >= AL_1, AL_4 >= AL_2,
                                                      AL_4 >= AL_1,
                                                      step(I).

%% If a robot is grasping a graspable object with any of its graspers which is itself a descendant of an ancestor grasper then
%% the robot is also grasping the same object with the ancestor grasper at the current and higher abstractions
holds(AL_1, grasping(ROBO, COMP_1, OBJ), B, I) :- holds(AL_2, grasping(ROBO, COMP_2, OBJ), B, I),
                                                  fluent(AL_1, physical, inertial, grasping(ROBO, COMP_1, OBJ), B),
                                                  fluent(AL_2, physical, inertial, grasping(ROBO, COMP_2, OBJ), B),
                                                  descendant_of(AL_2, ROBO, COMP_1),
                                                  descendant_of(AL_2, ROBO, COMP_2),
                                                  descendant_of(AL_2, COMP_1, COMP_2),
                                                  instance_of(AL_1, graspable, OBJ),
                                                  instance_of(AL_2, graspable, OBJ),
                                                  instance_of(AL_3, grasper, COMP_1),
                                                  instance_of(AL_4, grasper, COMP_2),
                                                  instance_of(AL_5, robot, ROBO),
                                                  state_representation_level(AL_1),
                                                  state_representation_level(AL_2),
                                                  state_representation_level(AL_3),
                                                  state_representation_level(AL_4),
                                                  state_representation_level(AL_5),
                                                  AL_1 >= AL_2, AL_3 >= AL_1,
                                                  AL_4 >= AL_2, AL_5 >= AL_2,
                                                  AL_5 >= AL_1,
                                                  boolean(B),
                                                  step(I).

%% If a robot is grasping a graspable object with any of its graspers then the robot is grasping that object with that grasper at the current and higher abstractions
holds(AL_1, grasping(ROBO, COMP, OBJ), B, I) :- holds(AL_2, grasping(ROBO, COMP, OBJ), B, I),
                                                fluent(AL_1, physical, inertial, grasping(ROBO, COMP, OBJ), B),
                                                fluent(AL_2, physical, inertial, grasping(ROBO, COMP, OBJ), B),
                                                descendant_of(AL_2, ROBO, COMP),
                                                instance_of(AL_1, graspable, OBJ),
                                                instance_of(AL_2, graspable, OBJ),
                                                instance_of(AL_3, grasper, COMP),
                                                instance_of(AL_4, robot, ROBO),
                                                state_representation_level(AL_1),
                                                state_representation_level(AL_2),
                                                state_representation_level(AL_3),
                                                state_representation_level(AL_4),
                                                AL_1 >= AL_2, AL_3 >= AL_2,
                                                AL_3 >= AL_1, AL_4 >= AL_2,
                                                AL_4 >= AL_1,
                                                boolean(B),
                                                step(I).

%% If a robot has configurable descendant components which themselves are ancestors of other configurable descendants which share the same
%% configuration states then the ancestors have the same configuration state as their descendants at the current and higher abstractions
holds(AL_1, configuration(ROBO, COMP_1), STATE, I) :- holds(AL_2, configuration(ROBO, COMP_2), STATE, I),
                                                      fluent(AL_1, physical, inertial, configuration(ROBO, COMP_1), STATE),
                                                      fluent(AL_2, physical, inertial, configuration(ROBO, COMP_2), STATE),
                                                      descendant_of(AL_2, ROBO, COMP_1),
                                                      descendant_of(AL_2, ROBO, COMP_2),
                                                      descendant_of(AL_2, COMP_1, COMP_2),
                                                      state_of(AL_1, COMP_1, STATE),
                                                      state_of(AL_2, COMP_2, STATE),
                                                      instance_of(AL_1, configurable, COMP_1),
                                                      instance_of(AL_2, configurable, COMP_2),
                                                      instance_of(AL_3, robot, ROBO),
                                                      state_representation_level(AL_1),
                                                      state_representation_level(AL_2),
                                                      state_representation_level(AL_3),
                                                      AL_1 >= AL_2, AL_3 >= AL_2,
                                                      AL_3 >= AL_1,
                                                      step(I).

%% If a robot has configurable descendant components then those components have the same configuration state at the current and higher abstractions
holds(AL_1, configuration(ROBO, COMP), STATE, I) :- holds(AL_2, configuration(ROBO, COMP), STATE, I),
                                                    fluent(AL_1, physical, inertial, configuration(ROBO, COMP), STATE),
                                                    fluent(AL_2, physical, inertial, configuration(ROBO, COMP), STATE),
                                                    descendant_of(AL_2, ROBO, COMP),
                                                    state_of(AL_1, COMP, STATE),
                                                    state_of(AL_2, COMP, STATE),
                                                    instance_of(AL_1, configurable, COMP),
                                                    instance_of(AL_2, configurable, COMP),
                                                    instance_of(AL_3, robot, ROBO),
                                                    state_representation_level(AL_1),
                                                    state_representation_level(AL_2),
                                                    state_representation_level(AL_3),
                                                    AL_1 >= AL_2, AL_3 >= AL_2,
                                                    AL_3 >= AL_1,
                                                    step(I).

%% If an object is on a surface that is a descendant of some ancester surface then that object is also on the ancestor surface at the current and higher abstractions
holds(AL_1, on(OBJ), SURFACE_1, I) :- holds(AL_2, on(OBJ), SURFACE_2, I),
                                      fluent(AL_1, physical, inertial, on(OBJ), SURFACE_1),
                                      fluent(AL_2, physical, inertial, on(OBJ), SURFACE_2),
                                      descendant_of(AL_2, SURFACE_1, SURFACE_2),
                                      instance_of(AL_1, surface, SURFACE_1),
                                      instance_of(AL_2, surface, SURFACE_2),
                                      instance_of(AL_3, placeable, OBJ),
                                      state_representation_level(AL_1),
                                      state_representation_level(AL_2),
                                      state_representation_level(AL_3),
                                      AL_1 >= AL_2, AL_3 >= AL_2,
                                      AL_3 >= AL_1,
                                      step(I).

%% If an object is on a surface then it is on that surface at the current and higher abstractions
holds(AL_1, on(OBJ), SURFACE, I) :- holds(AL_2, on(OBJ), SURFACE, I),
                                    fluent(AL_1, physical, inertial, on(OBJ), SURFACE),
                                    fluent(AL_2, physical, inertial, on(OBJ), SURFACE),
                                    instance_of(AL_1, surface, SURFACE),
                                    instance_of(AL_2, surface, SURFACE),
                                    instance_of(AL_3, placeable, OBJ),
                                    state_representation_level(AL_1),
                                    state_representation_level(AL_2),
                                    state_representation_level(AL_3),
                                    AL_1 >= AL_2, AL_3 >= AL_2,
                                    AL_3 >= AL_1,
                                    step(I).

%% If a robot is grasping an object with any of its graspers than it is transporting that object at the current and higher abstractions
holds(AL_1, transporting(ROBO, OBJ), true, I) :- holds(AL_2, grasping(ROBO, COMP, OBJ), true, I),
                                                 fluent(AL_1, physical, inertial, transporting(ROBO, OBJ), true),
                                                 fluent(AL_2, physical, inertial, grasping(ROBO, COMP, OBJ), true),
                                                 descendant_of(AL_2, ROBO, COMP),
                                                 instance_of(AL_1, graspable, OBJ),
                                                 instance_of(AL_2, graspable, OBJ),
                                                 instance_of(AL_3, grasper, COMP),
                                                 instance_of(AL_4, robot, ROBO),
                                                 AL_1 >= redefinition_level,
                                                 state_representation_level(AL_1),
                                                 state_representation_level(AL_2),
                                                 state_representation_level(AL_3),
                                                 state_representation_level(AL_4),
                                                 AL_1 >= AL_2, AL_3 >= AL_2,
                                                 AL_4 >= AL_1, AL_4 >= AL_2,
                                                 step(I).

holds(AL_1, transporting(ROBO, OBJ), false, I) :- N = #count { COMP : holds(AL_2, grasping(ROBO, COMP, OBJ), false, I),
                                                                      fluent(AL_2, physical, inertial, grasping(ROBO, COMP, OBJ), false),
                                                                      descendant_of(AL_2, ROBO, COMP),
                                                                      instance_of(AL_3, grasper, COMP) },
                                                  N = #count { COMP : descendant_of(AL_2, ROBO, COMP),
                                                                      instance_of(AL_2, grasper, COMP) },
                                              fluent(AL_1, physical, inertial, transporting(ROBO, OBJ), false),
                                              has_descendants_of_type(AL_2, ROBO, grasper),
                                              instance_of(AL_1, graspable, OBJ),
                                              instance_of(AL_2, graspable, OBJ),
                                              instance_of(AL_4, robot, ROBO),
                                              AL_1 >= redefinition_level,
                                              state_representation_level(AL_1),
                                              state_representation_level(AL_2),
                                              state_representation_level(AL_3),
                                              state_representation_level(AL_4),
                                              AL_1 >= AL_2, AL_3 >= AL_2,
                                              AL_4 >= AL_1, AL_4 >= AL_2,
                                              step(I).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Static Domain State - The static domain structure is defined here
%**% #program static_state.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Static Definitions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Room Layout
%%
%%      ___________________       ___________________       ___________________
%%     |                   |     |                   |     |                   |
%%     |   starting_room   | <-> |      hallway      | <-> |    puzzle_room    |
%%     |___________________|     |___________________|     |___________________|
%%                                         ^
%%                                _________v_________
%%                               |                   |
%%                               |    store_room     |
%%                               |___________________|
%%

is(1, connected((starting_room, 1), (hallway, 0))).
is(1, connected((store_room, 1), (hallway, 1))).
is(1, connected((puzzle_room, 1), (hallway, 2))).

%% Block colouring
is(AL, colour_of((BLOCK, N), red)) :- instance_of(AL, block, (BLOCK, N)), N <= 3.
is(AL, colour_of((BLOCK, N), yellow)) :- instance_of(AL, block, (BLOCK, N)), N > 3, N <= 6.
is(AL, colour_of((BLOCK, N), blue)) :- instance_of(AL, block, (BLOCK, N)), N > 6, N <= 9.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Static Relations
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Adjacent cells are connected
is(1, connected((A, X_1), (A, X_2))) :- instance_of(1, cell, (A, X_1)),
                                        instance_of(1, cell, (A, X_2)),
                                        X_2 = X_1 + 1.

%% Reversability of cell connections
is(1, connected(C_1, C_2)) :- is(1, connected(C_2, C_1)),
                              instance_of(1, cell, C_1),
                              instance_of(1, cell, C_2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Static Abstraction Rules
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Abstraction rule for places that have descendants
is(AL_1, connected(P_1, P_2)) :- is(AL_2, connected(P_1_C, P_2_C)),
                                 P_1 != P_2,
                                 descendant_of(AL_2, P_1, P_1_C),
                                 descendant_of(AL_2, P_2, P_2_C),
                                 instance_of(AL_1, place, P_1),
                                 instance_of(AL_1, place, P_2),
                                 instance_of(AL_2, place, P_1_C),
                                 instance_of(AL_2, place, P_2_C),
                                 abstraction_level(AL_1),
                                 abstraction_level(AL_2),
                                 AL_1 >= AL_2.

%% Abstraction rules for places that do not have descendants
is(AL_1, connected(P_1, P_2)) :- is(AL_2, connected(P_1, P_2)),
                                 P_1 != P_2,
                                 instance_of(AL_1, place, P_1),
                                 instance_of(AL_1, place, P_2),
                                 instance_of(AL_2, place, P_1),
                                 instance_of(AL_2, place, P_2),
                                 abstraction_level(AL_1),
                                 abstraction_level(AL_2),
                                 AL_1 >= AL_2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Specific initial state
%**% #program initial_state.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% The robot(s) starts in the starting room
holds(1, location(talos), (starting_room, 0), 0).
holds(1, location(bastion), (starting_room, 0), 0).

%% The robot(s) start with nothing in their grasp
holds(AL, grasping(ROBO, COMP, OBJ), false, 0) :- descendant_of(AL, ROBO, COMP),
                                                  instance_of(AL, armed_robot, ROBO),
                                                  instance_of(AL, grasper, COMP),
                                                  instance_of(AL, graspable, OBJ),
                                                  state_representation_level(AL).

%% The robot(s) start with their extensible descendant components retracted
holds(AL, configuration(ROBO, COMP), retracted, 0) :- descendant_of(AL, ROBO, COMP),
                                                      instance_of(AL, robot, ROBO),
                                                      instance_of(AL, extensible, COMP),
                                                      state_representation_level(AL).

%% Each puzzle room has a table in it, the south western corner of puzzle room 1 and the south eastern corner of puzzle room 2
holds(1, location(puzzle_room_table), (puzzle_room, 0), 0).

holds(1, on((block, 1)), puzzle_room_table_right, 0).
holds(1, on((block, 2)), puzzle_room_table_left, 0).
holds(1, on((block, 3)), (block, 1), 0).
holds(1, on((block, 4)), (block, 5), 0).
holds(1, on((block, 5)), (block, 2), 0).

holds(1, location((block, 6)), (store_room, 0), 0).
holds(1, location((block, 7)), (store_room, 0), 0).
holds(1, location((block, 8)), (store_room, 0), 0).
holds(1, location((block, 9)), (store_room, 0), 0).

holds(1, on((block, 6)), nothing, 0).
holds(1, on((block, 7)), nothing, 0).
holds(1, on((block, 8)), nothing, 0).
holds(1, on((block, 9)), nothing, 0).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Goals - The specific goal states the robot(s) must satisfy are defined here
%**% #program goal_state.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% The fluents pertinent to the goal state are the placement of blocks and the completeness of the towers
goal_fluent(AL, complete(COLOUR)) :- instance_of(AL, colour, COLOUR), state_representation_level(AL).
goal_fluent(AL, on((block, 3))) :- state_representation_level(AL).
goal_fluent(AL, on((block, 6))) :- state_representation_level(AL).
goal_fluent(AL, on((block, 9))) :- state_representation_level(AL).

%% The goal is to put block 2 on the left hand side of the table in puzzle room 2 whilst leaving block 1 on the table in puzzle room 1
final_goal(AL, complete(COLOUR), true, true) :- instance_of(AL, colour, COLOUR), state_representation_level(AL).
final_goal(1, on((block, 3)), puzzle_room_table_left, true).
final_goal(1, on((block, 6)), puzzle_room_table_middle, true).
final_goal(1, on((block, 9)), puzzle_room_table_right, true).
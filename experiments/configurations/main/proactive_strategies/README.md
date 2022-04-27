Testing the standard size-bound based proactive problem division strategies.
These are tested only for version 3 of both the small and large problems.

For the division strategy experiments, we have cut down in the number of different configurations, by requiring that the size bound at a lower abstraction level cannot be larger than the size bound at a higher abstraction level.
This means that we don't ever want problems at higher abstraction levels to be smaller than problems at lower abstraction levels.
The intuition simply being that, we should either divide the problem equally as much or more at lower levels as we did at the higher levels, and never less.

Need to decide whether you use the tasking model for the small problem or not, use the results from the modified hierarchies to do this!

The multiple puzzle experiments are then ran on the best performing configurations from these experiments.
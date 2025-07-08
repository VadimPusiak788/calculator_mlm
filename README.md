# MLM Commission Calculator
Algorithmic Approach
Build the hierarchy tree:

Given a list of partners, index by id for fast lookup.
Map each partner’s parent_id to children, building a tree (or forest) structure.
Identify root nodes (partners without parents: parent_id==None).
Validate the tree:

Use DFS with recursion stack tracking to detect cycles.
Check that all nodes are reachable from root(s) to detect orphans.
If cycles or orphans exist, raise an error.

For each root, recursively compute the sum of descendants’ daily profits.
Post-order traversal (process children first, then parent).
For partner P, the sum of descendants’ daily profit is the sum of:
Each child’s daily profit
Their descendants’ daily profit sums (computed recursively)
Commission for P is 5% of this total.
Output:

Commission amounts rounded to 2 decimals.
Output as dictionary mapping partner ID (str) to commission (float).

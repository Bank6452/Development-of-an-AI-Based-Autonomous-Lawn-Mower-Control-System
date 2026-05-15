# Graphify Mandatory Workflow for Antigravity

You MUST follow this protocol for every task involving code modification or architectural questions in this workspace.

## 🚨 Mandatory Steps

### 1. Pre-Implementation: Impact Analysis
- BEFORE modifying any code, run `graphify query` or `graphify path` to understand how the target file/function relates to other components.
- Identify potential side effects across the ROS2/C++/Python/URDF stack.

### 2. Implementation
- Execute the planned changes.

### 3. Post-Implementation: Graph Refresh
- AFTER every significant code change, you MUST run:
  `PYTHONPATH=$HOME/.local/lib/python3.10/site-packages python3 -m graphify update .`
- This ensures the knowledge graph remains a "Source of Truth" for subsequent turns.

### 4. Verification
- Use `graphify explain` or `graphify query` to verify that the new relationships match the intended design.

## 🎯 Goal
To maintain 100% architectural consistency and prevent regression bugs in the autonomous mower's complex multi-stack environment.

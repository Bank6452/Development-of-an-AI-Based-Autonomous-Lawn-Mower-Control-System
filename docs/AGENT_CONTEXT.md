# 🤖 AI Agent Context — Autonomous Mower Project

> **READ THIS FIRST if you are a new AI agent picking up this project.**
> Last Updated: 2026-04-02

---

## What This Project Is

A ROS2 Humble autonomous tracked lawn mower simulation in Gazebo Classic. The primary package is `robot_bridge`. See `docs/README.md` for full architecture.

---

## Current State (as of handoff)

The simulation is **stable and working**. Key areas that are complete:

- ✅ Gazebo simulation with physics, GPS, LiDAR, IMU plugins
- ✅ EKF localization (`ekf_sim.yaml`) with correct REP-103 axis mapping
- ✅ Nav2 navigation (Regulated Pure Pursuit controller)
- ✅ Geofence safety system (velocity gatekeeper via `geofence_enforcer.py`)
- ✅ Zigzag coverage path generation (`lawn_planner.py`)
- ✅ Autonomous path execution (`mow_zigzag.py`)

---

## Critical Architecture Facts

### 1. The Safety Command Pipeline (DO NOT BREAK)

```
Nav2 → /cmd_vel_nav → geofence_enforcer → /cmd_vel_filtered → Gazebo motors
```

- **Nav2's `/cmd_vel` output** is remapped to `/cmd_vel_nav` via `GroupAction + SetRemap` in `navigation.launch.py`
- **`geofence_enforcer.py`** subscribes to `/cmd_vel_nav` and `/cmd_vel_teleop`
- It publishes only to `/cmd_vel_filtered`
- **Gazebo diff_drive plugin** (`mower_gazebo.xacro`) listens on `cmd_vel_filtered` — this is the safety lock

**If `geofence_enforcer` is not running, the robot will not respond to ANY commands.**

### 2. Coordinate Datum — MUST Be Consistent

Both `lawn_planner.py` and `geofence_enforcer.py` compute ENU coordinates from GPS using:
```python
datum_lat = points[0]['lat']  # FIRST recorded point
datum_lon = points[0]['lon']
```
These **must stay identical** or the path and geofence boundary will appear offset in RViz.

### 3. Two Separate EKF Configs

- `config/ekf.yaml` → Real hardware (RealSense IMU mounted sideways: Robot X = IMU Z axis)
- `config/ekf_sim.yaml` → Gazebo (standard REP-103: Robot X = IMU X axis)
- **Never merge them.**

---

## What Still Needs Work

See `docs/STATUS.md` Section "Known Issues" for full details. The highest-priority items are:

1. **`geofence_enforcer` is not auto-started** — must be launched manually (interactive prompt for mode selection)
2. **Teleop needs custom topic** (`/cmd_vel_teleop`) — not the default `/cmd_vel`
3. **Real hardware**: compass (GY-273) causes NaN crashes — needs fix or hardware upgrade

---

## How To Run

```bash
cd ~/ros2_ws
./start_sim.sh
# Then in new terminals:
ros2 run robot_bridge geofence_enforcer  # Pick mode 1
ros2 run robot_bridge lawn_planner --ros-args -p geofence_file:=/home/nhio/ros2_ws/lawn_geofence_sim.yaml
ros2 run robot_bridge mow_zigzag         # Type 'go' to start
```

---

## Key Files To Read

1. `docs/README.md` — Full architecture, data flow, quick start
2. `docs/STATUS.md` — All known issues, architecture decisions, topic reference
3. `src/robot_bridge/robot_bridge/geofence_enforcer.py` — Safety gatekeeper logic
4. `src/robot_bridge/robot_bridge/lawn_planner.py` — Path generation logic
5. `src/robot_bridge/launch/navigation.launch.py` — Critical cmd_vel remapping
6. `src/robot_bridge/config/nav2_params.yaml` — All tuning parameters

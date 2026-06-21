# Robotiq Gripper for Gazebo Classic (ROS 2 Humble)

This repository provides a ROS 2 Humble simulation environment for Robotiq grippers in Gazebo Classic, resolving several initialization, parsing, and rendering issues encountered when using `gazebo_ros2_control`.

## Original Repository

This repository is a modified adaptation of the open-source work by PickNik Robotics.

- **Original Repository:** https://github.com/PickNikRobotics/ros2_robotiq_gripper/tree/humble

All core hardware drivers, original meshes, and baseline URDF structures belong to PickNik Robotics.

<img width="590" height="624" alt="Screenshot from 2026-06-21 14-05-43" src="https://github.com/user-attachments/assets/239dfacd-2d97-46f0-8c52-c1b267a11f32" />

---

## Current Status & Limitations

**This repository is currently configured and tested only with the Robotiq 2F-140 gripper.**

While the 2F-85 and Hand-E files are present in the repository, they have not yet been fully patched for Gazebo Classic simulation and may still exhibit rendering or control issues.

---

## The Challenges & Changes Made

Getting the original packages to run reliably in Gazebo Classic presented several undocumented challenges. If you are building your own ROS 2 robotic simulations, the following modifications were required.

### 1. YAML Parsing Crash (Gazebo Freezing)

#### The Problem

In ROS 2, the parameter override mechanism parses the entire `robot_description` as YAML. If an XML comment inside a `.xacro` file contains a colon (`:`), the YAML parser may fail silently, preventing the controller manager from spawning.

For example:

```xml
<!-- Parent Link: base_link -->
```

can trigger parsing issues.

#### The Fix

Sanitized all `.xacro` files in `robotiq_description` by removing colons from XML comments.

Example:

```xml
<!-- Parent Link base_link -->
```

---

### 2. Meshes Not Loading in Gazebo

#### The Problem

Visual meshes (`.stl` files) failed to render in Gazebo Classic due to package path resolution issues, even though collision geometry and inertial properties loaded correctly.

#### The Fix

Added the following export tag to `package.xml`:

```xml
<export>
  <gazebo_ros gazebo_model_path="${prefix}/.." />
</export>
```

This automatically exposes the package's installed share directory to Gazebo whenever the workspace is sourced.

---

### 3. Controller Manager Failing to Initialize

#### The Problem

Recent ROS 2 distributions require `gazebo_ros2_control` to explicitly know where the robot description is being published. Without this information, the controller manager may fail to initialize.

#### The Fix

Added the following parameters to the `gazebo_ros2_control` plugin block:

```xml
<robot_param>robot_description</robot_param>
<robot_param_node>robot_state_publisher</robot_param_node>
```

This ensures the controller manager can locate and parse the robot description correctly.

---

# Startup Guide:

## Prerequisites

Install the required Gazebo and ROS 2 control packages:

```bash
sudo apt update
sudo apt install \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-ros2-control
```

### Optional (Recommended)

Gazebo Classic may spend several minutes attempting to contact the online model database during startup.

To disable this behavior:

```bash
export GAZEBO_MODEL_DATABASE_URI=""
```

You may add this line to your `.bashrc` if desired.

---

## Build & Launch

Clone this repository into the `src` directory of your ROS 2 workspace.

```bash
cd ~/your_workspace/src
git clone <repository_url>
```

Build only the description package (recommended if you are interested solely in simulation and want to avoid hardware driver dependencies):

```bash
cd ~/your_workspace
colcon build --packages-select robotiq_description --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

Launch Gazebo Classic:

```bash
ros2 launch robotiq_description spawn_gazebo_classic.launch.py
```

---

# Controlling the Gripper

Once Gazebo is running and the `robotiq_gripper_controller` has successfully loaded, you can control the 2F-140 gripper through its action server.

Open a new terminal and source your workspace:

```bash
source ~/your_workspace/install/setup.bash
```

## Open the Gripper

```bash
ros2 action send_goal \
  /robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/GripperCommand \
  "{command: {position: 0.0, max_effort: 50.0}}"
```

## Close the Gripper

> Note: `0.695` is the calibrated closed position for the Robotiq 2F-140 gripper.

```bash
ros2 action send_goal \
  /robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/GripperCommand \
  "{command: {position: 0.695, max_effort: 50.0}}"
```

---

## Acknowledgements

This work is based on the original Robotiq ROS 2 packages developed by PickNik Robotics.

All original meshes, hardware interfaces, and baseline descriptions remain the property of their respective authors.

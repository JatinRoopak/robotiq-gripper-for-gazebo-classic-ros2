import os

import launch
import launch_ros
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    description_pkg_share = launch_ros.substitutions.FindPackageShare(
        package="robotiq_description"
    ).find("robotiq_description")
    gazebo_ros_pkg_share = launch_ros.substitutions.FindPackageShare(
        package="gazebo_ros"
    ).find("gazebo_ros")

    default_model_path = os.path.join(
        description_pkg_share, "urdf", "robotiq_2f_140_gripper.urdf.xacro"
    )

    args = []
    args.append(
        launch.actions.DeclareLaunchArgument(
            name="model",
            default_value=default_model_path,
            description="Absolute path to gripper URDF/xacro file",
        )
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            LaunchConfiguration("model"),
            " ",
            "sim_gazebo:=true",
            " ",
            "use_fake_hardware:=false",
        ]
    )
    robot_description_param = {
        "robot_description": launch_ros.parameter_descriptions.ParameterValue(
            robot_description_content, value_type=str
        )
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg_share, "launch", "gazebo.launch.py")
        )
    )

    robot_state_publisher_node = launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description_param, {"use_sim_time": True}],
    )

    spawn_entity = launch_ros.actions.Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "robotiq_2f_140"],
        output="screen",
    )

    joint_state_broadcaster_spawner = launch_ros.actions.Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robotiq_gripper_controller_spawner = launch_ros.actions.Node(
        package="controller_manager",
        executable="spawner",
        arguments=["robotiq_gripper_controller", "--controller-manager", "/controller_manager"],
    )

    # Give the gazebo_ros2_control plugin a moment to bring up /controller_manager
    # before we try to spawn controllers into it.
    delayed_controllers = TimerAction(
        period=5.0,
        actions=[joint_state_broadcaster_spawner, robotiq_gripper_controller_spawner],
    )

    nodes = [
        gazebo,
        robot_state_publisher_node,
        spawn_entity,
        delayed_controllers,
    ]

    return launch.LaunchDescription(args + nodes)

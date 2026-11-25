import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = FindPackageShare('jetbot_digitaltwin')

    xacro_file = PathJoinSubstitution([pkg, 'urdf', 'jetbot.urdf.xacro'])

    # STL-Teile nutzen, falls alle vorhanden – sonst das eigene Box-Modell
    mesh_dir = os.path.join(get_package_share_directory('jetbot_digitaltwin'), 'meshes')
    links = ['base_link', 'jetson', 'camerastand', 'camera', 'left_wheel', 'right_wheel',
             'left_antenne', 'right_antenne']
    use_mesh = 'true' if all(
        os.path.isfile(os.path.join(mesh_dir, link + '.stl')) for link in links) else 'false'

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' use_mesh:=', use_mesh]), value_type=str)

    rviz_config = PathJoinSubstitution([pkg, 'rviz', 'jetbot.rviz'])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    motor_driver = Node(
        package='jetbot_digitaltwin',
        executable='motor_driver_node.py',
        output='screen',
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
    )

    camera_driver = Node(
        package='jetbot_digitaltwin',
        executable='camera_driver_node.py',
        output='screen',
        parameters=[{'test_mode': True}]
    )

    return LaunchDescription([
        robot_state_publisher,
        motor_driver,
        camera_driver,
        rviz,
    ])
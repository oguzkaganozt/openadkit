"""Launch autoware_launch components with use_sim_time as a global parameter.

Upstream's simulator and map component launches ignore use_sim_time, while
the other components load it with the global parameters. Their nodes then run
on wall time against simulation-time TF and never clear their TF buffers when
a new scenario resets the clock. Usage:

    ros2 launch component.launch.py component:=tier4_simulator_component \
        use_sim_time:=true <component arguments>

A component is a file of autoware_launch's launch/components; a path such as
planning_simulator/perception_simulation names a file under launch/ instead.

Several components, separated by commas, run in this one process and get the
same arguments. With launch_pointcloud_container:=true it starts their shared
pointcloud_container_name once, as autoware.launch.xml does, and the
components load their nodes into it: they then start, fail and restart
together, and a restart never loads a node twice.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import SetParameter


def include(path, arguments):
    # A group keeps each include's own launch configurations out of the next.
    return GroupAction(
        [IncludeLaunchDescription(AnyLaunchDescriptionSource(path), launch_arguments=arguments.items())]
    )


def include_components(context):
    # Command-line arguments reach an include only when passed explicitly.
    arguments = dict(context.launch_configurations)
    components = arguments.pop("component").split(",")
    launch = os.path.join(get_package_share_directory("autoware_launch"), "launch")
    actions = [SetParameter(name="use_sim_time", value=LaunchConfiguration("use_sim_time"))]
    if arguments.get("launch_pointcloud_container") == "true":
        arguments["launch_pointcloud_container"] = "false"
        container = {"use_multithread": "true", "container_name": arguments["pointcloud_container_name"]}
        actions.append(include(os.path.join(launch, "pointcloud_container.launch.py"), container))
    for component in components:
        path = os.path.join(launch, component if "/" in component else os.path.join("components", component))
        actions.append(include(path + ".launch.xml", arguments))
    return actions


def generate_launch_description():
    return LaunchDescription([OpaqueFunction(function=include_components)])

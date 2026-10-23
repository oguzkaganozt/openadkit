# Copyright 2020 Tier IV, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# m2_layout4cam1lidar: TEK lidar (Hesai OT128 360°). Autoware'in concatenate node'u ≥2 topic ister
# ("Only one topic given. Need at least two topics") → tek lidar'da YÜKLENEMEZ. Bunun yerine
# tek cropped bulutu (zaten base_link frame'inde) doğrudan /sensing/lidar/concatenated/pointcloud'a
# RELAY ederiz (topic_tools relay). Downsample/NDT bu topic'i bekler. (Kaybedilen: motion-comp
# concat — tek lidar + düşük hız mapping için önemsiz; crop zaten base_link'e taşıdı.)
import launch
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():
    return launch.LaunchDescription([
        DeclareLaunchArgument("base_frame", default_value="base_link"),
        DeclareLaunchArgument("use_multithread", default_value="False"),
        DeclareLaunchArgument("use_intra_process", default_value="False"),
        DeclareLaunchArgument("use_pointcloud_container", default_value="False"),
        DeclareLaunchArgument("container_name", default_value="pointcloud_container"),
        Node(
            package="topic_tools",
            executable="relay",
            name="concatenate_data_relay",
            output="log",
            parameters=[{
                "input_topic": "/sensing/lidar/top/mirror_cropped/pointcloud_ex",
                "output_topic": "/sensing/lidar/concatenated/pointcloud",
                "type": "sensor_msgs/msg/PointCloud2",
                "reliability": "best_effort",
            }],
        ),
    ])

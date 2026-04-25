#!/usr/bin/env python3
import argparse
import math

import rosbag
import rospy
import sensor_msgs.point_cloud2 as point_cloud2
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header


POINT_FIELDS = [
    PointField("x", 0, PointField.FLOAT32, 1),
    PointField("y", 4, PointField.FLOAT32, 1),
    PointField("z", 8, PointField.FLOAT32, 1),
    PointField("intensity", 16, PointField.FLOAT32, 1),
    PointField("normal_x", 20, PointField.FLOAT32, 1),
    PointField("normal_y", 24, PointField.FLOAT32, 1),
    PointField("normal_z", 28, PointField.FLOAT32, 1),
    PointField("curvature", 32, PointField.FLOAT32, 1),
]


def make_odom(stamp, frame_index):
    msg = Odometry()
    msg.header.stamp = stamp
    msg.header.frame_id = "camera_init"
    msg.child_frame_id = "body"
    msg.pose.pose.orientation.w = 1.0
    msg.pose.pose.position.x = 0.04 * frame_index
    msg.pose.pose.position.y = 0.01 * math.sin(frame_index * 0.2)
    return msg


def make_cloud(stamp, frame_index, points_per_frame):
    header = Header()
    header.stamp = stamp
    header.frame_id = "camera_init"

    rings = 32
    columns = max(1, points_per_frame // rings)
    points = []
    for i in range(points_per_frame):
        ring = i % rings
        column = i // rings
        azimuth = -math.pi + 2.0 * math.pi * ((column + 0.37 * ring) % columns) / columns
        elevation = math.radians(-20.0 + 22.0 * ring / (rings - 1))
        radius = 8.0 + 10.0 * ((i * 1103515245 + frame_index * 12345) & 0xFFFF) / 65535.0
        radius += 0.4 * math.sin(azimuth * 3.0 + frame_index * 0.1)

        cos_elevation = math.cos(elevation)
        x = radius * cos_elevation * math.cos(azimuth)
        y = radius * cos_elevation * math.sin(azimuth)
        z = radius * math.sin(elevation)
        intensity = float(1 + (i % 64))
        curvature = 0.0
        points.append((x, y, z, intensity, 0.0, 0.0, 0.0, curvature))

    cloud = point_cloud2.create_cloud(header, POINT_FIELDS, points)
    cloud.is_dense = True
    return cloud


def main():
    parser = argparse.ArgumentParser(description="Generate a deterministic M-detector benchmark rosbag.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--frames", type=int, default=40)
    parser.add_argument("--points-per-frame", type=int, default=30000)
    parser.add_argument("--frame-duration", type=float, default=0.1)
    parser.add_argument("--points-topic", default="/cloud_registered_body")
    parser.add_argument("--odom-topic", default="/aft_mapped_to_init")
    args = parser.parse_args()

    with rosbag.Bag(args.output, "w") as bag:
        for frame_index in range(args.frames):
            stamp = rospy.Time.from_sec(1.0 + frame_index * args.frame_duration)
            bag.write(args.odom_topic, make_odom(stamp, frame_index), stamp)
            bag.write(args.points_topic, make_cloud(stamp, frame_index, args.points_per_frame), stamp)


if __name__ == "__main__":
    main()

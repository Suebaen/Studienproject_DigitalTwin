#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class CameraNode(Node):

    def __init__(self):
        super().__init__('camera_node')

        # Camera settings
        self.declare_parameter('test_mode', True)
        self.declare_parameter('width', 320)
        self.declare_parameter('height', 240)
        self.declare_parameter('fps', 10)

        self.test_mode = self.get_parameter('test_mode').value
        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value
        self.fps = self.get_parameter('fps').value

        self.publisher = self.create_publisher(
            Image, '/camera/image_raw', 10
        )

        self.camera = None

        if not self.test_mode:
            # Start the real JetBot camera
            from jetbot import Camera

            self.camera = Camera.instance()

        # Publish images based on the specified FPS
        self.timer = self.create_timer(1.0 / self.fps, self.publish_image)

        print("Camera node started")

    def publish_image(self):

        if self.test_mode:
            # Create a red test image
            pixel = [255, 0, 0]
            image_data = bytes(pixel * (self.width * self.height))
            encoding = 'rgb8'

        else:
            # Read the real camera image
            frame = self.camera.value

            if frame is None:
                return

            self.height = frame.shape[0]
            self.width = frame.shape[1]

            image_data = frame.tobytes()
            encoding = 'bgr8'

        # Create the ROS image message
        msg = Image()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_link'

        msg.height = self.height
        msg.width = self.width
        msg.encoding = encoding
        msg.step = self.width * 3
        msg.data = image_data

        self.publisher.publish(msg)


if __name__ == '__main__':

    rclpy.init()
    node = None

    try:
        node = CameraNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            if node.camera is not None:
                node.camera.stop()

            node.destroy_node()

        rclpy.try_shutdown()
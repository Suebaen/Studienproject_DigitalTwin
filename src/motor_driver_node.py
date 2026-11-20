#!/usr/bin/env python3

import rclpy           
from rclpy.node import Node   
from geometry_msgs.msg import Twist, TransformStamped
from sensor_msgs.msg import JointState
import math 
from tf2_ros import TransformBroadcaster 


class MotorDriver(Node):
    def __init__(self):
        super().__init__('motor_driver')                # Nodename
        self.get_logger().info('Motor driver started') 

        self.v = 0.0                                    # forward speed (m/s)
        self.w = 0.0                                    # turning speed (rad/s)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)    # listen on /cmd_vel: (message type, topic name, callback function, queue size)

        self.dt = 0.02                                  # 0.02 s = 50 times per second 
        self.create_timer(self.dt, self.update)

        self.wheel_radius = 0.0336                      # m, vom CAD model
        self.wheel_separation = 0.1183                  # m, centre vom linken Rad und vom rechten  

        self.left_angle = 0.0                           #aktueller Radstand (rad) 
        self.right_angle = 0.0

        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        #der teil berechnet wo der Roboter in RViz ist
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.tf_broadcaster = TransformBroadcaster(self)



    def cmd_cb(self, msg):
        self.v = msg.linear.x         
        self.w = msg.angular.z        

    def update(self): 
        self.get_logger().info(f'timer: v={self.v:.2f} w={self.w:.2f}') #print the current command

        v_left = self.v - self.w *self.wheel_separation / 2
        v_right = self.v + self.w *self.wheel_separation / 2

        self.left_angle += v_left / self.wheel_radius * self.dt
        self.right_angle += v_right / self.wheel_radius * self.dt

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['left_wheel_joint', 'right_wheel_joint']
        msg.position = [self.left_angle, self.right_angle]
        self.joint_pub.publish(msg)

        # robot position in RViz
        self.theta += self.w * self.dt
        self.x += self.v * math.cos(self.theta) * self.dt
        self.y += self.v * math.sin(self.theta) * self.dt

        # sendet position an TF: odom → base_footprint
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = math.sin(self.theta / 2)
        t.transform.rotation.w = math.cos(self.theta / 2)
        self.tf_broadcaster.sendTransform(t)

def main():
    rclpy.init()
    rclpy.spin(MotorDriver())
    rclpy.shutdown()


if __name__ == '__main__':
    main()

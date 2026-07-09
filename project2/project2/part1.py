import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty
import math

class Part1(Node): 
    def __init__(self):
        super().__init__('part1')
        
        #subscriber for odometry
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.subscription

        #publisher for motion (updates angular/linear velocity)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        #publisher to reset odometry
        self.pub_reset = self.create_publisher(Empty, '/commands/reset_odometry', 10)
        
        #timer to update motion (updates angular/linear velocity)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        #instance variables for velocity constants
        self.linear_vel = 0.5
        self.angular_vel = 0.5
        
        #current orientation via odometry
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.angular_pos = 0.0
        
        #target coordinates
        self.target_x = 0.0
        self.target_y = 0.0
        

    def timer_callback(self):
        cmd = Twist()
        
        #calculate angle from current coordinates to target coordinates
        #B = 1 - (arctan((yf-y0)/(xf-x0))
        beta = 1 - math.degree((math.atan((self.target_y - self.y_pos) / (self.target_x - self.x_pos))))     #potential /0 error
        
        cmd.linear.x = self.linear_vel      #constant value
        cmd.angular.z = self.angular_vel * beta   #kB (where k is constant and B is angle from current coordinates to target coordinates)
        self.pub.publish(cmd)
        
        
    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.orientation.z
        w = msg.pose.pose.orientation.w
        siny_cosp = 2 * w * z
        cosy_cosp = 1 - 2 * z * z
        yaw = math.atan2(siny_cosp, cosy_cosp)
        degree = yaw * 180 / math.pi
        #print ('x: %f y: %f Orientation: %f' % (x, y, degree))
        self.x_pos = x
        self.y_pos = y
        self.angular_pos = degree

        
def main(args=None):
    rclpy.init(args=args)
    aNode = Part1()
    try:      
        while True:
            #reset odometry before each move
            aNode.pub_reset.publish(Empty())
            
            move = input("Enter desired coordinates (x, y): ")
            aNode.target_x = int(move.split(" ")[0])
            aNode.target_y = int(move.split(" ")[1])
            rclpy.spin_once(aNode)
        
    except KeyboardInterrupt:
        pass
    finally:
        aNode.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        
if __name__== '__main__':
    main()

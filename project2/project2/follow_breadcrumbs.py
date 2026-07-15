import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty
import math

class FollowBreadcrumbs(Node): 
    def __init__(self):
        super().__init__('follow_breadcrumbs')
        
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
        self.linear_vel = 0.2
        self.angular_vel = 0.5
        
        #current orientation via odometry
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.angular_pos = 0.0
        
        #target coordinates
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_x_list = []
        self.target_y_list = []
        
        self.finished = False
        

    def timer_callback(self):
        cmd = Twist()
        
        #calculate angle from current coordinates to target coordinates
        #B = 90 - (arctan((yf-y0)/(xf-x0))
        beta = (((math.degrees((math.atan2((self.target_y - self.y_pos), (self.target_x - self.x_pos))))))-self.angular_pos)
        #USE ANGULAR POSITION in addition to position IN BETA CALCULATION
        
        dist = math.sqrt((self.target_y - self.y_pos)**2 + (self.target_x - self.x_pos)**2)
        beta = (beta+180)%360 -180

        
        #if robot reached target: stop
        if dist <= 0.05:
            print("arrived")
            #cmd.linear.x = 0.0
            #cmd.angular.z = 0.0
            if len(self.target_x_list) <= 0:
                print("DONE")
                self.linear_vel = 0.0
                self.angular_vel = 0.0
            else:
                self.target_x = self.target_x_list.pop(0)     #set targets to current coordinates
                self.target_y = self.target_y_list.pop(0)
            

        #elif dist <= 0.2:
            #self.angular_vel = self.angular_vel
        else:
            #cmd.linear.x = self.linear_vel      #constant value
            #cmd.angular.z = self.angular_vel * beta   #kB (where k is constant and B is angle from current coordinates to target coordinates)
            self.linear_vel = 0.2
            #self.angular_vel = (0.30085/math.sqrt((self.target_y)**2 + (self.target_x)**2)) * beta
            #if self.
            self.angular_vel = 0.55 * (beta/45)
            
        cmd.linear.x = self.linear_vel      #constant value
        cmd.angular.z = self.angular_vel
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
    aNode = FollowBreadcrumbs()
    try:     
        #reset odometry before each move
        aNode.pub_reset.publish(Empty())
        while True:
        
            #reset targets
            aNode.target_x = 0.0
            aNode.target_y = 0.0
            aNode.target_x_list = []
            aNode.target_y_list = []
            
            #read file and add it's coordinates to target lists
            name = input("Enter file name: ")
            with open(name) as f:
                for x in f:
                    aNode.target_x_list.append(float(x.split(",")[0]))
                    aNode.target_y_list.append(float(x.split(",")[1]))
            print(aNode.target_x_list)
            print("---")
            print(aNode.target_y_list)
                
            spin_bool = len(aNode.target_x_list) > 0
            while spin_bool:    #while there are more coordinates
                aNode.target_x = aNode.target_x_list.pop(0)     #set targets to current coordinates
                aNode.target_y = aNode.target_y_list.pop(0)
                #reset odometry before each move
                aNode.pub_reset.publish(Empty())
                rclpy.spin(aNode)              #robot makes move, then comes back to loop to receive new target
                spin_bool = len(aNode.target_x_list) > 0
        
    except KeyboardInterrupt:
        pass
    finally:
        aNode.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        
if __name__== '__main__':
    main()

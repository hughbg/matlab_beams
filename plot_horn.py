from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
            
   
def plot_horn(params, save_to=None):
    
    def line(start, end, colour="blue"):
        x = [start[0], end[0]]
        y = [start[1], end[1]]
        z = [start[2], end[2]]

        ax.plot3D(x, y, z, colour)

    def rect_around_y_axis(x_len, z_len, y_loc, colour="blue"):
        line((-x_len/2, y_loc, -z_len/2), (-x_len/2, y_loc, z_len/2), colour=colour)
        line((-x_len/2, y_loc, z_len/2), (x_len/2, y_loc, z_len/2), colour=colour)
        line((x_len/2, y_loc, z_len/2), (x_len/2, y_loc, -z_len/2), colour=colour)
        line((-x_len/2, y_loc, -z_len/2), (x_len/2, y_loc, -z_len/2), colour=colour)

    def line_parallel_y_axis(x, z, y_start, length, colour="blue"):
        line((x, y_start, z), (x, y_start+length, z))

    def waveguide(_w2, _h2, y_left, y_right):
        rect_around_y_axis(_w2, _h2, y_left, colour="blue")
        rect_around_y_axis(_w2, _h2, y_right, colour="blue")
        for x in [ -_w2/2, _w2/2 ]:
            for z in [ -_h2/2, _h2/2 ]:
                line_parallel_y_axis(x, z, y_left, y_right-y_left, colour="blue")

    def flare(_w1, _h1, _w2, _h2, y_left, y_right):
        rect_around_y_axis(_w1, _h1, y_right, colour="red")
        for x_dir in [ -1, 1]:
            for z_dir in [ -1, 1]:
                line((x_dir*_w2/2, y_left, z_dir*_h2/2), (x_dir*_w1/2, y_right, z_dir*_h1/2), colour="red")

    def feed(_h2, _l2, _f0, _f1, _h3, _y_start):
        # Where is the 0 of the feed?
        # is the feed offset [ x, y ]? or [y, x]?
        # is the feedwidth in the x or y direction? or both?
        # Ignoring feedwidth and assuming offset is x, y and is in centre of l2

        feed_x = _f0
        feed_y = _y_start+_l2/2+_f1
        line((feed_x, feed_y, -_h2/2), (feed_x, feed_y, -_h2/2+_h3), colour="black")
        
        

    # Convert to lengths, widths etc. (l1, w1, ...) on the diagram at 
    # https://uk.mathworks.com/help/antenna/ref/horn.html
    l1 = params["FlareLength"]
    h1 = params["FlareHeight"]
    w1 = params["FlareWidth"]
    l2 = params["Length"]
    h2 = params["Height"]
    w2 = params["Width"]
    h3 = params["FeedHeight"]
    w3 = params["FeedWidth"]
    f0 = params["FeedOffset0"]
    f1 = params["FeedOffset1"]

    # The midpoint of the horn along the y axis is placed at y=0
    # See https://uk.mathworks.com/help/antenna/ref/horn.html for
    # orientation of axes
    y_start = -(l1+l2)/2       
    #print("y start", y_start)


    max_x_offset = max(max(w1/2, w2/2), f0)
    max_y_offset = max(abs(y_start), y_start+l2/2+f1)
    max_z_offset = max(max(h1/2, h2/2), -h2/2+h3)
    
    max_offset = max(max_x_offset, max(max_y_offset, max_z_offset))


    plt.figure(figsize=(12, 12))
    ax = plt.axes(projection='3d')
    ax.set_aspect('equal', adjustable='box')

    #ax.view_init(10, 20)

    waveguide(w2, h2, y_start, y_start+l2)
    flare(w1, h1, w2, h2, y_start+l2, y_start+l2+l1)
    feed(h2, l2, f0, f1, h3, y_start)
    

    # Make the axes all the same. Should be done better. The point is that
    # the axes have to have the same resolution. If the horn is 10m long
    # and only 2m high then how to make sure 
    ax.set_xlim(-max_offset, max_offset)
    ax.set_ylim(-max_offset, max_offset)
    ax.set_zlim(-max_offset, max_offset)
    
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    if save_to is not None:
        plt.savefig(save_to)
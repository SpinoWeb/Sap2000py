import numpy as np

#from Sap2000py.SapSection import SapSection

def delete_all_frames(SapModel):

    # Get the names of all frame objects
    ret, all_frames, ret = SapModel.FrameObj.GetNameList()
    print("all_frames : ", all_frames)

    # Delete each frame object
    for frame in all_frames:
        SapModel.FrameObj.Delete(frame)

    print("All frames deleted successfully")

class add_cartesian_joints:
    def __init__(self, SapObj, cartesian_coords):
        """
        add joints by cartesian coordinate system
        input cartesian_coords(ndarray)-Nx3 array or Nx2 array in 2D model
        """
        self.__Object = SapObj._Object
        self.__Model = SapObj._Model
        N0 = SapObj.joint_coordinates.shape[0] if 'joint_coordinates' in SapObj.__dict__ else 0
        all_joints = SapObj.joint_coordinates if N0 else np.empty( shape = (0, cartesian_coords.shape[1]) )
        # Add new coords
        N, dim = cartesian_coords.shape
        uniqueN = N
        for i in range(N):
            if (cartesian_coords[i] == all_joints).all(-1).any():
                uniqueN -= 1  # point already exists
                print('coordinates ', cartesian_coords[i], ' duplicates! please check!')
            else:
                if dim == 2:
                    SapObj.Assign.PointObj.AddCartesian(cartesian_coords[i,0], cartesian_coords[i,1])
                if dim == 3:
                    SapObj.Assign.PointObj.AddCartesian(cartesian_coords[i,0], cartesian_coords[i,1], cartesian_coords[i,2])
                all_joints = np.vstack((all_joints, cartesian_coords[i]))
        SapObj.joint_coordinates = all_joints
        print(uniqueN,' Joints Added to the Model!')
        if N != uniqueN : print(N-uniqueN,' joints duplicates! please check!')
        
class add_frame_by_points:
    def __init__(self, SapObj, connectivity_frame):
        """
        add frame elements by connectivity_frame
        input connectivity_frame(ndarray)-Nx2 array

        https://docs.csiamerica.com/help-files/etabs-api-2016/html/3e7421b6-2710-f32a-970e-e7b4b87696b3.htm
        Function AddByPoint ( 
            Point1 As String,
            Point2 As String,
            ByRef Name As String,
            Optional PropName As String = "Default",
            Optional UserName As String = ""
        ) As Integer
        """

        #self.__Object = SapObj._Object
        self.__Model = SapObj._Model

        #print("\nSapObj.__dict__ : ", SapObj.__dict__)
        #print("\nconnectivity_frame : ", connectivity_frame)
        myShape = np.shape(connectivity_frame)
        #print("\nmyShape : ", myShape)

        N0 = SapObj.connectivity_frame.shape[0] if 'connectivity_frame' in SapObj.__dict__ else 0
        #print("\nN0 : ", N0)
        all_connectivity_frame = SapObj.connectivity_frame if N0 else np.empty( shape = (0, myShape[1]) )
        #print("\nall_connectivity_frame : ", all_connectivity_frame)
        # Add new connectivity_frame
        N, dim = myShape
        uniqueN = N
        for i in range(N):
            if (connectivity_frame[i] == all_connectivity_frame).all(-1).any():
                uniqueN -= 1  # element connection already exists
                print('connectivity_frame ', connectivity_frame[i],' duplicates! please check!')
            else:
                JointI, JointJ = connectivity_frame[i]
                #print("JointI, JointJ : ", JointI, JointJ)
                self.__Model.FrameObj.AddByPoint(str(JointI), str(JointJ))
                all_connectivity_frame = np.vstack((all_connectivity_frame, connectivity_frame[i]))
        SapObj.connectivity_frame = all_connectivity_frame

class add_frame_by_coord:
    def __init__(self, SapObj, parameters : dict = {}):
        """
        add frame elements by parameters
        input parameters = {XI, YI, ZI, XJ, YJ, ZJ, Name, PropName, UserName, CSys}
        """
        print("add_frame_by_coord > parameters : ", parameters)

        #self.__Object = SapObj._Object
        self.__Model = SapObj._Model

        #
        XI = parameters["XI"] if "XI" in parameters.__dict__ else 0
        YI = parameters["YI"] if "YI" in parameters.__dict__ else 0
        ZI = parameters["ZI"] if "ZI" in parameters.__dict__ else 0
        XJ = parameters["XJ"] if "XJ" in parameters.__dict__ else 1
        YJ = parameters["YJ"] if "YJ" in parameters.__dict__ else 1
        ZJ = parameters["ZJ"] if "ZJ" in parameters.__dict__ else 1
        Name = parameters["Name"] if "Name" in parameters.__dict__ else ""
        #
        PropName = parameters["PropName"] if "PropName" in parameters.__dict__ else "Default"
        UserName = parameters["UserName"] if "UserName" in parameters.__dict__ else ""
        CSys = parameters["CSys"] if "CSys" in parameters.__dict__ else "Global"

        #
        params = [XI, YI, ZI, XJ, YJ, ZJ, Name, PropName, UserName, CSys]
        #params.append(PropName)
        print("add_frame_by_coord > params : ", params)

        """        
        https://docs.csiamerica.com/help-files/etabs-api-2016/html/af874cd1-c96a-54db-a681-8aa01b659bf0.htm
        Function AddByCoord ( 
            XI As Double,
            YI As Double,
            ZI As Double,
            XJ As Double,
            YJ As Double,
            ZJ As Double,
            ByRef Name As String,
            Optional PropName As String = "Default",
            Optional UserName As String = "",
            Optional CSys As String = "Global"
        ) As Integer
        """
        ret = self.__Model.FrameObj.AddByCoord( *params )
        return ret
    
class create_2d_frame:
    # Creating a 2d frame
    # il modello va settato in 2d altrimenti non fa la modale
    def  __init__(self, SapObj, parameters : dict = {}):
        #print("create_3d_frame > parameters : ", parameters)
        
        #self.__Object = SapObj._Object
        self.__Model = SapObj._Model

        #
        bay_width = parameters["bay_width"] if "bay_width" in parameters else 6
        story_height = parameters["story_height"] if "story_height" in parameters else 3
        num_bays = parameters["num_bays"] if "num_bays" in parameters else 2
        num_stories = parameters["num_stories"] if "num_stories" in parameters else 2
        
        #
        base_points = []

        # Define material and section properties
        self.__Model.PropMaterial.SetMaterial("Concrete", 2)
        self.__Model.PropFrame.SetRectangle("Beam", "Concrete", 0.3, 0.5)
        self.__Model.PropFrame.SetRectangle("Column", "Concrete", 0.5, 0.5)

        # Create columns and beams
        for i in range(num_bays + 1):
            for j in range(num_stories):
                x_coord = i * bay_width
                z_coord = j * story_height
                self.__Model.FrameObj.AddByCoord(x_coord, 0, z_coord, x_coord, 0, z_coord + story_height, "", "Column", f"C{i}{j}")
                if j == 0:
                    base_points.append(f"{x_coord}_0_{z_coord}")

        # Create beams
        for j in range(1, num_stories + 1):
            z_coord = j * story_height
            for i in range(num_bays):
                x_start = i * bay_width
                x_end = (i + 1) * bay_width
                self.__Model.FrameObj.AddByCoord(x_start, 0, z_coord, x_end, 0, z_coord, "", "Beam", f"B{j}{i}")

        # store base points
        SapObj.base_points = base_points
        
        print("2d frame created successfully")
        #return base_points

class create_3d_frame:
    # Creating a 3d frame
    def  __init__(self, SapObj, parameters : dict = {}):
        #print("create_3d_frame > parameters : ", parameters)
        
        self.__Object = SapObj._Object
        self.__Model = SapObj._Model

        #
        NumberStorys = parameters["NumberStorys"] if "NumberStorys" in parameters else 3
        StoryHeight = parameters["StoryHeight"] if "StoryHeight" in parameters else 3
        NumberBaysX = parameters["NumberBaysX"] if "NumberBaysX" in parameters else 4
        BayWidthX = parameters["BayWidthX"] if "BayWidthX" in parameters else 6
        NumberBaysY = parameters["NumberBaysY"] if "NumberBaysY" in parameters else 2
        BayWidthY = parameters["BayWidthY"] if "BayWidthY" in parameters else 4        
        
        #
        #points = []
        base_points = []
        columns = []
        beams_x = []
        beams_y = []

        #
        #delete_all_frames(self.__Model)

        # Define material and section properties
        self.__Model.PropMaterial.SetMaterial("Concrete", 2)
        self.__Model.PropFrame.SetRectangle("Beam", "Concrete", 0.3, 0.5)
        self.__Model.PropFrame.SetRectangle("Column", "Concrete", 0.5, 0.5)

        #pi = 0 # points

        # Create columns and beams
        for xi in range(NumberBaysX + 1):
            x_coord = xi * BayWidthX
            for yi in range(NumberBaysY + 1):
                y_coord = yi * BayWidthY
                for zi in range(NumberStorys):                    
                    z_coord = zi * StoryHeight
                    self.__Model.FrameObj.AddByCoord(x_coord, y_coord, z_coord, x_coord, y_coord, z_coord + StoryHeight, "", "Column", f"C{xi}{yi}{zi}")
                    columns.append(f"C{xi}{yi}{zi}")
                    if zi == 0:
                        Point1 = ""
                        Point2 = ""
                        ret = self.__Model.FrameObj.GetPoints(f"C{xi}{yi}{zi}", Point1, Point2)
                        #print("ret : ", ret)              
                        self.__Model.PointObj.SetRestraint(ret[0], [True, True, True, True, True, True])
                        base_points.append(ret[0])

        # Create beams
        for zi in range(1, NumberStorys + 1):
            z_coord = zi * StoryHeight
            for xi in range(NumberBaysX):
                x_start = xi * BayWidthX
                x_end = (xi + 1) * BayWidthX
                for yi in range(NumberBaysY + 1):
                    y_coord = yi * BayWidthY
                    self.__Model.FrameObj.AddByCoord(x_start, y_coord, z_coord, x_end, y_coord, z_coord, "", "Beam", f"Bx{xi}{yi}{zi}")
                    beams_x.append(f"Bx{xi}{yi}{zi}")
            for yi in range(NumberBaysY):
                y_start = yi * BayWidthY
                y_end = (yi + 1) * BayWidthY
                for xi in range(NumberBaysX + 1):
                    x_coord = xi * BayWidthX
                    self.__Model.FrameObj.AddByCoord(x_coord, y_start, z_coord, x_coord, y_end, z_coord, "", "Beam", f"By{xi}{yi}{zi}")
                    beams_y.append(f"By{xi}{yi}{zi}")

        # storing
        SapObj.base_points = base_points
        SapObj.columns = columns
        SapObj.beams_x = beams_x
        SapObj.beams_y = beams_y
        
        print("3d frame created successfully")
        #return base_points
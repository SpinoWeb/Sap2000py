import numpy as np
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
        """
        self.__Object = SapObj._Object
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

import numpy as np
import math
import pycba as cba

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
        base_points = []
        columns = []
        beams_x = []
        beams_y = []

        # Define material properties
        Cgirder = "C25/30"
        self.__Model.PropMaterial.SetMaterial(Cgirder, 2)
        self.__Model.PropMaterial.SetOConcrete(Cgirder, 
                                               Fc = 25e3, 
                                               IsLightweight = False, 
                                               FcsFactor = 0,
                                               SSType = 1,
                                               SSHysType = 2,
                                               StrainAtFc = 2e-3, 
                                               StrainUltimate = 3.5e-3                                               
                                            )
        """
        Function SetOConcrete ( 
            Name As String,
            Fc As Double,
            IsLightweight As Boolean,
            FcsFactor As Double,
            SSType As Integer,
            SSHysType As Integer,
            StrainAtFc As Double,
            StrainUltimate As Double,
            Optional FrictionAngle As Double = 0,
            Optional DilatationalAngle As Double = 0,
            Optional Temp As Double = 0
        ) As Integer
        """

        # Define section properties
        #self.__Model.PropFrame.SetRectangle("column", Cgirder, 0.3, 0.5)
        self.__Model.PropFrame.SetCircle("column", Cgirder, 0.5)
        """
        Function SetCircle ( 
            Name As String,
            MatProp As String,
            T3 As Double,
            Optional Color As Integer = -1,
            Optional Notes As String = "",
            Optional GUID As String = ""
        ) As Integer
        """        
        
        #self.__Model.PropFrame.SetRectangle("beam_x", Cgirder, 0.3, 0.5)
        self.__Model.PropFrame.SetTee("beam_x", Cgirder, 0.5, 0.5, 0.1, 0.1)
        """
        Function SetTee ( 
            Name As String,
            MatProp As String,
            T3 As Double,
            T2 As Double,
            Tf As Double,
            Tw As Double,
            Optional Color As Integer = -1,
            Optional Notes As String = "",
            Optional GUID As String = ""
        ) As Integer
        """

        #self.__Model.PropFrame.SetRectangle("beam_y", Cgirder, 0.3, 0.4)
        self.__Model.PropFrame.SetSDSection("beam_y", Cgirder)
        """
        Function SetSDSection ( 
            Name As String,
            MatProp As String,
            Optional DesignType As Integer = 0,
            Optional Color As Integer = -1,
            Optional Notes As String = "",
            Optional GUID As String = ""
        ) As Integer
        """

        #add polygon shape to new property
        NumberPoints = 8
        x = [-.3, .3, .4, .3, .2, -.2, -.3, -.4]
        y = [  0,  0, .5, .5, .1,  .1,  .5,  .5]
        r = [0, 0, 0, 0, 0, 0, 0, 0]
        ret = self.__Model.PropFrame.SDShape.SetPolygon("beam_y", "SH1", Cgirder, "Default", NumberPoints, x, y, r, -1, False)

        # loadpatterns
        SapObj.Define.loadpatterns.Add("G1k", myType = 1, SelfWTMultiplier = 1)
        SapObj.Define.loadpatterns.Add("G2k", myType = 3)
        SapObj.Define.loadpatterns.Add("Q1k", myType = 3)
        SapObj.Define.loadpatterns.Add("H", myType = 3)

        # loadcases
        #SapObj.Define.loadcases.StaticLinear.SetCase("H")

        # combos
        comboName = "Fd"
        SapObj.Define.LoadCombo.Add(comboName, comboType = "LinearAdd")
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType="LoadCase", CName = "G1k", SF = 1.3)
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType="LoadCase", CName = "G2k", SF = 1.5)
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType="LoadCase", CName = "Q1k", SF = 1.5)

        # loads
        g2 = 3 * BayWidthY
        q1 = 2 * BayWidthY

        # Create columns and retraints
        for xi in range(NumberBaysX + 1):
            x_coord = xi * BayWidthX
            for yi in range(NumberBaysY + 1):
                y_coord = yi * BayWidthY
                for zi in range(NumberStorys):                    
                    z_coord = zi * StoryHeight
                    name = f"column-{xi}{yi}{zi}"
                    self.__Model.FrameObj.AddByCoord(x_coord, y_coord, z_coord, x_coord, y_coord, z_coord + StoryHeight, "", "column", name)
                    columns.append(name)
                    if zi == 0:
                        Point1 = ""
                        Point2 = ""
                        ret = self.__Model.FrameObj.GetPoints(name, Point1, Point2)
                        #print("ret : ", ret)              
                        self.__Model.PointObj.SetRestraint(ret[0], [True, True, True, True, True, True])
                        base_points.append(ret[0])
                        
                        # displ
                        #self.__Model.PointObj.SetRestraint(ret[1], [True, False, False, False, False, False])
                        #self.__Model.PointObj.SetLoadDispl(ret[1], "H", [0.01, 0, 0, 0, 0, 0]) # GLOBAL
                        # force
                        self.__Model.PointObj.SetLoadForce(ret[1], "H", [100, 0, 0, 0, 0, 0]) # GLOBAL

        # Create beams
        for zi in range(1, NumberStorys + 1):
            z_coord = zi * StoryHeight
            for xi in range(NumberBaysX):
                x_start = xi * BayWidthX
                x_end = (xi + 1) * BayWidthX
                for yi in range(NumberBaysY + 1):
                    y_coord = yi * BayWidthY
                    name = f"beam_x-{xi}{yi}{zi}"
                    self.__Model.FrameObj.AddByCoord(x_start, y_coord, z_coord, x_end, y_coord, z_coord, "", "beam_x", name)
                    beams_x.append(name)                    
                    q = g2 / 2 if yi == 0 or yi == NumberBaysY else g2
                    #print(yi, q)
                    self.__Model.FrameObj.SetLoadDistributed(name, "G2k", 1, 10, 0, 1, q, q)
                    q = q1 / 2 if yi == 0 or yi == NumberBaysY else q1
                    #print(yi, q)
                    self.__Model.FrameObj.SetLoadDistributed(name, "Q1k", 1, 10, 0, 1, q, q)
                    """
                    https://docs.csiamerica.com/help-files/etabs-api-2016/html/9a3832e7-d1eb-a2b6-5f28-679cd0f1cfc2.htm
                    Function SetLoadDistributed ( 
                        Name As String,
                        LoadPat As String,
                        MyType As Integer, // 1: Force per unit length, 2: Moment per unit length
                        Dir As Integer, // 10: Gravity direction (only applies when CSys is Global)
                        Dist1 As Double,
                        Dist2 As Double,
                        Val1 As Double,
                        Val2 As Double,
                        Optional CSys As String = "Global",
                        Optional RelDist As Boolean = true,
                        Optional Replace As Boolean = true,
                        Optional ItemType As eItemType = eItemType.Objects
                    ) As Integer
                    """
            for yi in range(NumberBaysY):
                y_start = yi * BayWidthY
                y_end = (yi + 1) * BayWidthY
                for xi in range(NumberBaysX + 1):
                    x_coord = xi * BayWidthX
                    name = f"beam_y-{xi}{yi}{zi}"
                    self.__Model.FrameObj.AddByCoord(x_coord, y_start, z_coord, x_coord, y_end, z_coord, "", "beam_y", name)
                    beams_y.append(name)

        # storing
        SapObj.base_points = base_points
        SapObj.columns = columns
        SapObj.beams_x = beams_x
        SapObj.beams_y = beams_y
        
        print("3D frame created successfully!")
        """
        return [
            {"name": "base_points", "type": "Point"},
            {"name": "columns", "type": "Frame"},
            {"name": "beams_x", "type": "Frame"},
            {"name": "beams_y", "type": "Frame"}
        ]
        """

class create_grid:
    # Creating a grid
    def __init__(self, SapObj, parameters : dict = {}):
        #print("create_grid > parameters: ", parameters)
        
        self.__Object = SapObj._Object
        self.__Model = SapObj._Model

        # parameters
        Cslab = "C25/30"
        Cgirder = "C28/35"
        girder = "Girder"
        crossbeam = "Crossbeam"
        slab = "slab"

        Materials = parameters["Materials"] if "Materials" in parameters else [
            {
                "Material": Cslab,
                "Type": "Concrete", # 2            
                "Fc": 25e03,
                "E1": 31e06,
                "LtWtConc": "No",
                "SSCurveOpt": "Parametric - Simple", # 1
                "SSHysType": "Takeda", # 2
                "ec2": 2, # StrainAtFc [mm/m]
                "ecu": 3.5, # StrainUltimate [mm/m]
            },
            {
                "Material": Cgirder,
                "Type": "Concrete", # 2            
                "Fc": 28e03,
                "E1": 33e06,
                "LtWtConc": "No",
                "SSCurveOpt": "Parametric - Simple", # 1
                "SSHysType": "Takeda", # 2
                "ec2": 2, # StrainAtFc [mm/m]
                "ecu": 3.5, # StrainUltimate [mm/m]
            }
        ]
        #print("Materials: ", Materials)

        Sections = parameters["Sections"] if "Sections" in parameters else [
            {
                "SectionName": crossbeam,
                "Material": Cgirder,
                "Shape": "Rectangular",
                "t3": 1,
                "t2": .2,
            },
            {
                "SectionName": girder,
                "Material": Cgirder,
                "Shape": "I/Wide Flange",
                "t3": 1.2,
                "t2": .45,
                "tf": .15,
                "tw": .1,
                "t2b": .45,
                "tfb": .15,
                "FilletRadius": 0
            },
            {
                "SectionName": "SDGirder",
                "Material": Cgirder,
                "Shape": "SD Section",
            },
        ]
        #print("Sections: ", Sections)

        Polygons = parameters["Polygons"] if "Polygons" in parameters else [
            {
                "SectionName": "SDGirder",
                "ShapeName": "SDGirder-1",
                "ShapeMat": Cgirder,
                "FillColor": 8421631, #"gray4",
                "XYR": [
                    {"X": -.2, "Y": 0},
                    {"X": .2, "Y": 0},
                    {"X": .2, "Y": .15},
                    {"X": -.2, "Y": .15}
                ]
            },
            {
                "SectionName": "SDGirder",
                "ShapeName": "SDGirder-2",
                "ShapeMat": Cgirder,
                "FillColor": 8421631, #"gray4",
                "XYR": [
                    {"X": -.05, "Y": .15},
                    {"X": .05, "Y": .15},
                    {"X": .05, "Y": 1.},
                    {"X": -.05, "Y": 1.}
                ]
            },
            {
                "SectionName": "SDGirder",
                "ShapeName": "SDGirder-3",
                "ShapeMat": Cgirder,
                "FillColor": 8421631, #"gray4",
                "XYR": [
                    {"X": -.2, "Y": 1.},
                    {"X": .2, "Y": 1.},
                    {"X": .2, "Y": 1.15},
                    {"X": -.2, "Y": 1.15}
                ]
            },
            {
                "SectionName": "SDGirder",
                "ShapeName": "SDGirder-4",
                "ShapeMat": Cslab,
                "FillColor": 8454016, #"gray4",
                "XYR": [
                    {"X": -.75, "Y": 1.15},
                    {"X": .75, "Y": 1.15},
                    {"X": .75, "Y": 1.35},
                    {"X": -.75, "Y": 1.35}
                ]
            }
        ]
        #print("Polygons: ", Polygons)

        AreaSections = parameters["AreaSections"] if "AreaSections" in parameters else [
            {
                "Section": slab,
                "Material": Cslab,
                "Type": "Shell-Thin",
                "Thickness": .2,
                "BendThick": .2,
            },
        ]
        #print("AreaSections: ", AreaSections)

        Grid = parameters["Grid"] if "Grid" in parameters else {
                "GUID": "grd01",
                "GridName": "Grd01",
                "GridAngle": 0,
                "GirdersNumber": 5,
                "GirdersSpacing": 1.5,
                #"GirderIndex": 1,
                "LdX": 4,
                "GridModelType": "Grid", # FEM, Grid
                #"ShowJointsText": False,
                #"ShowBeamsText": False,
                #"ShowShellsText": False,                
                "E1": 31e06,
                "I33": 3125e-06,
                "E1I33": 96875, # 31 * 3125                
            }    
        
        GridFields = parameters["GridFields"] if "GridFields" in parameters else [
            {
                "GridGUID": "grd01",
                "GridFieldGUID": "gfdsx",
                "GridFieldName": "Sx",
                "GirdersLength": 11,
                "GirdersSection": girder,
                "CrossbeamsSection": crossbeam,
                "CrossbeamsNumber": 2,
                "GridFieldSelected": False
            },
            {
                "GridGUID": "grd01",
                "GridFieldGUID": "gfd01",
                "GridFieldName": "Left",
                "GirdersLength": 2.75,
                "GirdersSection": girder,
                "CrossbeamsSection": crossbeam,
                "CrossbeamsNumber": 2,
                "GridFieldSelected": False
            },
            {
                "GridGUID": "grd01",
                "GridFieldGUID": "gfd02",
                "GridFieldName": "Center",
                "GirdersLength": 26,
                "GirdersSection": girder,
                "CrossbeamsSection": crossbeam,
                "CrossbeamsNumber": 6,
                "GridFieldSelected": False
            },
            {
                "GridGUID": "grd01",
                "GridFieldGUID": "gfd03",
                "GridFieldName": "Right",
                "GirdersLength": 2.75,
                "GirdersSection": girder,
                "CrossbeamsSection": crossbeam,
                "CrossbeamsNumber": 2,
                "GridFieldSelected": False
            },
            {
                "GridGUID": "grd01",
                "GridFieldGUID": "gfddx",
                "GridFieldName": "Dx",
                "GirdersLength": 11,
                "GirdersSection": girder,
                "CrossbeamsSection": crossbeam,
                "CrossbeamsNumber": 2,
                "GridFieldSelected": False
            },
        ]
        #print("GridFields: ", GridFields)

        Trucks = parameters["Trucks"] if "Trucks" in parameters else [
            {
                "GUID": "tck01",
                "TruckName": "T12",
                "ShowAxesText": False,
                "Width": 2,
                "Length": 6
            }
        ]
        #print("Trucks: ", Trucks)

        Axes = parameters["Axes"] if "Axes" in parameters else [
            {
                "TruckGUID": "tck01",
                "AxisGUID": "3bf57ed5",
                "AxisName": "New Axis",
                "x": 1,
                "dy": .2,
                "P": 20,
                #
                "AxisSelected": True,                
                "x1": 1,
                "y1": 0,
                "x2": 1,
                "y2": 2,
                "stroke": "FF8282"
            },
            {
                "TruckGUID": "tck01",
                "AxisGUID": "3bf57ed6",
                "AxisName": "New Axis",
                "x": 2,
                "dy": .200,
                "P": 20,
                #
                "AxisSelected": True,                
                "x1": 2,
                "y1": 0,
                "x2": 2,
                "y2": 2,
                "stroke": "FF8282"
            },
            {
                "TruckGUID": "tck01",
                "AxisGUID": "3bf57ed7",
                "AxisName": "New Axis",
                "x": 4,
                "dy": .200,
                "P": 40,
                #
                "AxisSelected": True,                
                "x1": 4,
                "y1": 0,
                "x2": 4,
                "y2": 2,
                "stroke": "FF8282"
            },
            {
                "TruckGUID": "tck01",
                "AxisGUID": "3bf57ed8",
                "AxisName": "New Axis",
                "x": 5,
                "dy": .200,
                "P": 40,
                #
                "AxisSelected": True,
                "x1": 5,
                "y1": 0,
                "x2": 5,
                "y2": 2,
                "stroke": "FF8282"
            }
        ]

        Scenarios = parameters["Scenarios"] if "Scenarios" in parameters else [
            {
                "GridGUID": "grd01",
                "ScenarioGUID": "scn01",
                "ScenarioName": "Scenario 01",
                "ScenarioTrucks": [
                    {
                        "TruckGUID": "tck01",
                        "x": 11+2,
                        "y": 3
                    }
                ]
            },
            {
                "GridGUID": "grd01",
                "ScenarioGUID": "scn02",
                "ScenarioName": "Scenario 02",
                "ScenarioTrucks": [
                    {
                        "TruckGUID": "tck01",
                        "x": 11+2,
                        "y": 3
                    },
                    {
                        "TruckGUID": "tck01",
                        "x": 11+13,
                        "y": 3
                    }
                ]
            }
        ]

        # Define materials
        for Material in Materials:
            #print("Material: ", Material)
            self.__SetMaterial(Material)    
        
        # Define sections
        SectionProperties = {}
        for Section in Sections:
            #print("Section: ", Section)
            SectionName = Section['SectionName']
            polys = [i for i in Polygons if i['SectionName'] == SectionName]
            self.__SetSection(Section, polys)
            ret = self.__Model.PropFrame.GetSectProps(SectionName)
            #print(SectionName, ": ", [ret[i] for i in [0, 5]])
            SectionProperties[SectionName] = {"Area": ret[0], "I33": ret[5]}

            """        
                Function GetSectProps ( 
                    Name As String,
                    ByRef Area As Double,
                    ByRef As2 As Double,
                    ByRef As3 As Double,
                    ByRef Torsion As Double,
                    ByRef I22 As Double,
                    ByRef I33 As Double,
                    ByRef S22 As Double,
                    ByRef S33 As Double,
                    ByRef Z22 As Double,
                    ByRef Z33 As Double,
                    ByRef R22 As Double,
                    ByRef R33 As Double
                ) As Integer
            """
        #print("SectionProperties:\n", SectionProperties)

        # Define area sections
        for AreaSection in AreaSections:
            #print("AreaSection: ", AreaSection)
            self.__SetAreaSection(AreaSection)

        # groups
        base_points = []
        #girders = []
        #crossbeams = []

        # generate model
        #widthOfTheGrid = self.__widthOfTheGrid(Grid)        
        lengthOfTheGrid = self.__lengthOfTheGrid(GridFields)
        #XiList = self.__XiList(Grid, GridFields)
        #print(widthOfTheGrid, lengthOfTheGrid, XiList)

        ScenariosList = [i for i in Scenarios if i['GridGUID'] == Grid['GUID']]
        #print("ScenariosList: ", ScenariosList)

        ActiveTrucksList = self.__ActiveTrucksList(ScenariosList, Trucks, Axes)
        #print("ActiveTrucksList: ", ActiveTrucksList)

        # Elements
        Elements = self.__GetElements(Grid, GridFields, ActiveTrucksList)

        #self.__Model.GridSys.SetGridSys("GridSysA", 1, 1, 0, 0)
        #print(dir(self.__Model.from_param))

        # Grid Lines
        FieldsKeysIncluded = [
                'CoordSys', 'AxisDir', 'GridID', 'XRYZCoord', 'LineType',
                    'LineColor', 'Visible', 'BubbleLoc', 'AllVisible', 'BubbleSize'
            ]    
        data = [
                # Z
                'GLOBAL', 'Z', 'Z0', '0', 'Primary', 'Gray8Dark', 'Yes', 'Start', 'Yes', '2',
            ]
        
        # X
        LdX = Grid['LdX'] if 'LdX' in Grid else 2
        dX = lengthOfTheGrid / LdX
        for i in range(LdX + 1):
            GridID = 'X' + str(i + 1)
            XRYZCoord = str(i * dX).replace('.', ',')
            #print(GridID, " : ", XRYZCoord)
            data = data + ['GLOBAL', 'X', GridID, XRYZCoord, 'Primary', 'Gray8Dark', 'Yes', 'End', 'Yes', '2']

        # Y
        yList = Elements['yList']
        #print("yList: ", yList)
        for i, y in enumerate(yList):
            GridID = 'Y' + str(i + 1)
            XRYZCoord = str(y).replace('.', ',')
            #print(GridID, " : ", XRYZCoord)
            data = data + ['GLOBAL', 'Y', GridID, XRYZCoord, 'Primary', 'Gray4', 'Yes', 'Start', 'Yes', '2']

        NumberRecords = int(len(data) / len(FieldsKeysIncluded))
        TableKey = 'Grid Lines'
        TableVersion = 1
        ret = self.__Model.DatabaseTables.SetTableForEditingArray(TableKey, TableVersion, FieldsKeysIncluded, NumberRecords, data)              
        #print(ret)
        FillImport = True
        ret = self.__Model.DatabaseTables.ApplyEditedTables(FillImport)
        #print(ret)

        # Joints
        Joints = Elements['Joints']
        #print("Joints: ", Joints)
        for i in range(0, len(Joints), 3):
            name = str(int(Joints[i]))
            #name = str(Joints[i])
            #print(i, name, Joints[i + 1], Joints[i + 2])
            self.__Model.PointObj.AddCartesian(Joints[i + 1], Joints[i + 2], 0, name, name)

        # Beams
        Beams = Elements['Beams']
        #print("Beams: ", len(Beams))
        for i in range(0, len(Beams), 5):
            #print(i, Beams[i], Beams[i + 1], Beams[i + 2], Beams[i + 3], Beams[i + 4])
            self.__Model.FrameObj.AddByPoint(Beams[i + 1], Beams[i + 2], Beams[i], Beams[i + 3])
            # https://docs.csiamerica.com/help-files/csibridge/Advanced_tab/Assign/Frame/Frame_Insertion_Point.htm
            self.__Model.FrameObj.SetInsertionPoint(Beams[i], 8, False, True, [0, 0, 0], [0, 0, 0])
        
        # Shells
        Shells = Elements['Shells']
        #print("Shells: ", len(Shells))
        for i in range(0, len(Shells), 5):
            #print(i, Shells[i], Shells[i + 1], Shells[i + 2], Shells[i + 3], Shells[i + 4])
            Point = [Shells[i + 1], Shells[i + 2], Shells[i + 3], Shells[i + 4]]
            self.__Model.AreaObj.AddByPoint(4, Point, Shells[i], "slab")

        JointsWithRestrains = Elements['JointsWithRestrains']
        #print("JointsWithRestrains: ", len(JointsWithRestrains))
        for i in range(0, len(JointsWithRestrains), 1):
            name = str(int(JointsWithRestrains[i]))
            #name = JointsWithRestrains[i]
            self.__Model.PointObj.SetRestraint(name, [True, True, True, True, False, True])
            base_points.append(name)

        groups = Elements['groups']
        #print("groups: ", groups)
        for g in list(groups.keys()):
            gtype = g.split('-')[0]
            ret = SapObj.Scripts.Group.GetElements(g)
            #print(f'{g} : {ret}')
            if len(ret) > 0:
                ret = self.__Model.GroupDef.Delete(g)
                #print(f'{g} : {ret}')
            SapObj.Scripts.Group.AddtoGroup(g, groups[g], gtype)
            #ret = SapObj.Scripts.Group.GetElements(g)
            #print(f'{g} : {ret}')

        # loadpatterns
        SapObj.Define.loadpatterns.Add("G1k", myType = 1, SelfWTMultiplier = 1)
        SapObj.Define.loadpatterns.Add("G2k", myType = 3)
        SapObj.Define.loadpatterns.Add("Q1k", myType = 3)
        #SapObj.Define.loadpatterns.Add("H", myType = 3)

        for Scenario in ScenariosList:
            #print(Scenario)
            SapObj.Define.loadpatterns.Add(Scenario["ScenarioName"], myType = 3)

        # loadcases
        #SapObj.Define.loadcases.StaticLinear.SetCase("H")

        # combos
        comboName = "CV"
        SapObj.Define.LoadCombo.Add(comboName, comboType = "LinearAdd")
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType = "LoadCase", CName = "G1k", SF = 1.3)
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType = "LoadCase", CName = "G2k", SF = 1.5)
        SapObj.Define.LoadCombo.SetCaseList(comboName, CNameType = "LoadCase", CName = "Q1k", SF = 1.5)

        # loads
        JointsWithLoad = Elements['JointsWithLoad']
        #print("JointsWithLoad: ", len(JointsWithLoad), "\n", JointsWithLoad)
        for i in range(0, len(JointsWithLoad), 3):
            #print(i, JointsWithLoad[i], JointsWithLoad[i + 1], JointsWithLoad[i + 2])

            # Replace = False (Default) If it is True, all previous point force loads, if any,
            # assigned to the specified point object(s) in the specified load pattern are deleted 
            # before making the new assignment.
            self.__Model.PointObj.SetLoadForce(JointsWithLoad[i], JointsWithLoad[i + 1], [0, 0, float(JointsWithLoad[i + 2]), 0, 0, 0], Replace = False)

        # storing
        SapObj.base_points = base_points
        #SapObj.girders = girders
        #SapObj.crossbeams = crossbeams
        SapObj.GroupNames = list(groups.keys())
        #
        SapObj.Scenarios = [i['ScenarioName'] for i in ScenariosList]
        SapObj.JointsOfInterest = Elements["JointsOfInterest"]
         
        print("Grid created successfully!")
    
    # set Material
    def __SetMaterial(self, Material = {}):
        #print("Material: ", Material)
        Name = Material["Material"]
        Type = Material["Type"]

        # Concrete
        if Type == "Concrete":
            IsLightweight = False if Material["LtWtConc"] == "No" else True
            # SSType
            match Material["SSCurveOpt"]:
                case 'User defined':
                    SSType = 0
                case 'Parametric - Simple':
                    SSType = 1
                case 'Parametric - Mander':
                    SSType = 2
                case _:
                    SSType = 1   # default
            # SSHysType
            match Material["SSHysType"]:
                case 'Elastic':
                    SSHysType = 0
                case 'Kinematic':
                    SSHysType = 1
                case 'Takeda':
                    SSHysType = 2
                case _:
                    SSHysType = 2   # default

            self.__Model.PropMaterial.SetMaterial(Name, 2)
            self.__Model.PropMaterial.SetOConcrete(Name, 
                                                    Fc = Material["Fc"], 
                                                    IsLightweight = IsLightweight, 
                                                    FcsFactor = 0,
                                                    SSType = SSType,
                                                    SSHysType = SSHysType,
                                                    StrainAtFc = Material["ec2"] * pow(10, -3), 
                                                    StrainUltimate = Material["ecu"] * pow(10, -3),                                               
                                                )

    # set Section
    def __SetSection(self, Section = {}, Polygons = []):
        #print("Section: ", Section, "\nPolygons: ", Polygons)
        SectionName = Section["SectionName"]
        Material = Section["Material"]
        Shape = Section["Shape"]

        t3 = Section["t3"] if "t3" in Section else 0.5
        t2 = Section["t2"] if "t2" in Section else 0.3
        tf = Section["tf"] if "tf" in Section else 0.2
        tw = Section["tw"] if "tw" in Section else 0.2
        t2b = Section["t2b"] if "t2b" in Section else 1.
        tfb = Section["tfb"] if "tfb" in Section else 0.2

        # Rectangular
        if Shape == "Rectangular":
            self.__Model.PropFrame.SetRectangle(SectionName, Material, t3, t2)

        # Tee
        """
        Function SetTee ( 
            Name As String,
            MatProp As String,
            T3 As Double,
            T2 As Double,
            Tf As Double,
            Tw As Double,
            Optional Color As Integer = -1,
            Optional Notes As String = "",
            Optional GUID As String = ""
        ) As Integer
        """
        if Shape == "Tee":
            self.__Model.PropFrame.SetTee(SectionName, Material, t3, t2, tf, tw)

        # I/Wide Flange
        """
        Function SetISection ( 
            Name As String,
            MatProp As String,
            T3 As Double,
            T2 As Double,
            Tf As Double,
            Tw As Double,
            T2b As Double,
            Tfb As Double,
            Optional Color As Integer = -1,
            Optional Notes As String = "",
            Optional GUID As String = ""
        ) As Integer
        """
        if Shape == "I/Wide Flange":
            self.__Model.PropFrame.SetISection(SectionName, Material, t3, t2, tf, tw, t2b, tfb)

        if Shape == "SD Section":
            """
            Function SetSDSection ( 
                Name As String,
                MatProp As String,
                Optional DesignType As Integer = 0,
                Optional Color As Integer = -1,
                Optional Notes As String = "",
                Optional GUID As String = ""
            ) As Integer
            """
            self.__Model.PropFrame.SetSDSection(SectionName, Material)
            for Polygon in Polygons:
                ShapeName = Polygon["ShapeName"]
                ShapeMat = Polygon["ShapeMat"]
                XYR = Polygon["XYR"] if "XYR" in Polygon else []
                Color = Polygon["FillColor"] if "FillColor" in Polygon else -1
                SSOverwrite = ""

                NumberPoints = len(XYR)
                if NumberPoints > 2:
                    X = [i['X'] for i in XYR]
                    Y = [i['Y'] for i in XYR]
                    Radius = [0] * NumberPoints 
                    #print(X, Y, R)
                    self.__Model.PropFrame.SDShape.SetPolygon(
                        SectionName, 
                        ShapeName, 
                        ShapeMat, 
                        SSOverwrite, 
                        NumberPoints,
                        X, Y, Radius,
                        Color, 
                        False, 
                        None
                    )

    # set AreaSection
    def __SetAreaSection(self, AreaSection = {}):
        #print("AreaSection: ", AreaSection)
        Section = AreaSection["Section"]
        Material = AreaSection["Material"]
        Type = AreaSection["Type"]
        MatAng = 0

        # ShellType
        match Type:
            case 'Shell-Thin':
                ShellType = 1
            case 'Shell-Thick':
                ShellType = 2
            case 'Plate-Thin':
                ShellType = 3
            case 'Plate-Thck':
                ShellType = 4
            case 'Membrane':
                ShellType = 5
            case 'Shell layered/nonlinear':
                ShellType = 6
            case _:
                ShellType = 1   # default

        Thickness = AreaSection['Thickness'] if 'Thickness' in AreaSection else .2
        BendThick = AreaSection['BendThick'] if 'BendThick' in AreaSection else Thickness

        self.__Model.PropArea.SetShell(Section, ShellType, Material, MatAng, Thickness, BendThick)

    # width Of the grid
    @staticmethod
    def __widthOfTheGrid(Grid = {}):   

        GirdersNumber = Grid["GirdersNumber"] if "GirdersNumber" in Grid else 2
        GirdersSpacing = Grid["GirdersSpacing"] if "GirdersSpacing" in Grid else 1
        GridAngle = Grid["GridAngle"] if "GridAngle" in Grid else 0
        # GridAngleRad = (GridAngle * np.pi) / 180;

        return (GirdersNumber - 1) * GirdersSpacing
    
    # length of the grid
    @staticmethod
    def __lengthOfTheGrid(GridFields = []):

        if len(GridFields) < 1:
            return 1

        lengthOfTheGrid = 0

        for GridField in GridFields:
            #print(GridField)
            GirdersLength = GridField["GirdersLength"] if "GirdersLength" in GridField else 0

            lengthOfTheGrid = lengthOfTheGrid + GirdersLength

        return lengthOfTheGrid
    
    #abscissa coordinates
    #@staticmethod
    def __XiList(self, Grid = {}, GridFields = []):
        
        if len(GridFields) < 1:
            return []

        LdX = Grid["LdX"] if "LdX" in Grid else 1
        lengthOfTheGrid = self.__lengthOfTheGrid(GridFields)

        XiList = []
        dX = lengthOfTheGrid / LdX
        X = 0

        while X <= lengthOfTheGrid:
            XiList.append(X)
            X = X + dX    

        return XiList

    # Active Trucks List
    def __ActiveTrucksList(self, ScenariosList = [], Trucks = [], Axes = []):
        #print("Trucks: ", Trucks)

        ActiveTrucksList = []
        
        for Scenario in ScenariosList:
            #print(Scenarios)
            ScenarioTrucks = Scenario["ScenarioTrucks"] if "ScenarioTrucks" in Scenario else []
            #print(ScenarioTrucks)

            # get Loads
            for ScenarioTruck in ScenarioTrucks:

                TruckGUID = ScenarioTruck["TruckGUID"] if "TruckGUID" in ScenarioTruck else ""
                x = ScenarioTruck["x"] if "x" in ScenarioTruck else 0
                y = ScenarioTruck["y"] if "y" in ScenarioTruck else y
                #print(TruckGUID, x, y)

                #Truck = [i for i in Trucks if i['GUID'] == TruckGUID]
                #print("Truck: ", Truck)

                for Truck in Trucks:                    
                    if Truck['GUID'] == TruckGUID:
                        #print("Truck: ", Truck)
                        break
                    else:
                        None
                
                Width = Truck["Width"] if "Width" in Truck else 0
                AxesList = [i for i in Axes if i['TruckGUID'] == TruckGUID]
                #print("AxesList: ", AxesList)

                for Axis in AxesList:
                    ActiveTrucksList.append({
                        "ScenarioName": Scenario['ScenarioName'],
                        "X": x + Axis['x'],
                        "Y": y - Axis['dy'],
                        "P": Axis['P'],
                    })
                    ActiveTrucksList.append({
                        "ScenarioName": Scenario['ScenarioName'],
                        "X": x + Axis['x'],
                        "Y": y - Width + Axis['dy'],
                        "P": Axis['P'],
                    })                
        
        return ActiveTrucksList
    
    #
    # C-A method
    #
    def __diList(self, Grid = {}):
        #print("GridJs > diList", Grid);

        GirdersNumber = Grid["GirdersNumber"] if "GirdersNumber" in Grid else 2
        GirdersSpacing = Grid["GirdersSpacing"] if "GirdersSpacing" in Grid else 1
        #GridAngle = Grid["GridAngle"] if "GridAngle" in Grid else 0
        #const GridAngleRad = (GridAngle * Math.PI) / 180;

        widthOfTheGrid = self.__widthOfTheGrid(Grid)
        #const widthOfTheGrid: number = (GirdersNumber - 1) * GirdersSpacing;

        diList = []
        for i in range(GirdersNumber):
            diList.append(i * GirdersSpacing - widthOfTheGrid / 2)

        return diList    

    def __nm(self, Grid = {}):
        #print("GridJs > nm", Grid);

        GirdersNumber = Grid["GirdersNumber"] if "GirdersNumber" in Grid else 2

        diList = self.__diList(Grid)

        n = GirdersNumber
        m = 0

        for i in range(GirdersNumber):
            m = m + 1 * diList[i] * diList[i]

        return { "n": n, "m": m }

    def __riList(self, Grid = {}, e = 0):
        #print("GridJs > riList", Grid, e);

        nm = self.__nm(Grid)
        diList = self.__diList(Grid)

        riList = []
        for i in range(len(diList)):
            riList.append(1 / nm['n'] + (e * diList[i]) / nm['m'])

        #return ki / n + (e * di * ki) / m;
        return riList
    
    # return distributed loads list
    # LoadsList includes loads of a scenario
    def __PiList(self, Grid = {}, LoadsList = []):
        #print("LoadsList: ", LoadsList)

        PiList = []

        #
        # Courbon - Albenga
        #

        widthOfTheGrid = self.__widthOfTheGrid(Grid)
        #diList = self.__diList(Grid)
        #nm = self.__nm(Grid)
        #print(widthOfTheGrid, diList, nm)
        
        for l in LoadsList:
            #print(l)
            Yi = l['Y']
            Pi = l['P']
            ei = Yi - widthOfTheGrid / 2
            ri = self.__riList(Grid, ei)
            #print("ca: ", ri, sum(ri))
            #print(Yi, ei, ri[0], sum(ri))

            #PiList.append({'ScenarioName': l['ScenarioName'], 'X': l['X'], 'P': [Pi * i for i in ri]})
        
        #
        # cba
        #

        GirdersNumber = Grid["GirdersNumber"] if "GirdersNumber" in Grid else 2
        GirdersSpacing = Grid["GirdersSpacing"] if "GirdersSpacing" in Grid else 1

        #L = [i * GirdersSpacing for i in list(range(GirdersNumber))]
        L = [GirdersSpacing] * (GirdersNumber - 1)
        EI = 1.
        R = [-1, 0] * GirdersNumber
        for l in LoadsList:
            #print(l)
            Yi = l['Y']
            Pi = float(l['P'])
            i_span = int(Yi / GirdersSpacing) + 1
            a = Yi - (i_span - 1) * GirdersSpacing
            #print(i_span, Pi, a)
            #print(L, EI, R)
            beam_analysis = cba.BeamAnalysis(L, EI, R)
            beam_analysis.add_pl(i_span, 1, a)
            beam_analysis.analyze()
            ri = beam_analysis.beam_results.R
            #print("cba: ", ri, sum(ri))

            PiList.append({'ScenarioName': l['ScenarioName'], 'X': l['X'], 'P': [Pi * i for i in ri]})

        #print("PiList: ", PiList)
        return PiList

    # Get Elements
    # LoadsList includes loads of all scenarios
    def __GetElements(self, Grid = {}, GridFields = [], LoadsList = []):
        #print("LoadsList: ", LoadsList)

        if len(GridFields) < 1:
            return []
        
        GirdersNumber = Grid["GirdersNumber"] if "GirdersNumber" in Grid else 2
        GirdersSpacing = Grid["GirdersSpacing"] if "GirdersSpacing" in Grid else 1
        GridAngle = Grid["GridAngle"] if "GridAngle" in Grid else 0
        GridModelType = Grid["GridModelType"] if "GridModelType" in Grid else "FEM"
        
        GridAngleRad = math.radians(GridAngle) # (GridAngle * np.pi) / 180
        widthOfTheGrid = self.__widthOfTheGrid(Grid)
        lengthOfTheGrid = self.__lengthOfTheGrid(GridFields)
        #print("lengthOfTheGrid: ", lengthOfTheGrid)

        # add x corresponding to interesting displ points
        xGridList = np.array([])
        LdX = Grid['LdX'] if 'LdX' in Grid else 2
        dX = lengthOfTheGrid / LdX
        for i in range(LdX + 1):            
            xGridList = np.append(xGridList, i * dX)
        #xGridList = np.sort(xGridList)
        #print("xGridList: ", xGridList)

        # ScenarioLoads
        # Grid model / distribuire trasversalmente i carichi sulle travi
        ScenarioLoads = {}
        for i in LoadsList:
            t = ScenarioLoads.setdefault(i['ScenarioName'], [])
            t.append(i)        
        ScenarioNames = list(ScenarioLoads.keys())
        #print("ScenarioNames: ", ScenarioNames)
        #print("ScenarioLoads: ", ScenarioLoads)

        PiList = []
        for ScenarioName in ScenarioNames:
            PiList = PiList + self.__PiList( Grid, ScenarioLoads[ScenarioName])
        #PiList = PiList + self.__PiList( Grid, ScenarioLoads['Scenario 01'])
        #print("PiList:\n", PiList)

        #
        # init
        #
        #Elements = []
        yList = np.array([])
        xList = np.array([])

        # y
        for i in range(GirdersNumber):
            yList = np.append(yList, i * GirdersSpacing)
        np.sort(yList) 
        #print("yList: ", yList)

        yListWithLoads = yList
        #print("yListWithLoads: ", yListWithLoads)
        if GridModelType == "FEM":          
            yListWithLoads = np.concatenate(
                (yListWithLoads, 
                 np.array([-GirdersSpacing / 2, widthOfTheGrid + GirdersSpacing / 2]), # add half spacing on the two sides
                 np.array([i['Y'] for i in LoadsList]) # with Y of loads
                )
            )
        
        #print("yListWithLoads: ", yListWithLoads)
        yListWithLoads = np.unique(yListWithLoads) # remove duplicates, sort
        #print("yListWithLoads: ", yListWithLoads)

        x = 0
        xl = 0
        GridFieldsLimits = np.zeros(shape = (0, 2))
        #print("GridFieldsLimits: ", GridFieldsLimits)
        GridFieldsEnd = np.array([])
        GirdersSectionsList = []
        CrossbeamsSectionsList = []        

        xList = np.append(xList, x)
        #print("xList: ", xList)

        #
        # GridFields
        #
        for GridField in GridFields:
            CrossbeamsNumber = GridField["CrossbeamsNumber"] if "CrossbeamsNumber" in GridField else 1
            CrossbeamsSection = GridField["CrossbeamsSection"] if "CrossbeamsSection" in GridField else None
            GirdersLength = GridField["GirdersLength"] if "GirdersLength" in GridField else 1
            GirdersSection = GridField["GirdersSection"] if "GirdersSection" in GridField else ""

            spacing = GirdersLength / CrossbeamsNumber

            for i in range(CrossbeamsNumber + 1):
                xList = np.append(xList, x + i * spacing)
            #print("xList: ", xList)

            x = xList[- 1]
            #print("x: ", x)

            # GirdersSectionsList
            GirdersSectionsList.append(GirdersSection)

            # CrossbeamsSectionsList
            CrossbeamsSectionsList.append(CrossbeamsSection)

            # GridFieldsLimits
            GridFieldsLimits = np.append(GridFieldsLimits, np.array([[xl, x + i * spacing]]), axis = 0)
            #GridFieldsLimits.push([xl, xl + GirdersLength]);
            xl = xl + GirdersLength
            GridFieldsEnd = np.append(GridFieldsEnd, xl)

        xList = np.sort(xList)

        print("xList: ", xList)
        #print("GirdersSectionsList: ", GirdersSectionsList)
        #print("CrossbeamsSectionsList: ", CrossbeamsSectionsList)
        print("GridFieldsLimits: ", GridFieldsLimits)
        print("GridFieldsEnd: ", GridFieldsEnd)
        #print("xl: ", xl)

        # all x values
        xListWithLoads = np.sort(np.unique(np.concatenate((xList, xGridList, np.array([i['X'] for i in LoadsList])))))
        #print("xListWithLoads: ", xListWithLoads)

        #
        joints = []
        jointsWithLoad = []
        jointsWithRestrains = []
        jointsOfInterest = []
        beams = []
        groups = {}
        
        # questi se evito di conservare oggetti
        Joints = np.array([])
        JointsWithLoad = np.array([])
        JointsWithRestrains = np.array([])
        JointsOfInterest = np.array([])
        Beams = np.array([])
        #Groups = np.array([])
    
        #
        Joint = 0
        Beam = 0
        gf = -1 # GridField index
        g = 0 # group of girders
        cb = 0 # group crossbeams

        #
        JointI = Joint

        # loop along y
        for j, y in enumerate(yListWithLoads):
            if y in yList: # is it a girder ?
                g = g + 1
                framesGroupName = "Frame-G" + str(g)
                framesGroup = np.array([])
                pointsGroupName = "Point-G" + str(g)
                pointsGroup = np.array([])

            # loop along x
            for i, x in enumerate(xListWithLoads):
                # gf
                res = np.where(GridFieldsEnd == x)
                gf = -1 if len(res[0]) < 1 else res[0][0]
                print("gf: ", gf, x)


                # get the GirdersSection
                # let GirdersSection: string | undefined;
                flag = False
                c = -1
                while flag == False and c < len(GridFieldsLimits):
                    c = c + 1
                    flag = x >= GridFieldsLimits[c][0] and x <= GridFieldsLimits[c][1]
                #print("GridJs > getElements", x, " > ", GirdersSection)

                # joints
                Joint = Joint + 1
                #const xr: number = x * Math.cos(GridAngleRad) - y * Math.sin(GridAngleRad);
                xr = x # askew
                yr = x * math.sin(GridAngleRad) + y * math.cos(GridAngleRad)

                joints.append({ "Joint": Joint, "x": xr.item(), "y": yr.item() })
                #joints = np.append(joints, [{ "Joint": Joint, "x": xr, "y": yr }] )
                #Joints.append([Joint, xr, yr])
                Joints = np.append(Joints, [Joint, xr, yr])
                #print("Joints: ", Joints.shape)

                # save loaded joints
                a = []
                if GridModelType == "FEM":
                    # FE model
                    a = [l for l in LoadsList if l['X'] == x and l['Y'] == y]
                else:
                    # Grid model
                    # y == 0 è l'ordinata della trave di riva
                    a = [l for l in PiList if l['X'] == x and y == 0]

                if len(a) > 0:
                    #print(Joint, a)       
                    for ai in a:
                        P = - float(ai['P']) if GridModelType == "FEM" else - float(ai['P'][0]) # P[0] è sulla trave di riva
                        jointsWithLoad.append({'Joint': Joint, 'ScenarioName': ai['ScenarioName'], 'P': P})
                        JointsWithLoad = np.append(JointsWithLoad, [Joint, ai['ScenarioName'], P])

                # save restrained joints                
                if x == xList[0] or x == xList[-1]:                          
                    if len(yList[np.isin(yList, y)]) > 0:
                        jointsWithRestrains.append({ 'Joint': Joint })
                        JointsWithRestrains = np.append(JointsWithRestrains, [Joint])

                # save joints of interest
                if len(yList[np.isin(yList, y)]) > 0 and len(xGridList[np.isin(xGridList, x)]) > 0:
                    jointsOfInterest.append({ 'Joint': str(Joint) })
                    JointsOfInterest = np.append(JointsOfInterest, [str(Joint)])
                
                # girders
                if y in yList and i > 0:
                    Beam = Beam + 1
                    JointJ = Joint
                    beams.append({
                        "Beam": str(Beam), 
                        "JointI": str(JointI),
                        "JointJ": str(JointJ),
                        "AnalSect": GirdersSectionsList[c],
                        "GroupName": framesGroupName,
                    })
                    #Beams.append(Beam, JointI, JointJ, GirdersSectionsList[c], framesGroupName);
                    Beams = np.append(Beams, [str(Beam), str(JointI), str(JointJ), GirdersSectionsList[c], framesGroupName])

                    framesGroup = np.append(framesGroup, [str(Beam)])
                    pointsGroup = np.append(pointsGroup, [str(JointI), str(JointJ)])

                    JointI = JointJ
                else:
                    JointI = Joint
                
            if y in yList: # is it a girder ?
                #print(framesGroupName, framesGroup)
                #print(pointsGroupName, pointsGroup)
                groups[framesGroupName] = np.unique(framesGroup).tolist()
                groups[pointsGroupName] = np.unique(pointsGroup).tolist()        

        # Crossbeams
        # loop along x
        for i, x in enumerate(xListWithLoads):
            if x in xList: # is it a crossbeam ?
                cb = cb + 1
                framesGroupName = "Frame-CB" + str(cb)
                framesGroup = np.array([])
                pointsGroupName = "Point-CB" + str(cb)
                pointsGroup = np.array([])

                # loop along y
            for j, y in enumerate(yListWithLoads):
                JointI = 1 + i + len(xListWithLoads) * (j - 1)
                JointJ = 1 + i + len(xListWithLoads) * (j - 0)
                #print("GridJs > getElements > JointI, JointJ", JointI, JointJ)

                if (x in xList and y > 0 and y <= widthOfTheGrid and JointI > 0 and JointJ > 0):
                    #print("GridJs > getElements > y", y)
                    Beam = Beam + 1
                    beams.append({
                        "Beam": str(Beam),
                        "JointI": str(JointI),
                        "JointJ": str(JointJ),
                        "AnalSect": CrossbeamsSectionsList[c],
                        "GroupName": framesGroupName
                    })
                    Beams = np.append(Beams, [str(Beam), str(JointI), str(JointJ), CrossbeamsSectionsList[c], framesGroupName])

                    framesGroup = np.append(framesGroup, [str(Beam)])
                    pointsGroup = np.append(pointsGroup, [str(JointI), str(JointJ)])

            if x in xList: # is it a crossbeam ?
                #print(framesGroupName, framesGroup)
                #print(pointsGroupName, pointsGroup)
                groups[framesGroupName] = np.unique(framesGroup).tolist()
                groups[pointsGroupName] = np.unique(pointsGroup).tolist()

        # shells        
        shells = [] #np.array([])
        Shells = np.array([]) # se non conservo oggetti
        Shell = 0

        for j in range(1, len(yListWithLoads)):
            y = yListWithLoads[j]
            for i in range(0, len(xListWithLoads) - 1):
                x = xListWithLoads[i]

                JointI = 1 + i + len(xListWithLoads) * (j - 1)
                JointJ = JointI + 1
                JointL = 1 + i + len(xListWithLoads) * (j - 0)
                JointK = JointL + 1

                flag = False
                c = 0
                while flag == False and c < len(GridFieldsLimits):
                    flag = x >= GridFieldsLimits[c][0] and x <= GridFieldsLimits[c][1]
                    #print("GridJs > getElements > between", flag, " > ", c)
                    c = c + 1
                #print("c: ", c)

                Shell = Shell + 1
                shells.append({
                    "Shell": str(Shell),
                    "JointI": str(JointI),
                    "JointJ": str(JointJ),
                    "JointK": str(JointK),
                    "JointL": str(JointL)
                    })
                Shells = np.append(Shells, [str(Shell), str(JointI), str(JointJ), str(JointK), str(JointL)])
        
        # GroupNames
        groups["Point-JointsOfInterest"] = np.unique(JointsOfInterest).tolist()
        GroupNames = list(groups.keys())
        #print("GroupNames: ", GroupNames)

        #print("joints: ", joints)
        #print("jointsWithLoad: ", jointsWithLoad)
        #print("jointsWithRestrains: ", jointsWithRestrains)
        #print("jointsOfInterest: ", jointsOfInterest)      
        #print("Joints: ", Joints)
        #print("JointsWithLoad: ", JointsWithLoad)
        #print("JointsWithRestrains: ", JointsWithRestrains)
        #print("JointsOfInterest: ", JointsOfInterest)   

        #print("beams: ", beams)
        #print("Beams: ", Beams)
        
        #print("shells: ", shells)
        #print("Shells: ", Shells)

        #print("groups: ", groups)
        
        return {
            #"joints": joints,
            #"jointsWithLoad": jointsWithLoad,
            #"jointsWithRestrains": jointsWithRestrains,
            #"jointsOfInterest": jointsOfInterest,
            #"beams": beams,
            #"shells": shells if GridModelType == "FEM" else [],
            "groups" : groups,
            #
            #"GridFieldsLimits": GridFieldsLimits,
            #"xList": xList,
            "yList": yList,
            "GroupNames": GroupNames,
            #
            "Joints": Joints,
            "JointsWithLoad": JointsWithLoad,
            "JointsWithRestrains": JointsWithRestrains,
            "JointsOfInterest": JointsOfInterest,
            "Beams": Beams,
            "Shells": Shells if GridModelType == "FEM" else []
        }
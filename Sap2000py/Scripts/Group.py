
from typing import Literal

class SapGroup:
    def __init__(self,Sapobj):
        """
        Choose cases to run and Analyze model
        """
        self.__Object = Sapobj._Object
        self.__Model = Sapobj._Model
        self._Sapobj = Sapobj

    def GetGroupNames(self):
        """
        Get group names, return NameList.
        """
        NumberNames, NameList, ret = self.__Model.GroupDef.GetNameList()
        return NameList
    
    def Select(self,GroupName):
        """
        Select group by GroupName
        input:
            GroupName(str/list):group name
        """
        # Change type to list
        if type(GroupName) == str:
            GroupName = [GroupName]

        nonameflag = False
        for Name in GroupName:
            if Name not in self.GetGroupNames():
                print('GroupName "{}"doesn\'t exist!'.format(Name))
                nonameflag = True
            else:
                ret = self.__Model.SelectObj.Group(Name)
                #print("ret: ", ret)

        if nonameflag:
            print('You have entered the wrong GroupName, please check in the Caselist below:')
            print(self.GetGroupNames())

    def GetElements(self, GroupName: str):
        """
        Get elements in group
        input:
            GroupName(str|list):group name
        output:
        ElementList(list):
            EleList is like ['Frame:id1','Point:id2']
            element id : type(Point:1,Frame:2,Cable:3,
                        Tendon:4,Area:5,Solid:6,Link:7)
        """
        #print("GroupName : ", GroupName)

        # Change type to list
        if type(GroupName) == str:
            GroupName = [GroupName]
        #print("GroupName : ", GroupName)
        
        nonameflag = False
        ElementList = {}
        for Name in GroupName:
            if Name not in self.GetGroupNames():
                #print('GroupName "{}"doesn\'t exist!'.format(Name))
                nonameflag = True
            else:
                """
                https://docs.csiamerica.com/help-files/etabs-api-2016/html/c55450e0-59ba-3ef8-9d32-a5b1548985fb.htm
                Function GetAssignments ( 
                    Name As String,
                    ByRef NumberItems As Integer,
                    ByRef ObjectType As Integer(),
                    ByRef ObjectName As String()
                ) As Integer
                """
                NumberItems, typelist, elementList, ret = self.__Model.GroupDef.GetAssignments(Name)
                #print("NumberItems, typelist, elementList, ret : ", NumberItems, typelist, elementList, ret)
                
                # Change typelist to typestr_list
                """
                typestr_list = []
                for types in typelist:
                    print("types: ", types)
                    typestr = self._Sapobj.Scripts.lookup(self._Sapobj.ObjDict, types)
                    ###typestr = self._Sapobj.map(lambda x: x.get(types)).take(2)
                    typestr_list.append(typestr)
                
                # combine elementList and typestr_list to a new list
                newlist = [tstr + ':' + ele for tstr, ele in zip(typestr_list, elementList)]
                # update the ElementList
                ElementList.update(dict.fromkeys(newlist))
                """
                ElementList = elementList

        if nonameflag:
            print('You have entered the wrong GroupName, please check in the Caselist below: ')
            print(self.GetGroupNames())
        return list(ElementList)

    def AddtoGroup(self, GroupName: str, namelist, type: Literal['Point','Frame','Cable','Tendon','Area','Solid','Link']):
        """
        Add elements to group
        input:
            GroupName(str): group name
            namelist(list): element id list
            typeStr(str): {'Point':1, 'Frame':2, 'Cable':3, 'Tendon':4, 'Area':5, 'Solid':6, 'Link':7}
        """
        #print(GroupName, namelist, type)

        Objstr = type + 'Obj'
        SapModel = self.__Model

        # check if this group exists
        allgroups = self.GetGroupNames()
        #print("allgroups : ", allgroups)
        if GroupName not in allgroups:
            SapModel.GroupDef.SetGroup(GroupName)

        # Change type to list
        if isinstance(namelist, str):
            namelist = [namelist]

        #print("namelist : ", namelist)
        for name in namelist:
            ret = eval(f'SapModel.{Objstr}.SetGroupAssign(name, GroupName)')
            if ret != 0:
                print(f'Add {Objstr}:{name} to group {GroupName} failed!')

    def RemovefromGroup(self, GroupName: str, dellist, typeStr: str):
        """
        Remove elements from group
        input:
            GroupName(str):group name
            dellist(list):element id list to be deleted
            typeStr(str):{'Point':1,'Frame':2,'Cable':3,
                        'Tendon':4,'Area':5,'Solid':6,'Link':7}
        """
        Objstr = typeStr+'Obj'
        # Delete from existing elements
        EleList = dict.fromkeys(self.GetElements(GroupName))
        for id2del in dellist:
            # key in EleList is like {'Frame:id'}
            elekey = typeStr+':'+id2del
            if elekey in EleList:
                del EleList[elekey]
            else:
                print('The element {} is not in group {}!'.format(elekey,GroupName))
        
        # clear current group
        self.__Model.GroupDef.Clear(GroupName)

        # create the group again
        for ele in EleList.keys():
            typestr = ele.split(':')[0]
            eleid = ele.split(':')[1]
            self.AddtoGroup(GroupName,eleid,typestr)
      
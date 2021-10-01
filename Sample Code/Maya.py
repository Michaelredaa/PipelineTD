#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sample of simple code inside maya.
Documentation: General maya class to automate the repeated functions.
"""

####### WIP #######

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Copyright 2021, Michael Reda"
__status__ = "Beta"

# ---------------------------------
# import libraries
import sys, os
import json, re

from PySide2.QtWidgets import QWidget

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

__python__ = sys.version_info[0]


# ---------------------------------
class Maya(object):
    def __init__(self):
        pass

    @classmethod
    def maya_main_window(self):
        # Return the Maya main window widget as a Python object
        main_window_ptr = omui.MQtUtil.mainWindow()
        if __python__ == 2:
            mayaWin = wrapInstance(long(main_window_ptr), QWidget)
        else:
            mayaWin = wrapInstance(int(main_window_ptr), QWidget)

        return mayaWin

    def maya_version(self):
        """
        To get the current maya version
        :return(int):  The version of maya
        """
        return int(cmds.about(version=True))

    def python_version(self):
        """
        To get the current python version
        :return(int):  The version of python
        """
        return sys.version_info[0]

    def get_cameras(self, shapes=False):
        """
        To get all cameras in scene
        :param shapes (bool):  return the shape node name of transform node name
        :return (list): list of cameras in scene
        """
        all_cameras_shapes = cmds.ls(type="camera")
        all_cameras = [cmds.listRelatives(x, p=1, type="transform")[0] for x in all_cameras_shapes]
        if shapes:
            return all_cameras_shapes
        else:
            return all_cameras

    def nodeShape(self, node, fullpath=False):
        """
        To get the shapes node of given transform node
        :param node (str): the transform node name
        :param fullpath(bool): return the full path name
        :return (list): list of shapes named
        """
        if not cmds.objExists(node):
            om.MGlobal.displayError("The node does not exist: '{}'".formate(node))
            return
        return cmds.listRelatives(node, s=1, fullPath=fullpath)

    def list_children(self, parentNode, node_type="mesh"):
        """
        list all the children nodes under given node
        :param parentNode:
        :param node_type: if "all" will return all the children else with return the specific type only
        :return (list) list of children names
        """
        if not cmds.objExists(parentNode):
            print("The node does not exist: ", parentNode)
            return
        if node_type == "all":
            return cmds.listRelatives(parentNode, ad=1)
        else:
            return cmds.listRelatives(parentNode, ad=1, type=node_type)

    def get_parent_transform(self, node, full_path=False):
        """
        To get the transform node of given node
        :param node(str): the required node name
        :param full_path(bool): return the full path
        :return(list): list of parents names
        """
        _parent = cmds.listRelatives(node, p=1, type="transform")
        if _parent:
            if full_path:
                return cmds.ls(_parent[0], l=1)
            return _parent
        else:
            print('"{}" have not parent'.format(node))
            return False

    def get_current_cam(self, shape=None):
        """
        To get the current camera name
        :param shape (bool): return the shape name
        :return (str): thr name of camera
        """
        current_cam = cmds.lookThru(q=1)
        if shape:
            return cmds.listRelatives(current_cam, s=1, type="camera")[0]
        else:
            return current_cam

    def set_viewport_cam(self, cam):
        """
        To set the current camera of viewport
        :param cam (str): the name of camera
        :return: None
        """
        if cmds.objExists(cam):
            cmds.lookThru(cam)

    def get_projectName(self):
        """
        To get the project name
        :return (str): The project name
        """
        dir = self.get_projectDir()
        if os.path.isdir(dir):
            return dir.split("/")[-2]

    def get_projectDir(self):
        """
        To get the project directory
        :return (str): The project directory
        """
        return cmds.workspace(q=1, rd=1)

    def get_filePath(self):
        """
        To get the maya file path
        :return (str): the maya file path
        """
        return cmds.file(q=1, sn=1)

    def get_timeSlider(self):
        """
        To get the time slider range
        :return (list): list of start and end time
        """
        return [
            cmds.playbackOptions(q=1, min=1),
            cmds.playbackOptions(q=1, max=1)
        ]

    def set_timeSlider(self, time):
        """
        To set the current time slider range
        :param time (list): list of start and end time
        :return: None
        """
        cmds.playbackOptions(e=1, min=time[0])
        cmds.playbackOptions(e=1, max=time[1])

    def playblast(self, path, timeSlider=None, camera=None):

        """
        To make a playblast of viewport
        :param path (str): the output path of movie
        :param timeSlider (list): list of start and end time
        :param camera (str): the playblast camera name
        :return:
        """

        # get cameras
        bu_cam = self.get_current_cam()
        if camera:
            self.set_viewport_cam(camera)
        try:
            if not timeSlider:
                start, end = self.get_timeSlider()
            else:
                start, end = timeSlider
            res = self.get_renderSetting_res()  # (1920, 1080)
            vid_formate = ["qt", "MPEG-4 Video"]

            cmds.playblast(fp=4,
                           clearCache=0,
                           format=vid_formate[0],
                           compression=vid_formate[1],
                           sequenceTime=0,
                           showOrnaments=1,
                           percent=100,
                           filename=path,
                           viewer=0,
                           forceOverwrite=1,
                           quality=100,
                           widthHeight=res,
                           startTime=start,
                           endTime=end
                           )
        except:
            if camera:
                self.set_viewport_cam(bu_cam)

    def get_renderSetting_res(self):
        """
        To get the resolution of rendering
        :return (tuple): tuple of resolution (width *  height)
        """
        return cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")

    def set_renderSetting_res(self, res):
        """
        To set the resolution of rendering
        :param res (list): list of resolution of render (width *  height)
        :return: None
        """

        cmds.setAttr("defaultResolution.width", res[0])
        cmds.setAttr("defaultResolution.height", res[1])

    def get_refs_data(self, _list=None):
        """
        To get all the references data in the maya scene
        :param _list (list): list of required nodes, if None return all scene
        :return: dict of data {}
        """

        """
        for path in data:
            print("Path: ", path)
            for _type in d[path]:
                print("Type: ", _type)
                for node in d[path][_type]:
                    print("nodeName: ", k)
                    for edit in d[path][_type][node]["edits"]:
                        print("Edits: ", edit)
        """
        if not _list:
            _list = cmds.ls(dag=1, l=1)

        data = {}
        for node in _list:
            if cmds.referenceQuery(node, isNodeReferenced=True):
                file_path_ref = cmds.referenceQuery(node, filename=True)
                _type = cmds.nodeType(node)

                if not file_path_ref in data:
                    data[file_path_ref] = {}
                if not _type in data[file_path_ref]:
                    data[file_path_ref][_type] = {}

                if not node in data[file_path_ref][_type]:
                    edits = cmds.referenceQuery(node, editStrings=True)
                    data[file_path_ref][_type][node] = {}

                if not "edits" in data[file_path_ref][_type][node]:
                    data[file_path_ref][_type][node]["edits"] = []
                data[file_path_ref][_type][node]["edits"].extend(edits)

        return data

    def get_abc_paths(self, _list=None):
        """
        get the all scene alembic nodes, return a dictionary
        {
        nodeName: {
                    "abcNode": abcNodeNmae
                    "path": cachePath
        }
        """
        data = {}
        if not _list:
            _list = cmds.ls(dag=True, type="mesh", ni=True, l=True)
        for shape in _list:
            abc = cmds.listConnections(shape, type='AlembicNode')
            if abc is None:
                continue

            cache_path = cmds.getAttr('{0}.{1}'.format(abc[0], 'abc_File'))
            data[shape] = {}
            data[shape]["abcNode"] = abc[0]
            data[shape]["path"] = cache_path
            data[shape]["nodeShape"] = shape

        return data

    def get_ref_paths(self, _list=None):
        """
        To get the references paths in scene
        :param _list (list): list of required nodes, if None return all scene
        :return (list): list of paths
        """

        # if not _list:
        #     _list = cmds.ls(dag=1, l=1)
        #
        # data = []
        # for node in _list:
        #     if cmds.referenceQuery(node, isNodeReferenced=True):
        #         file_path_ref = cmds.referenceQuery(node, filename=True)
        #         _type = cmds.nodeType(node)
        #
        #         if not file_path_ref in data:
        #             data.append(file_path_ref)
        # return data

        if not _list:
            _list = cmds.ls(dag=1, l=1, type="reference")

        data = []
        for node in _list:
            try:
                file_path_ref = cmds.referenceQuery(node, filename=True)
                _type = cmds.nodeType(node)

                if not file_path_ref in data:
                    data.append(file_path_ref)
            except:
                pass
        return data

    def make_reference(self, path):
        """
        To make reference of file inside scene
        :param path: The reference file path
        :return: list of reference nodes
        """
        before = cmds.ls(assemblies=1)
        cmds.file(path, ignoreVersion=1, r=1, gl=1, mergeNamespacesOnClash=False, options="v=0;")
        after = cmds.ls(assemblies=1)
        importedNodes = list(set(after) - set(before))
        return importedNodes

    def writeJSON(self, json_data, json_file):
        """
        To push the data inside json file
        :param json_data (dict): the dictionary of data
        :param json_file: the json file path
        :return: None
        """
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=4)

    def readJSON(self, json_file):
        """
        To read the data from json file
        :param json_file (str): the json file path
        :return: dict of json data
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data
        except:
            pass

    def listFile(self, paths=True):
        """
        To list all texture file nodes paths
        :param paths:
        :return: dict of file information dict{"texs": <nodeName>: <textureName>}
        """
        if paths:
            Pathes_data = {}
            tex_files = cmds.ls(type="file")
            fileNodeData = {}
            for texNode in tex_files:
                tex_path = cmds.getAttr(texNode + ".fileTextureName")
                fileNodeData[texNode] = tex_path

            Pathes_data["texs"] = fileNodeData
            return Pathes_data

    def isChild(self, child, _parent):
        """
        To check if node is child tp another
        :param child (str): the child node name
        :param _parent (str): the parent node name
        :return (bool): if child return true
        """
        children = cmds.listRelatives(_parent, ad=True, f=False)
        if not children:
            return False
        if child in children:
            return True
        else:
            return False

    def parent(self, child, _parent):
        """
        To parent node to another
        :param child (str): the child node name
        :param _parent (str): the parent node name
        :return:
        """
        if not self.isChild(child, _parent):
            cmds.parent(child, _parent)

    def delete_unknown(self):
        """
        To delete unknown nodes
        :return:
        """
        unknownNodes = cmds.ls(type="unknown")
        unknownNodes += cmds.ls(type="unknownDag")
        for item in unknownNodes:
            if cmds.objExists(item):
                print(item)
                cmds.lockNode(item, lock=False)
                cmds.delete(item)

    def get_triangle_plan(self, poinsList=None):
        """
        Create a plan in between the more than 3 points, and make the plan flexiable with the objects
        """
        if not poinsList:
            poinsList = cmds.ls(sl=1)
        if len(poinsList) < 3:
            print("You must select at least 3 points")
            return

        postions = []
        for obj in poinsList:
            postions.append(cmds.xform(obj, q=1, ws=1, t=1))

        plan, plan_his = cmds.polyCreateFacet(ch=1, tx=1, p=postions, n="triangle")
        vertcies = cmds.ls(plan + ".vtx[*]", fl=1)

        for i, obj in enumerate(poinsList):
            dcm = cmds.createNode("decomposeMatrix", n=obj + "_dcm")
            cmds.connectAttr(obj + ".worldMatrix[0]", dcm + ".inputMatrix")
            cmds.connectAttr(dcm + ".outputTranslate", "{}.vertices[{}]".format(plan_his, i))

        cmds.select(plan_his)
        cmds.setAttr(plan_his + ".nodeState", 0)

    def get_abc_timerange(self, node):
        """
        to get the time range of alembic cache
        :param node: the cache node or alembic node
        :return: list of time range
        """

        abctimeRange = []
        frames_attrs = [".startFrame", ".endFrame"]
        if cmds.nodeType(node) == 'AlembicNode':
            abcNode = node
        else:
            abcNode = cmds.listConnections(node, type='AlembicNode')
            if abcNode:
                abcNode = abcNode[0]
            else:
                abcNode = cmds.listConnections(self.get_parent_transform(node), type='AlembicNode')
                if abcNode:
                    abcNode = abcNode[0]
                else:
                    return False

        for attr in frames_attrs:
            abctimeRange.append(round(cmds.getAttr(abcNode + attr)))
        return abctimeRange

    def importAbc(self, abc_path, ref=False, prfx="_"):
        """
        Import or reference alembic file
        :param abc_path: the .abc path
        :param ref: if you want to enter the alembic as reference
        :param prfx: the prifix in case of reference
        :return:
        """
        self.load_plugin("AbcImport")
        if os.path.isfile(abc_path):
            before = cmds.ls(assemblies=1)
            if ref:
                cmds.file(abc_path, r=1, type="Alembic", ignoreVersion=1, gl=1, rpr=prfx)
            else:
                cmds.AbcImport(abc_path, mode='import', fitTimeRange=1)
            after = cmds.ls(assemblies=1)
            importedNodes = list(set(after) - set(before))
            return importedNodes

    def load_plugin(self, pluginName):
        """
        Making sure if the plugin is loaded
        :param pluginName:
        :return:
        """
        if not cmds.pluginInfo(pluginName, q=True, loaded=True):
            cmds.loadPlugin(pluginName)

    def get_keyframes_range(self, node):
        """
        Get the start and the end keyframe from object, if object havent keyframes return empty list
        :param node: node with animation
        :return:list of the start and end keyframes
        """
        try:
            keyframes = list(set(cmds.keyframe(node, query=True, tc=1)))
            start = min(keyframes)
            end = max(keyframes)
            return start, end
        except:
            return []

    def has_animation(self, node, attr):
        """
        check if a node has animation on certain attribute
        :param node:
        :param attr:
        :return:
        """
        if cmds.keyframe(node, attribute=attr, q=True, tc=True):
            return True
        else:
            return False

    def list_dag_geos(self, nodes, shape=True, fullPtah=True):
        """
        get a list of all visiable dag geometry
        :param nodes: list of the selected node
        :param shape: list all shapes (mesh nodes), if False get the geometry
        :param shape: use full path dag of object
        :return: list of geos
        """
        geo_list = []
        for node in nodes:
            all_hierarchy = cmds.ls(node, dag=1, l=fullPtah, type="mesh")
            for child in all_hierarchy:
                flag = True
                if (not cmds.getAttr(child + ".intermediateObject")) and cmds.objectType(child) == 'mesh':
                    fullpath_node = cmds.ls(child, l=1)[0]
                    for item in fullpath_node.split("|")[1:]:
                        if not cmds.getAttr(item + ".visibility"):
                            flag = False
                            continue
                    if flag:
                        # print("child: ", child)
                        if shape:
                            geo_list.append(child)
                        else:
                            geo_list.append(cmds.listRelatives(child, p=True, s=shape, f=fullPtah)[0])

        if geo_list == []:
            cmds.confirmDialog(title="Warning", message="Select at least one object!", b="ok")
            om.MGlobal.displayWarning("You should select at least one geometry")
        return geo_list

    def ck_parents_vis(self, nodeFn):
        """
        check if one of node parent is hidden
        :param:(MFnDagNode)
        :return: True if all parent are shown, False if any parebt is hidden
        """
        for i in range(nodeFn.parentCount()):
            parent_obj = nodeFn.parent(i)
            parent_fn = om.MFnDagNode(parent_obj)
            plug = nodeFn.findPlug("visibility", False)
            if plug.asBool():  # if visibility on
                if not self.ck_parents_vis(parent_fn):
                    return False
            else:
                return False
        return True

    def list_allDag(self, shape=True, fullPath=True, type=om.MFn.kMesh, hidden=False):
        """
        list all objects in children by type on selection
        :param shape: return shapes
        :param fullPath:
        :param type: MFn Type
        :param hidden: include hidden objects or not, True: included
        :return: list of objects names
        """

        traversal_type = om.MItDag.kDepthFirst
        filter_type = type

        objectsList = []
        selection_list = om.MGlobal.getActiveSelectionList()
        # dag iterator
        dag_iter = om.MItDag(traversal_type, filter_type)

        for i in range(selection_list.length()):
            if not selection_list.isEmpty() and dag_iter.isDone():
                dag_iter.reset(selection_list.getDependNode(i), traversal_type, filter_type)

            while not dag_iter.isDone():
                # MObject
                shape_obj = dag_iter.currentItem()
                # DagNode
                shape_fn = om.MFnDagNode(shape_obj)
                # check intermediate
                inter_plug = shape_fn.findPlug("intermediateObject", False)
                # check if node is not intermediate and not hidden in viewport
                if (hidden or self.ck_parents_vis(shape_fn)) and (not inter_plug.asBool()):
                    if shape:
                        if fullPath:
                            objectsList.append(shape_fn.fullPathName())
                        else:
                            objectsList.append(shape_fn.name())
                    else:
                        parent_fn = om.MFnDagNode(shape_fn.parent(0))

                        if fullPath:
                            objectsList.append(parent_fn.fullPathName())
                        else:
                            objectsList.append(parent_fn.name())
                dag_iter.next()
        return objectsList

    def exportGeoCache(self, geos, path, frameRange=[1, 100], filePerFrame=False):
        """

        :param geo: List of geometry to cache (list)
        :param path: the output path
        :param frameRange:
        :param filePerFrame: (bool) Write file per frame or single file, (False) Write file per shape or single file
        :param forceExport: (bool) Force export even if it overwrites existing files
        :return:
        """
        # Constant value args
        version = 6  # version of geometry cache
        refresh = 1  # Refresh during caching
        usePrefix = 0  # Name as prefix (shape name)
        cacheAction = 'export'  # Cache action "add", "replace", "merge", "mergeDelete" or "export"
        simRate = 1  # (steps per frame - ?)
        forceExport = False

        # Cache file distribution
        if filePerFrame:
            cacheDist = 'OneFilePerFrame'
            cachePerGeo = True
        else:
            cacheDist = 'OneFile'
            cachePerGeo = False

        # Determine destination directory and file
        fileName = os.path.basename(path)
        cacheDir = path.replace("\\", "/")

        startFrame, endFrame = frameRange

        # Export cache
        cmds.select(cl=1)
        cmds.select(geos)
        cmd = 'doCreateGeometryCache ' + str(version) + ' { "2", "' + str(startFrame) + '", "' + str(
            endFrame) + '", "' + cacheDist + '", "' + str(refresh) + '", "' + cacheDir + '", "' + str(
            int(cachePerGeo)) + '", "", "' + str(usePrefix) + '", "' + cacheAction + '", "' + str(
            int(forceExport)) + '", "1", "1","0", "1", "mcx", "0" };'
        print(cmd)
        mel.eval(cmd)

    def importGeoCache(self, geo, cacheFileDir):
        """
        This methode import geometry cache to spacific object
        :param geo: Geometry to load cache to (str)
        :param cacheFileDir: Geometry cache file path to load (path)
        :return:
        """
        # Check geo
        if not cmds.objExists(geo):
            error = 'Geometry: "' + geo + '" does not exist!'
            om.MGlobal.displayWarning(error)
            raise Exception(error)
        # Check file
        if not os.path.isfile(cacheFileDir):
            error = 'Cache file "' + cacheFileDir + '" Missing!'
            om.MGlobal.displayWarning(error)
            raise Exception(error)
        # Load cache
        mel.eval('doImportCacheFile "' + cacheFileDir + '" "" {"' + geo + '"} {}')

    def importGeoCacheList(self, geoList, cachePath):
        """
        :param geoList: list of geomertries
        :param cachePath: the path of geometery cache
        :return:
        """

        cachePath = os.path.normpath(cachePath).replace('\\', '/')
        # Check file
        if not os.path.isfile(cachePath):
            error = 'Cache file "' + cachePath + '" does not exist!'
            raise Exception(error)

        cmds.select(geoList)
        mel.eval('doImportCacheFile "' + cachePath + '" "" {} {}')

        # # For each geometry in list
        # for i in range(len(geoList)):
        #     # Get geometry shape
        #     if cmds.nodeType(geoList[i]) == "mesh":
        #         geoShape = geoList[i]
        #     else:
        #         shapeList = cmds.listRelatives(geoList[i], s=True, ni=True, pa=True)
        #         if shapeList:
        #             geoShape = shapeList[0]
        #         else:
        #             error = '"{}" has not any shape node.'
        #             om.MGlobal.displayWarning(error)
        #             raise Exception(error)
        #
        #     # Check file
        #     if not os.path.isfile(cachePath):
        #         error = 'Cache file "' + cachePath + '" does not exist!'
        #         raise Exception(error)
        #     # Import cache
        #
        #     self.importGeoCache(geoList[i], cachePath)

    def importReference(self, nodes):
        """
        To import the reference node in maya scenece
        @param node:(str) or (list) the maya node
        @return: None
        """
        if isinstance(nodes, list):
            for node in nodes:
                if cmds.referenceQuery(node, isNodeReferenced=True):
                    ref_path = cmds.referenceQuery(node, filename=True)
                    cmds.file(ref_path, importReference=True)
        else:
            if cmds.referenceQuery(nodes, isNodeReferenced=True):
                ref_path = cmds.referenceQuery(nodes, filename=True)
                cmds.file(ref_path, importReference=True)

    def focus_on_selected(self):
        """
        focus to deformed selected
        """
        selected = cmds.ls(sl=1)[0]
        cmds.viewFit(cmds.select(selected + ".f[:]"))
        cmds.select(cl=1)
        cmds.select(selected)

    def reset_ctrl_attrs(self, nurbsCurves):
        """
        #set all nurbsCurves to default attributes
        :param nurbsCurves: list of nurbsCurves
        :return:
        """
        for crv in nurbsCurves:
            attrs = cmds.listAttr(crv, k=1, u=1)
            if not attrs:
                continue
            for eachAttr in attrs:
                try:
                    defaultValue = cmds.attributeQuery(eachAttr, node=crv, ld=1)[0]
                    cmds.setAttr('{}.{}'.format(crv, eachAttr), defaultValue)
                except:
                    pass

    def deleteUnsedNodes(self):
        """
        To delete unused nodes in hypershade
        """
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        mel.eval('MLdeleteUnused;')

    def getAllDGNodes(self, inNode, node_type=om.MFn.kShadingEngine, direction=om.MItDependencyGraph.kDownstream):
        """
        To get the all connection nodes by type
        direction : om.MItDependencyGraph.kUpstream
        nodeMfnType : om.MFn.kShadingEngine, om.MFn.kMesh, om.MFn.FileTexture, om.MFn.kFileTexture

        ## Test ##
        for i in getAllDGNodes("SHoes_PartsShape4", om.MFn.kShadingEngine, om.MItDependencyGraph.kDownstream):
        print(getAllDGNodes(i, om.MFn.kMesh, om.MItDependencyGraph.kUpstream))

        """

        nodes = []
        # Create a MSelectionList to add the object:
        selection_list = om.MSelectionList()
        selection_list.add(inNode)
        mObject = selection_list.getDependNode(0)  # The current object
        node_fn = om.MFnDagNode(mObject)

        # Create a dependency graph iterator for the current object:
        mItDependencyGraph = om.MItDependencyGraph(mObject, direction, direction)
        while not mItDependencyGraph.isDone():
            currentNode = mItDependencyGraph.currentNode()
            dependNode_fn = om.MFnDependencyNode(currentNode)

            # print("Current Node: ", dependNodeFunc.name())
            # Check the type of node
            if currentNode.hasFn(node_type):
                name = dependNode_fn.name()

                if currentNode.hasFn(om.MFn.kDagNode):
                    dagNode_fn = om.MFnDagNode(currentNode)
                    name = dagNode_fn.fullPathName()
                nodes.append(name)
            mItDependencyGraph.next()

        return nodes

    def isNameDuplicated(self, node):
        """
        Check if node name doublicated or not
        @param node: Dag node
        """
        if len(cmds.ls(node)) > 1:
            return True
        else:
            return False

    def renameDuplicates(self):
        """
        To rename all DAG nodes that have the same name, by incrementing the name with 1
        :return:
        """
        # Find all objects that have the same shortname as another
        # We can identify them because they have | in the name
        duplicates = [f for f in cmds.ls() if '|' in f]
        # Sort them by hierarchy so that we don't rename a parent before a child.
        duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)

        # if we have duplicates, rename them
        if duplicates:
            for name in duplicates:
                try:
                    # extract the base name
                    m = re.compile("[^|]*$").search(name)
                    shortname = m.group(0)

                    # extract the numeric suffix
                    m2 = re.compile(".*[^0-9]").match(shortname)
                    if m2:
                        stripSuffix = m2.group(0)
                    else:
                        stripSuffix = shortname

                    # rename, adding '#' as the suffix, which tells maya to find the next available number
                    newname = cmds.rename(name, (stripSuffix + "#"))
                    print("renamed {} to {}".format(name, newname))
                except Exception as e:
                    print(name, e)

            print('Renamed "{}" objects with duplicated name.'.format(duplicates))


# Main function
def main():
    print("Hello, You should run this file inside maya only.")
    pass


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))

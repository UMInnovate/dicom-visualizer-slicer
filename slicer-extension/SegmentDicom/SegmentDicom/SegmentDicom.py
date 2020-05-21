import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# SegmentDicom
#

class SegmentDicom(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SegmentDicom"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = "acknowledgementText"
    self.RunOnStartUp()
    
  def RunOnStartUp(self):
    # Run module on startup of slicer
    slicer.app.connect("startupCompleted()", self.LoadSegment)
  
  def LoadSegment(self):
    # Adding delay to allow other slicer modules to be instantiated
    qt.QTimer.singleShot(100, self.ProceduralSegmentation)

  def ProceduralSegmentation(self):
 
    # TODO create text box for input folder
    # Importing Dicom into temporary database
    #dicomDataDir = "Z:/Dicom2Text/LumbarCTforMagicLeap"
    dicomDataDir = "C:/Users/Public/Pictures"
    from DICOMLib import DICOMUtils
    loadedNodeIDs = []

    with DICOMUtils.TemporaryDICOMDatabase() as db:
      DICOMUtils.importDicom(dicomDataDir, db)
      patientUIDs = db.patients()
      for patientUID in patientUIDs:
        loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
    
    # dicomDataDir = "Z:/Dicom2Text/LumbarCTforMagicLeap"
    #DICOMUtils.importDicom(dicomDataDir)

    # Load specific dicom given sop and series instance uids
    #seriesInstanceUID = '2.16.840.1.114151.3.1.20566.9261759.7592.1584719071.211'
    #sopInstanceUID = '2.16.840.1.114151.3.1.20566.9261759.7592.1584719071.212'
    #DICOMUtils.loadSeriesByUID([seriesInstanceUID])

    #seriesNodeIDs = DICOMUtils.loadSeriesByUID([seriesInstanceUID,])
    #self.delayDisplay(seriesNodeIDs)
    #seriesVolumeNode = slicer.util.getNode(seriesNodeIDs[0])
	#storageNode.SetFileName(slicer.dicomDatabase.fileForInstance(sopInstanceUID))

	# Loading Dicom into scene
    seriesVolumeNode = slicer.util.getNode(loadedNodeIDs[0])
    storageNode = seriesVolumeNode.CreateDefaultStorageNode()
    slicer.mrmlScene.AddNode(storageNode)
    seriesVolumeNode.SetAndObserveStorageNodeID(storageNode.GetID())

    # Access segmentation module
    slicer.util.selectModule('Segment Editor')
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    #segmentationNode = slicer.vtkMRMLSegmentationNode()
    segmentationNode.CreateDefaultDisplayNodes()
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(seriesVolumeNode)
    #segmentTypeID = segmentationNode.GetSegmentation().AddEmptySegment("bone")

    # TODO Automate creation of different segments in the future
    # Create spine segment
    segmentTypeID = "Spine"
    newSegment = slicer.vtkSegment()
    newSegment.SetName(segmentTypeID)
    newSegment.SetColor([0.89, 0.85, 0.78])
    segmentationNode.GetSegmentation().AddSegment(newSegment,segmentTypeID)

    # Create segment editor to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

    # Access segment editor
    #segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
    slicer.mrmlScene.AddNode(segmentEditorNode)
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(seriesVolumeNode)

    # Segment Editor Effect: Thresholding
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","100")
    effect.setParameter("MaximumThreshold","1200")
    effect.self().onApply()

    # Segment Editor Effect: Smoothing
    #segmentEditorWidget.setActiveEffectByName("Smoothing")
    #effect = segmentEditorWidget.activeEffect()
    #effect.setParameter("SmoothingMethod", "MEDIAN")
    #effect.setParameter("KernelSizeMm", 11)
    #effect.self().onApply()

    # Clean up
    segmentEditorWidget = None
    slicer.mrmlScene.RemoveNode(segmentEditorNode)

    # Make segmentation results visible in 3D
    segmentationNode.GetSegmentation().SetConversionParameter("Decimation factor", "0.8") 
    segmentationNode.CreateClosedSurfaceRepresentation()

    # Export segmentation to models module
    #shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    #exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Segments")
    #slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, exportFolderItemId)

    # Send segment to output folder
    # TODO create text box for output folder
    outputFolder = "Z:/GitHub/andrewxr.io"
    segmentIDs = vtk.vtkStringArray()
    segmentIDs.InsertNextValue(segmentTypeID)
    slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsClosedSurfaceRepresentationToFiles(outputFolder, segmentationNode, segmentIDs, "OBJ", True, 1.0, False)

    # Write to OBJ File NOT WORKING!!!
    #surfaceMesh = segmentationNode.GetClosedSurfaceInternalRepresentation(segmentTypeID)
    #writer = vtk.vtkOBJWriter
    #writer.SetInputData(surfaceMesh)
    #writer.SetFileName("Z:/Dicom2Text/DicomPrefabs/testspine1.obj")
    #self.delayDisplay(writer)
    #writer.Update()
	

#
# SegmentDicomWidget
#

class SegmentDicomWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

  def cleanup(self):
    pass

#
# SegmentDicomLogic
#

class SegmentDicomLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


class SegmentDicomTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SegmentDicom1()

  def test_SegmentDicom1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = SegmentDicomLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

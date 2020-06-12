import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

class DICOM2OBJ(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "DICOM2OBJ"
    self.parent.categories = ["Modules"]
    self.parent.dependencies = []
    self.parent.contributors = ["Andrew Gonzalez"]
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
    dicomDataDir = "C:/Users/Public/Pictures"
    from DICOMLib import DICOMUtils
    loadedNodeIDs = []

    with DICOMUtils.TemporaryDICOMDatabase() as db:
      DICOMUtils.importDicom(dicomDataDir, db)
      patientUIDs = db.patients()
      for patientUID in patientUIDs:
        loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))

	# Loading Dicom into scene
    seriesVolumeNode = slicer.util.getNode(loadedNodeIDs[0])
    storageNode = seriesVolumeNode.CreateDefaultStorageNode()
    slicer.mrmlScene.AddNode(storageNode)
    seriesVolumeNode.SetAndObserveStorageNodeID(storageNode.GetID())

    # Access segmentation module
    slicer.util.selectModule('Segment Editor')
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(seriesVolumeNode)

    # TODO Automate creation of different segments in the future
    # Create spine segment
    segmentTypeID = "Spine"
    newSegment = slicer.vtkSegment()
    newSegment.SetName(segmentTypeID)
    newSegment.SetColor([0.89, 0.85, 0.78])
    segmentationNode.GetSegmentation().AddSegment(newSegment,segmentTypeID)

    # Create segment editor widget to get access to effects
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

    # Access segment editor node
    segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
    slicer.mrmlScene.AddNode(segmentEditorNode)
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(seriesVolumeNode)

    # Segment Editor Effect: Thresholding
    segmentEditorWidget.setActiveEffectByName("Threshold")
    thresholdEffect = segmentEditorWidget.activeEffect()
    thresholdEffect.setParameter("MinimumThreshold","90")
    thresholdEffect.setParameter("MaximumThreshold","1600")
    thresholdEffect.self().onApply()

    # Setting Closed Surface Representation Values
    segmentationNode.GetSegmentation().SetConversionParameter("Oversampling factor", "1.5")
    segmentationNode.GetSegmentation().SetConversionParameter("Joint smoothing", "1.00")
    segmentationNode.GetSegmentation().SetConversionParameter("Smoothing factor", "1.00")
    segmentationNode.GetSegmentation().SetConversionParameter("Decimation factor", "0.00")

    # Segment Editor Effect: Smoothing
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    smoothingEffect = segmentEditorWidget.activeEffect()
    # 2mm MEDIAN Smoothing
    #smoothingEffect.setParameter("SmoothingMethod", "MEDIAN")
    #smoothingEffect.setParameter("KernelSizeMm", 2.5)
    #smoothingEffect.self().onApply

    # 2mm OPEN Smoothing
    smoothingEffect.setParameter("SmoothingMethod", "MORPHOLOGICAL_OPENING")
    smoothingEffect.self().onApply
    smoothingEffect.setParameter("KernelSizeMm", 2)
    smoothingEffect.self().onApply
    # 1.5mm CLOSED Smoothing
    smoothingEffect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
    smoothingEffect.self().onApply
    smoothingEffect.setParameter("KernelSizeMm", 1.5)
    smoothingEffect.self().onApply

    # Create Closed Surface Representation
    segmentationNode.CreateClosedSurfaceRepresentation()

    # Clean up
    segmentEditorWidget = None
    slicer.mrmlScene.RemoveNode(segmentEditorNode)

    # Decimate Closed Surface Representation
    decimate = vtkDecimatePro()
    decimate.SetInputData(segmentationNode)
    decimate.SetTargetReduction(.90)
    decimate.Update()

    # Send segment to output folder
    # TODO create text box for output folder
    outputFolder = "Z:/GitHub/andrewxr.io"
    segmentIDs = vtk.vtkStringArray()
    segmentIDs.InsertNextValue(segmentTypeID)
    slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsClosedSurfaceRepresentationToFiles(outputFolder, segmentationNode, segmentIDs, "OBJ", True, 1.0, False) 

    slicer.mrmlScene.RemoveNode(segmentationNode)


class DICOM2OBJWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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

class DICOM2OBJLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

class DICOM2OBJTest(ScriptedLoadableModuleTest):
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
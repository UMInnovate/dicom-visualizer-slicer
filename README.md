# UM Innovate Dicom Visualizer Slicer Extension

UM Innovate's Dicom Visualizer Slicer Extension for converting DICOM2OBJ and STL2OBJ

# Slicer Extension Script Locations

DICOM2OBJ Module
`InnovateVisualizerSlicerExtension\InnovateVisualizer\DICOM2OBJ\DICOM2OBJ.py`

STL2OBJ Module
`InnovateVisualizerSlicerExtension\InnovateVisualizer\STL2OBJ\STL2OBJ.py`

# Slicer Version and How to Install
Version `Slicer 4.11.0 Preview Release revision 29173 built 2020-06-23`

Download here https://download.slicer.org

# Adding Extension to Slicer
Follow the guide provided https://www.slicer.org/wiki/Documentation/4.3/SlicerApplication/ExtensionsManager

# Command Line Interface Subprocess

Launches Slicer `./Slicer`
Without a GUI `--no-main-window --no-splash`
Running the module `--python-script <module_script_path>`
I/O for conversion `-i <input_path> -o <output_path>`

All together 
`./Slicer --no-main-window --no-splash --python-script <module_script_path> -i <input_path> -o <output_path>`

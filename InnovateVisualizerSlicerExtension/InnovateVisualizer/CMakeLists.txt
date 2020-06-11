cmake_minimum_required(VERSION 3.13.4)

project(InnovateVisualizer)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/InnovateVisualizer")
set(EXTENSION_CATEGORY "Modules")
set(EXTENSION_CONTRIBUTORS "Andrew Gonzalez (University of Miami IT Innovate)")
set(EXTENSION_DESCRIPTION "This is University of Miami's IT Innovate Visualizer for converting .dcm files into 3D Models in the form of a .obj. This extension also handles .stl to .obj conversion using slicers segmentation.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/InnovateVisualizer.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/InnovateVisualizer/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(DICOM2OBJ)
add_subdirectory(STL2OBJ)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

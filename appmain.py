import vtk
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.misc import vtkGetDataRoot
from renderapp import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        self.ui.slider.valueChanged.connect(self.slider_SLOT)
        self.ui.pushButton.clicked.connect(self.DICOMREADER)
        self.ui.comboBox.activated.connect(self.Rendering_Mode)

        self.surfaceExtractor = vtk.vtkContourFilter()
        # self.iren = QVTKRenderWindowInteractor()  
    
    def slider_SLOT(self,val):
        self.iren = QVTKRenderWindowInteractor() 
        self.surfaceExtractor.SetValue(0, val)
        self.iren.update()

    def load(self):
        dataDir = QFileDialog.getExistingDirectory(self, 'Choose DICOM Directory') + '/'
        print(dataDir)
        return dataDir 

    def DICOMREADER(self):
        # Read Dataset using vtkDICOMReader
        dataDir = self.load()
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(dataDir)
        print(dataDir)
        self.reader.Update()

    
    def Rendering_Mode(self):
        print(self.ui.comboBox.currentIndex())
        if self.ui.comboBox.currentIndex() == 1:
            self.vtk_surface_rendering()

        elif self.ui.comboBox.currentIndex() == 2:
            self.vtk_rayCasting()
        
    def vtk_surface_rendering(self):
        self.iren = QVTKRenderWindowInteractor()  
        self.renWin = self.iren.GetRenderWindow()
        aRenderer = vtk.vtkRenderer()
        self.renWin.AddRenderer(aRenderer)

        self.surfaceExtractor.SetInputConnection(self.reader.GetOutputPort())
        self.surfaceExtractor.SetValue(0, 0.0)
        surfaceNormals = vtk.vtkPolyDataNormals()
        surfaceNormals.SetInputConnection(self.surfaceExtractor.GetOutputPort())
        surfaceNormals.SetFeatureAngle(60.0)
        surfaceMapper = vtk.vtkPolyDataMapper()
        surfaceMapper.SetInputConnection(surfaceNormals.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        
        surface = vtk.vtkActor()
        surface.SetMapper(surfaceMapper)
        
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()
        
        aRenderer.AddActor(surface)
        aRenderer.SetActiveCamera(aCamera)
        aRenderer.ResetCamera()
        aCamera.Dolly(1)
        
        aRenderer.SetBackground(0, 0, 0)
        self.renWin.SetSize(640, 480)
        aRenderer.ResetCameraClippingRange()
        
        # Interact with the data.
        self.iren.Initialize()
        self.renWin.Render()
        self.iren.Start()
        self.iren.show()
        

    def vtk_rayCasting(self):
       
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(renWin)
        
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(self.reader.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500,  1.0, 0.0, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00)
        volumeScalarOpacity.AddPoint(500,  0.15)
        volumeScalarOpacity.AddPoint(1000, 0.15)
        volumeScalarOpacity.AddPoint(1150, 0.85)
        
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(90,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

      
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

       
        ren.AddViewProp(volume)

        camera =  ren.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 500, c[1], c[2])
        camera.SetViewUp(0, 0, -1)

        renWin.SetSize(640, 480)

        # Interact with the data.
        self.iren.Initialize()
        renWin.Render()
        self.iren.Start()

def main():
    path = os.getcwd()
    os.chdir(path + '/data')
    directory = os.getcwd()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
   
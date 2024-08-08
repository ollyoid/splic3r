from printrun.gviz import GvizWindow
import wx


app = wx.App(False)
with open("../Characterisation/4 Point/First/4point.gcode", "r") as file:
    main = GvizWindow(file, build_dimensions = [360, 360, 360, 0, 0, 0])
main.Show()
app.MainLoop()
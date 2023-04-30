from pyrevit import revit, DB, script, forms, HOST_APP
from pyrevit.revit.db import query
from pyrevit.framework import List
from pyrevit import forms
from pyrevit.forms import WPFWindow

from itertools import izip
from rpw import ui
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox, CommandLink, TaskDialog, Alert
#import helper, math, units, sys



version = HOST_APP.version

def Canceled():
    Alert('User canceled the operation', title="Canceled", header="", exit=True)


def GetCenterPoint(ele):
    bBox = ele.get_BoundingBox(None)
    return (bBox.Max + bBox.Min) / 2


iso = {
"B": 6,
"C": 7, 
"D": 8, 
"CNC": 9,
"NC": 10, 
"PB": 11,
"Other": ""
}

ISOopis = ["B", "C", "D", "CNC", "NC", "PB", "Other" ]
ISObroj = [6, 7, 8, 9, 10, 11, ""]

osnove = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewPlan) 
osnova_dict = {v.Name: v for v in osnove if v.IsTemplate}
osnova_dict["<None>"] = None



components = [

    Label("View Template for Floor Plans"),
    ComboBox(name="isoopcije", options=sorted(iso)), #default="Osnova 1.50"),
    Separator(),
    Label(""),
    Button("Ok")
]

form = FlexForm("View Settings", components)

viewSettings = form.show()



#### CHATGPT ####

from pyrevit import revit, DB

doc = revit.doc

rooms = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_Rooms)\
    .WhereElementIsNotElementType()

corner_count = 0

tolerance = 1e-1

for room in rooms:
    room_boundary = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    for boundary in room_boundary:
        for segment in boundary:
            start_point = segment.GetCurve().GetEndPoint(0)
            end_point = segment.GetCurve().GetEndPoint(1)
            # check if the start and end points are different and close to each other
            if start_point != end_point and start_point.IsAlmostEqualTo(end_point, tolerance):
                corner_count += 1

print('Number of corners in all the rooms: ' + str(corner_count))

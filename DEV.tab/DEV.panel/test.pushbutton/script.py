from pyrevit import revit, DB

from Autodesk.Revit import *


doc = revit.doc

rooms = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_Rooms)\
    .WhereElementIsNotElementType()

tolerance = 0.15

for room in rooms:
    corner_count = 0
    room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    room_boundary = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    for boundary in room_boundary:
        for segment in boundary:
            start_point = segment.GetCurve().GetEndPoint(0)
            end_point = segment.GetCurve().GetEndPoint(1)
            # check if the start and end points are different and close to each other
            if start_point != end_point and start_point.IsAlmostEqualTo(end_point, tolerance):
                corner_count += 1
    print('Room: ' + room_name)
    print('Number of corners: ' + str(corner_count))
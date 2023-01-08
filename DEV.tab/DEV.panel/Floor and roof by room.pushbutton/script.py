# This Python file uses the following encoding: utf-8
import clr
from Autodesk.Revit import Exceptions, Creation
from Autodesk.Revit.DB import Element, XYZ, CurveArray, ModelCurveArray, SpatialElementBoundaryOptions
from pyrevit import revit, DB, script, HOST_APP
from pyrevit.revit.db import query
from pyrevit.framework import List
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
doc = revit.doc
version = HOST_APP.version



def find_by_class_and_name(dbItem, namez):

    findBy = DB.FilteredElementCollector(doc).OfClass(getattr(DB, dbItem)).ToElements()
    if findBy:
        return [find for find in findBy if find.Name == namez]
    else:
        return "Nor floor plan named ±0.00"
#print(find_by_class_and_name("Level", "±0.00"))
# print(find_by_class_and_name("Level", "±0.00"))
# print(find_by_class_and_name("RoofType", "600x600 Armstrong"))

#kolektor
levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
roofTypes = DB.FilteredElementCollector(doc).OfClass(DB.RoofType).ToElements()
floors = DB.FilteredElementCollector(doc).OfClass(DB.FloorType).ToElements()

rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
roofs = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
svaGledista = (DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)) 
floor_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Floor Plan"][1]

osnova = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
osnova = [find for find in osnova if find.Name == "±0.00"][0]

#dict
roofType_dict = {'{}: {}'.format(rf.FamilyName, revit.query.get_name(rf)): rf for rf in roofTypes}
levels_roof_dict = {'{}: {}'.format(lvl.Name, revit.query.get_name(lvl)): lvl for lvl in levels}
levels_floor_dict = {'{}: {}'.format(lvl.Name, revit.query.get_name(lvl)): lvl for lvl in levels}
floors_dict = {'{}: {}'.format(fl.FamilyName, revit.query.get_name(fl)): fl for fl in floors}

#form
components = [
    
    Label ("Place Roofs"),
    CheckBox(name="place_roof", checkbox_text="", default=True),
    Label ("Select Roof Type"),
    ComboBox(name="rf", options=sorted(roofType_dict)), #default="Sloped Glazing: 600x600 Armstrong"),
    Label("Select Roof Level"),
    ComboBox(name="rflvl", options=sorted(levels_roof_dict)), #default="+3.00: +3.00"),
    
    Separator(),
    
    Label ("Place Floor"),
    CheckBox(name="place_floor", checkbox_text="", default=False),
    Label("Select Floor Type"),
    ComboBox(name="fl", options=sorted(floors_dict), default="Floor: Clean room floor"),
    Label("Select Floor Level"),
    ComboBox(name="fllvl", options=sorted(levels_floor_dict), default="±0.00: ±0.00"),
    
    Separator(),
    Label(""),
    Button("Ok")
]
form = FlexForm("Settings", components)
form.show()

chosen_roof_type = roofType_dict[form.values["rf"]]
chosen_floor = floors_dict[form.values["fl"]]
chosen_roof_level = levels_roof_dict[form.values["rflvl"]]
chosen_floor_level = levels_floor_dict[form.values["fllvl"]]

chosen_place_roof = form.values["place_roof"]
chosen_place_floor = form.values["place_floor"]

foot = 304.8 #jebem ih u usta imperialistička

# dodati if petlju ukoliko je sloped glazing
# offset od plafona
# naši paneli su FamilySymbol i to komplikuje stvari
# defaultRoofPanel = chosen_roof_type.get_Parameter(DB.BuiltInParameter.AUTO_PANEL)	
# print(defaultRoofPanel.AsElementId())
# getRoofPanelType = revit.doc.GetElement(defaultRoofPanel.AsElementId())
# print(getRoofPanelType)
# getThikness = getRoofPanelType.get_Parameter(DB.BuiltInParameter.CURTAIN_WALL_SYSPANEL_THICKNESS).AsDouble()
# print(getThikness)

#Crop
a = True
if a == True:
    chosen_crop_offset = -40
else:
    chosen_crop_offset = 0

with revit.Transaction("Create roof and floor", doc): 

    for room in rooms:
        room_boundary = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        #floor_shape = room_boundary[0]
        openings = list(room_boundary)[1:] if len(room_boundary) > 1 else []
        
        if room.Area > 0:
            room_level_id = room.Level
            room_boundary = room.GetBoundarySegments(room_boundary)[0]
            room_curves = CurveArray()
            roof_curves = DB.CurveLoop()
            normal = XYZ.BasisZ
                        
            for boundary_segment in room_boundary[0]:
                crv = boundary_segment.GetCurve()
                room_curves.Append(crv)
                roof_curves.Append(crv)
                crvStart = crv.GetEndPoint(0)
                crvEnd = crv.GetEndPoint(1)
                inside = DB.XYZ(0, 0, 1)
                ccud = DB.CurveLoop.CreateViaOffset(roof_curves, chosen_crop_offset/foot, inside) #Create floor curve loop
                roofCurveArray = CurveArray() #Initialize the curve array
                for c in ccud: #Append the floor curves to the curve array
                    roofCurveArray.Append(c)
                
            if chosen_place_floor: #create floors
                
                if version < 2023:
                    newFlor = doc.Create.NewFloor(room_curves, chosen_floor, chosen_floor_level, False, normal )
                    flOffsetFromLvl = newFlor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(0)
                    if openings:
                        for opening in openings:
                            opening_curve = CurveArray()
                            for seg in opening:
                                opening_curve.Append(seg.GetCurve())
                    floor_opening = doc.Create.NewOpening(newFlor, opening_curve, True)
                        
                if version >= 2023:
                    List_curve_loop = List[DB.CurveLoop]()
                    for room_outline in room_boundary:
                        curve_loop = DB.CurveLoop()
                        for seg in room_outline:
                            curve_loop.Append(seg.GetCurve())
                        List_curve_loop.Add(curve_loop)
                    newFlor = DB.Floor.Create(doc, room_curves, chosen_floor, chosen_floor_level, False, normal )
                    flOffsetFromLvl = newFlor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(0)
                
            if chosen_place_roof: #create roofs
                mcArray = clr.StrongBox[ModelCurveArray](ModelCurveArray())		
                newRof = doc.Create.NewFootPrintRoof(roofCurveArray, chosen_roof_level, chosen_roof_type, mcArray)
                rfOffsetFromLvl = newRof.get_Parameter(DB.BuiltInParameter.ROOF_LEVEL_OFFSET_PARAM).Set(32/foot)
                
                
                

def room_to_floor(room, floor_type):
    # Make sure that Room is bounding.
    if not room.get_Parameter(DB.BuiltInParameter.ROOM_AREA).AsDouble():
        return None

    # >>>>>>>>>> CREATE FLOOR
    with revit.Transaction("Create roof and floor", doc): 

        # >>>>>>>>>> ROOM BOUNDARIES
        room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        floor_shape = room_boundaries[0]
        openings = list(room_boundaries)[1:] if len(room_boundaries) > 1 else []

        if version < 2023:
            curve_array = CurveArray()
            for seg in floor_shape:
                curve_array.Append(seg.GetCurve())
            new_floor = doc.Create.NewFloor(curve_array, chosen_floor, chosen_floor_level, False)

            # >>>>>>>>>> CREATE FLOOR OPENINGS SEPERATELY BEFORE RVT 2023
            if openings:
                with revit.Transaction("Create Openings", doc): 
                    for opening in openings:
                        opening_curve = CurveArray()
                        for seg in opening:
                            opening_curve.Append(seg.GetCurve())
                        floor_opening = doc.Create.NewOpening(new_floor, opening_curve, True)

        if version >= 2023:
            List_curve_loop = List[DB.CurveLoop]()
            for room_outline in room_boundaries:
                curve_loop = DB.CurveLoop()
                for seg in room_outline:
                    curve_loop.Append(seg.GetCurve())
                List_curve_loop.Add(curve_loop)
            new_floor = DB.Floor.Create(doc, List_curve_loop, chosen_floor.Id, chosen_floor_level.Id) #FIXME

    return new_floor
#
def create_floors(selected_rooms, chosen_floor):
    """Function to loop through selected rooms and create floors from them."""
    # >>>>>>>>>> LOOP THROUGH ROOMS
    with TransactionGroup(doc, __title__) as tg:
        tg.Start()
        for r in selected_rooms:
            with try_except(debug=True):
                room_to_floor(room = r, floor_type=chosen_floor)
        tg.Assimilate()
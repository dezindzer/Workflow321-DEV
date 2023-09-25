# -*- coding: utf-8 -*-
import  os
from pyrevit import revit, DB, script, forms
from pyrevit.revit import doc
from pyrevit.revit.db import query
from Autodesk.Revit.DB import *

ft=304.8
mm=3.280839
output = script.get_output()
matching_elements = [] # list to store the elements that match the criteria
collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels) # filtered element collector

for element in collector: # Iterate through the elements and check if they have the specified parameter
    param = element.LookupParameter("Sirina A") # Get the parameter to search for
    if param is not None and param.HasValue: # Check if the parameter exists and has a value
        matching_elements.append(element)

counter=0
with revit.Transaction("test", doc):
    for element in matching_elements: 
        A = element.GetParameters("A")[0].AsValueString() #Width
        B = element.GetParameters("B")[0].AsValueString() #Height
        
        SirinaA = element.GetParameters("Sirina A")[0].AsValueString()
        VisinaA = element.GetParameters("Visina A")[0].AsValueString()
        AX = element.GetParameters("Udaljenost ose A od vert. ivice")[0]
        AY = element.GetParameters("Visina ose A")[0]
        TestAXLeft = (27.0 + float(SirinaA)/2.0)/ft
        TestAXRight = (float(A) - 27.0 - float(SirinaA)/2.0)/ft
        TestAYTop = (float(B) - 27.0 - float(VisinaA)/2.0)/ft
        TestAYBottom = (27.0 + float(VisinaA)/2.0)/ft
        
        if TestAXLeft > AX.AsDouble():
            AX.Set(TestAXLeft)
            counter=counter+1
            print('AX Left ├ id: {}'.format(output.linkify(element.Id)))
        if AX.AsDouble() > TestAXRight:
            AX.Set(TestAXRight)
            counter=counter+1
            print('AX Right ├ id: {}'.format(output.linkify(element.Id)))
        if TestAYBottom > AY.AsDouble():
            AY.Set(TestAYBottom)
            counter=counter+1
            print('AX Bottom ├ id: {}'.format(output.linkify(element.Id)))
        if AY.AsDouble() > TestAYTop:
            AY.Set(TestAYTop)
            counter=counter+1
            print('AX Top ├ id: {}'.format(output.linkify(element.Id)))
                
        # if element.LookupParameter("Sirina B") is not None and param.HasValue:
        #     SirinaB = element.GetParameters("Sirina B")[0].AsValueString()
        #     VisinaB = element.GetParameters("Visina B")[0].AsValueString()
        #     BX = element.GetParameters("Udaljenost ose B od vert. ivice")[0]
        #     BY = element.GetParameters("Visina ose B")[0]
        #     TestBXLeft = (27.0 + float(SirinaB)/2.0)/ft
        #     TestBXRight = (float(A) - 27.0 - float(SirinaB)/2.0)/ft
        #     TestBXTop = (float(A) - 27.0 - float(VisinaB)/2.0)/ft
        #     TestBXBottom = (27.0 + float(VisinaB)/2.0)/ft
            
        #     if TestBXLeft > AX.AsDouble():
        #         AX.Set(TestBXLeft)
        #         counter=counter+1
        #         print('BX Left ├ id: {}'.format(output.linkify(element.Id)))

        #     if AX.AsDouble() > TestBXRight:
        #         AX.Set(TestBXRight)
        #         counter=counter+1
        #         print('BX Right ├ id: {}'.format(output.linkify(element.Id)))
        #     if TestBXBottom > AX.AsDouble():
        #         AX.Set(TestBXBottom)
        #         counter=counter+1
        #         print('BX Bottom ├ id: {}'.format(output.linkify(element.Id)))
        #     if AX.AsDouble() > TestBXTop:
        #         AX.Set(TestBXTop)
        #         counter=counter+1
        #         print('BX Top ├ id: {}'.format(output.linkify(element.Id)))

print(counter)
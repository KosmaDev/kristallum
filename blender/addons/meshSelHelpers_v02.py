import bpy
import bmesh
import math
import mathutils
from mathutils import Vector
from random import random, seed
from mathutils.bvhtree import BVHTree
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
	"name": "WPL Mesh Helpers",
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

WPL_PROJM = [
	('TO_CAMERA', "To camera", "", 1),
	('USE_NORMALS', "Use Normals", "", 2),
]

kRaycastEpsilon = 0.01
kRaycastDeadzone = 0.05

def force_visible_object(obj):
	if obj:
		if obj.hide == True:
			obj.hide = False
		for n in range(len(obj.layers)):
			obj.layers[n] = False
		current_layer_index = bpy.context.scene.active_layer
		obj.layers[current_layer_index] = True

def select_and_change_mode(obj,obj_mode,hidden=False):
	if obj:
		obj.select = True
		bpy.context.scene.objects.active = obj
		force_visible_object(obj)
		try:
			m = bpy.context.mode
			if bpy.context.mode!='OBJECT':
				bpy.ops.object.mode_set(mode='OBJECT')
			bpy.context.scene.update()
			bpy.ops.object.mode_set(mode=obj_mode)
			#print("Mode switched to ", obj_mode)
		except:
			pass
		obj.hide = hidden
	return m

def camera_pos(region_3d):
	""" Return position, rotation data about a given view for the first space attached to it """
	#https://stackoverflow.com/questions/9028398/change-viewport-angle-in-blender-using-python
	def camera_position(matrix):
		""" From 4x4 matrix, calculate camera location """
		t = (matrix[0][3], matrix[1][3], matrix[2][3])
		r = (
		  (matrix[0][0], matrix[0][1], matrix[0][2]),
		  (matrix[1][0], matrix[1][1], matrix[1][2]),
		  (matrix[2][0], matrix[2][1], matrix[2][2])
		)
		rp = (
		  (-r[0][0], -r[1][0], -r[2][0]),
		  (-r[0][1], -r[1][1], -r[2][1]),
		  (-r[0][2], -r[1][2], -r[2][2])
		)
		output = mathutils.Vector((
		  rp[0][0] * t[0] + rp[0][1] * t[1] + rp[0][2] * t[2],
		  rp[1][0] * t[0] + rp[1][1] * t[1] + rp[1][2] * t[2],
		  rp[2][0] * t[0] + rp[2][1] * t[1] + rp[2][2] * t[2],
		))
		return output
	#look_at = region_3d.view_location
	matrix = region_3d.view_matrix
	#rotation = region_3d.view_rotation
	camera_pos = camera_position(matrix)
	return camera_pos

def get_selected_facesIdx(active_mesh):
	# find selected faces
	bpy.ops.object.mode_set(mode='OBJECT')
	faces = [f.index for f in active_mesh.polygons if f.select]
	# print("selected faces: ", faces)
	return faces

def get_selected_edgesIdx(active_mesh):
	# find selected faces
	bpy.ops.object.mode_set(mode='OBJECT')
	selectedEdgesIdx = [e.index for e in active_mesh.edges if e.select]
	return selectedEdgesIdx

def get_selected_vertsIdx(active_mesh):
	# find selected faces
	bpy.ops.object.mode_set(mode='OBJECT')
	selectedVertsIdx = [e.index for e in active_mesh.vertices if e.select]
	return selectedVertsIdx

def visibilitySelect(active_object, active_mesh, context, actionSelectType, fuzz):
	selverts = get_selected_vertsIdx(active_mesh)
	bpy.ops.object.mode_set( mode = 'EDIT' )
	bpy.ops.mesh.select_all(action = 'DESELECT')
	scene = bpy.context.scene
	bm = bmesh.from_edit_mesh( active_mesh )
	bm.verts.ensure_lookup_table()
	bm.faces.ensure_lookup_table()
	bm.verts.index_update()
	cameraOrigin = camera_pos(bpy.context.space_data.region_3d)
	affectedVerts = []
	fuzzlist = [(0,0,0),(fuzz,0,0),(-fuzz,0,0),(0,fuzz,0),(0,-fuzz,0),(0,0,fuzz),(0,0,-fuzz)]
	for face in bm.faces:
		for vert in face.verts:
			for fuzzpic in fuzzlist:
				if vert.index not in affectedVerts:
					# Cast a ray from the "camera" position
					co_world = active_object.matrix_world * vert.co + mathutils.Vector(fuzzpic)
					direction = co_world - cameraOrigin;
					direction.normalize()
					result, location, normal, faceIndex, object, matrix = scene.ray_cast( cameraOrigin, direction )
					#print ("result",result," faceIndex",faceIndex," vert",vert, " verts", bm.faces[faceIndex].verts)
					if result and object.name == active_object.name:
						facevrt = [ e.index for e in bm.faces[faceIndex].verts]
						#print ("vert.index",vert.index," facevrt",facevrt)
						if vert.index in facevrt:
							affectedVerts.append(vert.index)
	#bmesh.update_edit_mesh( active_mesh )
	bpy.ops.object.mode_set(mode='OBJECT')
	if actionSelectType == 0:
		for vertIdx in affectedVerts:
			active_mesh.vertices[vertIdx].select = True
	elif actionSelectType == 1:
		for vertIdx in selverts:
			if vertIdx in affectedVerts:
				active_mesh.vertices[vertIdx].select = True
	elif actionSelectType == 2:
		for vertIdx in selverts:
			if vertIdx not in affectedVerts:
				active_mesh.vertices[vertIdx].select = True
	bpy.ops.object.mode_set(mode='EDIT')
	#context.tool_settings.mesh_select_mode = (True, False, False)
	bpy.ops.mesh.select_mode(type="VERT")
		
class WPL_selvccol( bpy.types.Operator ):
	bl_idname = "mesh.wplvert_selvccol"
	bl_label = "Select by VC color"
	bl_options = {'REGISTER', 'UNDO'}
	opt_colFuzz = bpy.props.FloatProperty(
		name		= "HSV color distance",
		default	 = 0.3
	)
	@classmethod
	def poll( cls, context ):
		return ( context.object is not None  and
				context.object.type == 'MESH' )

	def current_brush(self, context):
		if context.area.type == 'VIEW_3D' and context.vertex_paint_object:
			brush = context.tool_settings.vertex_paint.brush
		elif context.area.type == 'VIEW_3D' and context.image_paint_object:
			brush = context.tool_settings.image_paint.brush
		elif context.area.type == 'IMAGE_EDITOR' and  context.space_data.mode == 'PAINT':
			brush = context.tool_settings.image_paint.brush
		else :
			brush = None
		return brush

	def execute( self, context ):
		active_object = context.scene.objects.active
		active_mesh = active_object.data
		if not active_mesh.vertex_colors:
			self.report({'ERROR'}, "Active object has no Vertex color layer")
			return {'FINISHED'}
		select_and_change_mode(active_object,"VERTEX_PAINT")
		active_mesh.use_paint_mask = True
		br = self.current_brush(context)
		if br:
			#print("brush color:",br.color)
			basecol = Vector(br.color)
			baselayr = active_mesh.vertex_colors.active
			vertx2sel = []
			for ipoly in range(len(active_mesh.polygons)):
				for idx, ivertex in enumerate(active_mesh.polygons[ipoly].loop_indices):
					ivdx = active_mesh.polygons[ipoly].vertices[idx]
					if (ivdx not in vertx2sel) and (baselayr.data[ivertex].color is not None):
						dist = Vector(baselayr.data[ivertex].color)
						if (dist-basecol).length <= self.opt_colFuzz:
							print("Near color:",dist,basecol)
							vertx2sel.append(ivdx)
			select_and_change_mode(active_object,"OBJECT")
			for idx in vertx2sel:
				active_mesh.vertices[idx].select = True
			select_and_change_mode(active_object,"EDIT")
			#select_and_change_mode(active_object,"VERTEX_PAINT")
		return {'FINISHED'}

class WPL_selvisible( bpy.types.Operator ):
	bl_idname = "mesh.wplvert_selvisible"
	bl_label = "Select visible verts"
	bl_options = {'REGISTER', 'UNDO'}
	opt_rayFuzz = bpy.props.FloatProperty(
		name		= "Fuzziness",
		default	 = 0.05
	)
	@classmethod
	def poll( cls, context ):
		return ( context.object is not None  and
				context.object.type == 'MESH' )

	def execute( self, context ):
		if not bpy.context.space_data.region_3d.is_perspective:
			self.report({'ERROR'}, "Can`t work in ORTHO mode")
			return {'CANCELLED'}
		active_object = context.scene.objects.active
		active_mesh = active_object.data
		visibilitySelect(active_object, active_mesh, context, 0, self.opt_rayFuzz )
		return {'FINISHED'}

class WPL_deselvisible( bpy.types.Operator ):
	bl_idname = "mesh.wplvert_deselunvisible"
	bl_label = "Deselect invisible verts"
	bl_options = {'REGISTER', 'UNDO'}
	opt_rayFuzz = bpy.props.FloatProperty(
		name		= "Fuzziness",
		default	 = 0.05
	)
	@classmethod
	def poll( cls, context ):
		return ( context.object is not None  and
				context.object.type == 'MESH' )

	def execute( self, context ):
		if not bpy.context.space_data.region_3d.is_perspective:
			self.report({'ERROR'}, "Can`t work in ORTHO mode")
			return {'CANCELLED'}
		active_object = context.scene.objects.active
		active_mesh = active_object.data
		visibilitySelect(active_object, active_mesh, context, 1, self.opt_rayFuzz )
		return {'FINISHED'}

class WPL_deselunvisible( bpy.types.Operator ):
	bl_idname = "mesh.wplvert_deselvisible"
	bl_label = "Deselect visible verts"
	bl_options = {'REGISTER', 'UNDO'}
	opt_rayFuzz = bpy.props.FloatProperty(
		name		= "Fuzziness",
		default	 = 0.05
	)
	@classmethod
	def poll( cls, context ):
		return ( context.object is not None  and
				context.object.type == 'MESH' )

	def execute( self, context ):
		if not bpy.context.space_data.region_3d.is_perspective:
			self.report({'ERROR'}, "Can`t work in ORTHO mode")
			return {'CANCELLED'}
		active_object = context.scene.objects.active
		active_mesh = active_object.data
		visibilitySelect(active_object, active_mesh, context, 2, self.opt_rayFuzz )
		return {'FINISHED'}

class WPLSelectFeatures_Panel(bpy.types.Panel):
	bl_label = "Selection helpers"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'WPL'

	def draw_header(self, context):
		layout = self.layout
		layout.label(text="")

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		col.separator()
		col.label("Selection control")
		col.operator("mesh.wplvert_selvisible", text="Select visible")
		col.operator("mesh.wplvert_deselvisible", text="Deselect visible")
		col.operator("mesh.wplvert_deselunvisible", text="Deselect invisible")
		col.operator("mesh.wplvert_selvccol", text="Select by VC color")

def register():
	print("WPLSelectFeatures_Panel registered")
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
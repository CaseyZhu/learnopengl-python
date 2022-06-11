#!/usr/bin/python
import sys
import math
import glfw
import OpenGL.GL as gl
from PIL import Image
from pathlib import Path
from pyrr import Matrix44, matrix44, Vector3
from ctypes import c_float, sizeof, c_void_p
import numpy as np
CURDIR = Path(__file__).parent.absolute()
RESDIR = CURDIR.parent.parent.joinpath("resources")
sys.path.append(str(CURDIR.parent))
from shader import Shader
from camera import Camera, CameraMovement

def Tex(fn):
    return RESDIR.joinpath("textures", fn)


width, height = 800, 600
camera = Camera(Vector3([0.0, 0.0, 3.0]))

delta_time = 0.0
last_frame = 0.0

first_mouse = True



def main():
    global delta_time, last_frame

    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(width, height, "LearnOpenGL", None, None)
    if not window:
        print("Window Creation failed!")
        glfw.terminate()

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, on_resize)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    gl.glEnable(gl.GL_DEPTH_TEST)
    #gl.glDepthFunc(gl.GL_ALWAYS); 
    #gl.glEnable(gl.GL_BLEND); 
    #gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);

    shader  = Shader(CURDIR / 'shaders/blending_sort.vs', CURDIR / 'shaders/blending_sort.fs')
    cshader = Shader(CURDIR / 'shaders/singlecolor.vs', CURDIR / 'shaders/singlecolor.fs')
    vertices = [
     # Back face
    -0.5, -0.5, -0.5,  0.0, 0.0, # Bottom-left
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right
     0.5, -0.5, -0.5,  1.0, 0.0, # bottom-right         
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right
    -0.5, -0.5, -0.5,  0.0, 0.0, # bottom-left
    -0.5,  0.5, -0.5,  0.0, 1.0, # top-left
    # Front face
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-right
     0.5,  0.5,  0.5,  1.0, 1.0, # top-right
     0.5,  0.5,  0.5,  1.0, 1.0, # top-right
    -0.5,  0.5,  0.5,  0.0, 1.0, # top-left
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left
    # Left face
    -0.5,  0.5,  0.5,  1.0, 0.0, # top-right
    -0.5,  0.5, -0.5,  1.0, 1.0, # top-left
    -0.5, -0.5, -0.5,  0.0, 1.0, # bottom-left
    -0.5, -0.5, -0.5,  0.0, 1.0, # bottom-left
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-right
    -0.5,  0.5,  0.5,  1.0, 0.0, # top-right
    # Right face
     0.5,  0.5,  0.5,  1.0, 0.0, # top-left
     0.5, -0.5, -0.5,  0.0, 1.0, # bottom-right
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right         
     0.5, -0.5, -0.5,  0.0, 1.0, # bottom-right
     0.5,  0.5,  0.5,  1.0, 0.0, # top-left
     0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left     
    # Bottom face
    -0.5, -0.5, -0.5,  0.0, 1.0, # top-right
     0.5, -0.5, -0.5,  1.0, 1.0, # top-left
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-left
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-left
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-right
    -0.5, -0.5, -0.5,  0.0, 1.0, # top-right
    # Top face
    -0.5,  0.5, -0.5,  0.0, 1.0, # top-left
     0.5,  0.5,  0.5,  1.0, 0.0, # bottom-right
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right     
     0.5,  0.5,  0.5,  1.0, 0.0, # bottom-right
    -0.5,  0.5, -0.5,  0.0, 1.0, # top-left
    -0.5,  0.5,  0.5,  0.0, 0.0  # bottom-left
     
    ]
    vertices = (c_float * len(vertices))(*vertices)
    planeVertices = [
        # positions          // texture Coords 
         5.0, -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5,  5.0,  0.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,

         5.0, -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,
         5.0, -0.5, -5.0,  2.0, 2.0
    ]
    planeVertices = (c_float * len(planeVertices))(*planeVertices)
    transparentVertices = [
        # positions         // texture Coords (swapped y coordinates because texture is flipped upside down)
        0.0,  0.5,  0.0,  0.0,  0.0,
        0.0, -0.5,  0.0,  0.0,  1.0,
        1.0, -0.5,  0.0,  1.0,  1.0,

        0.0,  0.5,  0.0,  0.0,  0.0,
        1.0, -0.5,  0.0,  1.0,  1.0,
        1.0,  0.5,  0.0,  1.0,  0.0
    ]
    transparentVertices =(c_float * len(transparentVertices))(*transparentVertices)
    #cube_positions = [
    #    ( 0.0,  0.0,  0.0),
    #    ( 2.0,  5.0, -15.0),
    #    (-1.5, -2.2, -2.5),
    #    (-3.8, -2.0, -12.3),
    #    ( 2.4, -0.4, -3.5),
    #    (-1.7,  3.0, -7.5),
    #    ( 1.3, -2.0, -2.5),
    #    ( 1.5,  2.0, -2.5),
    #    ( 1.5,  0.2, -1.5),
    #    (-1.3,  1.0, -1.5)
    #]

    # cube VAO
    #unsigned int cubeVAO, cubeVBO;
    cubeVAO = gl.glGenVertexArrays(1)
    cubeVBO = gl.glGenBuffers(1)
    gl.glBindVertexArray(cubeVAO);
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, cubeVBO);
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW);
    gl.glEnableVertexAttribArray(0);
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0));
    gl.glEnableVertexAttribArray(1);
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)));
    #// plane VAO
    #unsigned int planeVAO, planeVBO;
    planeVAO = gl.glGenVertexArrays(1);
    planeVBO = gl.glGenBuffers(1);
    gl.glBindVertexArray(planeVAO);
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, planeVBO);
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(planeVertices), planeVertices, gl.GL_STATIC_DRAW);
    gl.glEnableVertexAttribArray(0);
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0));
    gl.glEnableVertexAttribArray(1);
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)));
    #// transparent VAO
    #unsigned int transparentVAO, transparentVBO;
    transparentVAO = gl.glGenVertexArrays(1);
    transparentVBO = gl.glGenBuffers(1);
    gl.glBindVertexArray(transparentVAO);
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, transparentVBO);
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(transparentVertices), transparentVertices, gl.GL_STATIC_DRAW);
    gl.glEnableVertexAttribArray(0);
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0));
    gl.glEnableVertexAttribArray(1);
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)));
    gl.glBindVertexArray(0);

    #// load textures
    #// -------------
    #unsigned int cubeTexture = loadTexture(FileSystem::getPath("resources/textures/marble.jpg").c_str());
    #unsigned int floorTexture = loadTexture(FileSystem::getPath("resources/textures/metal.png").c_str());
    #unsigned int transparentTexture = loadTexture(FileSystem::getPath("resources/textures/grass.png").c_str());
    # -- load texture 1
    cubeTexture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, cubeTexture)
    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    img = Image.open(Tex('marble.jpg')).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    #load texture 2
    floorTexture =  gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, floorTexture)
    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    img = Image.open(Tex('metal.png')).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    #load teture3
    transparentTexture =  gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, transparentTexture)
    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    img = Image.open(Tex('window.png')) #.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, img.width, img.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    #// transparent windows locations
    #// --------------------------------
    windows = [
        (-1.5, 0.0, -0.48),
        ( 1.5, 0.0, 0.51),
        ( 0.0, 0.0, 0.7),
        (-0.3, 0.0, -2.3),
        (0.5, 0.0, -0.6)
    ]

    # window sort
    wdict= []
    for wposition in windows:
        distence = camera.position[2] - wposition[2]
        wdict.append([distence, list(wposition)]) 
    wdict.sort(key=lambda tup:tup[0],reverse=True)
    windowp =[]
    for wposition in wdict:
        windowp.append([wposition[1:3]])

    shader.use()
    shader.set_int("texture1", 0)
    #shader.set_int("texture2", 1)

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT)

        #gl.glActiveTexture(gl.GL_TEXTURE0)
        #gl.glBindTexture(gl.GL_TEXTURE_2D, texture1)
        #gl.glActiveTexture(gl.GL_TEXTURE1)
        #gl.glBindTexture(gl.GL_TEXTURE_2D, texture2)

        shader.use()
        projection = Matrix44.perspective_projection(camera.zoom, width/height, 0.1, 100.0)
        shader.set_mat4('projection', projection)

        view = camera.get_view_matrix()#Matrix44.look_at(camera_pos, camera_pos + camera_front, camera_up)
        shader.set_mat4('view', view)
        #// floor 
        gl.glBindVertexArray(planeVAO);
        gl.glBindTexture(gl.GL_TEXTURE_2D, floorTexture);
        model = np.identity(4) #glm.mat4(1.0);
        shader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6);
        
        # cubes 
        gl.glEnable(gl.GL_STENCIL_TEST);
        gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_REPLACE);
        gl.glStencilFunc(gl.GL_ALWAYS, 1, 0xFF)
        gl.glStencilMask(0xFF); # 启用模板缓冲写入

        gl.glBindVertexArray(cubeVAO);
        gl.glActiveTexture(gl.GL_TEXTURE0);
        gl.glBindTexture(gl.GL_TEXTURE_2D, cubeTexture);
        #model = np.identity(4) #glm.Mat4(1.0);
        model = Matrix44.from_translation([-1.0, 0.0, -1.0]) #glm.translate(model, glm.vec3(-1.0, 0.0, -1.0));
        shader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36);
        #model = glm.mat4(1.0); 
        model = Matrix44.from_translation([2.0, 0.0, 0.0])#glm.translate(model, glm.vec3(2.0, 0.0, 0.0));
        shader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36);
        #=============================================================================
        #draw outline
        cshader.use()
        cshader.set_mat4('projection', projection)
        cshader.set_mat4('view', view)
        gl.glBindVertexArray(cubeVAO);

        gl.glStencilFunc(gl.GL_NOTEQUAL, 1, 0xFF);
        gl.glStencilMask(0x00); # 禁止模板缓冲的写入
        gl.glDisable(gl.GL_DEPTH_TEST);
        #model = np.identity(4) #glm.Mat4(1.0);
        model = Matrix44.from_translation([-1.0, 0.0, -1.0]) #glm.translate(model, glm.vec3(-1.0, 0.0, -1.0));
        model = model*Matrix44.from_scale([1.05,1.05,1.05])
        cshader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36);
        #model = glm.mat4(1.0); 
        model = Matrix44.from_translation([2.0, 0.0, 0.0])#glm.translate(model, glm.vec3(2.0, 0.0, 0.0));
        model = model*Matrix44.from_scale([1.05,1.05,1.05])
        cshader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36);
        gl.glDisable(gl.GL_STENCIL_TEST);
        gl.glStencilMask(0xFF);
        gl.glEnable(gl.GL_DEPTH_TEST);  
        '''
        #window draw
        gl.glBindVertexArray(transparentVAO);
        gl.glBindTexture(gl.GL_TEXTURE_2D, transparentTexture);
        for position in windowp:
            #model = glm.mat4(1.0);
            model =  Matrix44.from_translation(position)#glm.translate(model, position);
            shader.set_mat4("model", model);
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6);
        '''
        glfw.poll_events()
        glfw.swap_buffers(window)
    #end while
    gl.glDeleteVertexArrays(1, id(cubeVAO))
    gl.glDeleteBuffers(1, id(cubeVBO))
    glfw.terminate()


def on_resize(window, w, h):
    gl.glViewport(0, 0, w, h)

def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.FORWARD, delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.BACKWARD, delta_time)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.LEFT, delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.RIGHT, delta_time)


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y

    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)


def scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)


if __name__ == '__main__':
    main()

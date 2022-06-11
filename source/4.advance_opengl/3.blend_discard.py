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


def Tex(fn):
    return RESDIR.joinpath("textures", fn)


width, height = 800, 600
camera_pos = Vector3([0.0, 0.0, 3.0])
camera_front = Vector3([0.0, 0.0, -1.0])
camera_up = Vector3([0.0, 1.0, 0.0])

delta_time = 0.0
last_frame = 0.0

first_mouse = True
fov = 45.0
yaw = -90.0
pitch = 0.0
sensitivity = 0.1
last_x = 800 / 2
last_y = 300 / 2


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
    glfw.set_cursor_pos_callback(window, on_mouse_event)
    glfw.set_scroll_callback(window, on_mouse_scroll)

    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    gl.glEnable(gl.GL_DEPTH_TEST)
    shader = Shader(CURDIR / 'shaders/blending_discard.vs', CURDIR / 'shaders/blending_discard.fs')

    vertices = [
     # positions      tex_coords
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,

    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,

     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0
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
    cube_positions = [
        ( 0.0,  0.0,  0.0),
        ( 2.0,  5.0, -15.0),
        (-1.5, -2.2, -2.5),
        (-3.8, -2.0, -12.3),
        ( 2.4, -0.4, -3.5),
        (-1.7,  3.0, -7.5),
        ( 1.3, -2.0, -2.5),
        ( 1.5,  2.0, -2.5),
        ( 1.5,  0.2, -1.5),
        (-1.3,  1.0, -1.5)
    ]

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

    img = Image.open(Tex('grass.png')) #.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, img.width, img.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    #// transparent vegetation locations
    #// --------------------------------
    vegetation = [
        (-1.5, 0.0, -0.48),
        ( 1.5, 0.0, 0.51),
        ( 0.0, 0.0, 0.7),
        (-0.3, 0.0, -2.3),
         (0.5, 0.0, -0.6)
    ]

    
    shader.use()
    shader.set_int("texture1", 0)
    #shader.set_int("texture2", 1)

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        #gl.glActiveTexture(gl.GL_TEXTURE0)
        #gl.glBindTexture(gl.GL_TEXTURE_2D, texture1)
        #gl.glActiveTexture(gl.GL_TEXTURE1)
        #gl.glBindTexture(gl.GL_TEXTURE_2D, texture2)

        shader.use()
        projection = Matrix44.perspective_projection(fov, width/height, 0.1, 100.0)
        shader.set_mat4('projection', projection)

        view = Matrix44.look_at(camera_pos, camera_pos + camera_front, camera_up)
        shader.set_mat4('view', view)
        
        # cubes
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
        #// floor
        gl.glBindVertexArray(planeVAO);
        gl.glBindTexture(gl.GL_TEXTURE_2D, floorTexture);
        model = np.identity(4) #glm.mat4(1.0);
        shader.set_mat4("model", model);
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6);
        
        # vegetation
        gl.glBindVertexArray(transparentVAO);
        gl.glBindTexture(gl.GL_TEXTURE_2D, transparentTexture);
        for idx, position in enumerate(vegetation):
            #model = glm.mat4(1.0);
            model =  Matrix44.from_translation(position)#glm.translate(model, position);
            shader.set_mat4("model", model);
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6);
        
        glfw.poll_events()
        glfw.swap_buffers(window)
    #end while
    gl.glDeleteVertexArrays(1, id(cubeVAO))
    gl.glDeleteBuffers(1, id(cubeVBO))
    glfw.terminate()


def on_resize(window, w, h):
    gl.glViewport(0, 0, w, h)


def process_input(window):
    global camera_pos, camera_front
    cam_speed = 2.5 * delta_time

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += cam_speed * camera_front
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= cam_speed * camera_front

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= camera_front.cross(camera_up).normalized * cam_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += camera_front.cross(camera_up).normalized * cam_speed


def on_mouse_scroll(window, dx, dy):
    global fov
    if fov >= 1.0 and fov <= 45.0:
        fov -= dy

    if fov <= 1.0:
        fov = 1.0
    if fov >= 45.0:
        fov = 45.0


def on_mouse_event(window, xpos, ypos):
    global first_mouse, pitch, yaw, last_x, last_y, camera_front
    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset
    if pitch > 89.0:
        pitch = 89.0
    if pitch < -89.0:
        pitch = -89.0

    front = Vector3()
    front.x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
    front.y = math.sin(math.radians(pitch))
    front.z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    camera_front = front.normalized


if __name__ == '__main__':
    main()

import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = 'image'
    num_frames = 1

    foundV = False
    foundF = False
    foundB = False

    for command in commands:
        op = command['op']
        if op == 'basename':
            foundB = True
            if 'args' in command:
                name = command['args'][0]
            else:
                print("basename needs arguments\n")
                exit(0)

        elif op == 'frames':
            foundF = True
            if 'args' in command:
                num_frames = int(command['args'][0])
            else:
                print("Frame needs arguments\n")
                exit(0)
        elif op == 'vary':
            foundV = True


        if (foundV and not foundF):
            print("Vary was found but not frames\n")
            exit(0)
        #if(not foundB):
            #print("The basename is " + name + "\n")

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    for command in commands:
        if command['op'] == 'vary':
            if 'args' and 'knob' in command:
                args = command['args']
                if(args[0] > 0):
                    i = 0
                    while(i < args[0]):
                        if(not(command['knob'] in frames[i])):
                            frames[i][command['knob']] = 0
                        i += 1
                i = int(args[0])
                start = args[2]
                step = float((args[3] - args[2])) / (args[1] - args[0])
                while(i < args[1]):
                    frames[i][command['knob']] = start
                    i += 1
                    start += step

            else:
                print("vary command needs a knob and arguments\n")
                exit(0)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.1,
              0.6,
              1],
             [255,
              0,
              100]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    i = 0

    for frame in frames:
        for key in frame:
            symbols[key] = frame[key]


        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []
        knob = 1

        for command in commands:
            #print command
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']

                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'mesh':
                file=command["args"][0]
                file=open(file+".obj","r")
                objfile=file.readlines()
                ## if you want to "clean up" the file, add the name of what you want to name the new file as a 3rd parameter
                add_mesh_obj(tmp,objfile) 
                matrix_mult( stack[-1], tmp )
                phong(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                file.close()
                tmp = []
                reflect = '.white'

            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []

            elif c == 'move':

                if command['knob']:
                    knob = symbols[command['knob']]

                tmp = make_translate(args[0] * knob, args[1] * knob, args[2] * knob)
                matrix_mult(stack[-1], tmp)

                stack[-1] = [x[:] for x in tmp]
                tmp = []

                knob = 1

            elif c == 'scale':

                if command['knob']:
                    knob = symbols[command['knob']]

                tmp = make_scale(args[0] * knob, args[1] * knob, args[2] * knob )

                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                knob = 1

            elif c == 'rotate':
                if command['knob']:
                    knob = symbols[command['knob']]

                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta * knob)
                elif args[0] == 'y':
                    tmp = make_rotY(theta * knob)
                else:
                    tmp = make_rotZ(theta * knob)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
                knob = 1
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            # end operation loop
        if num_frames > 1:
            i += 1
            #print("saving\n")
            save_extension(screen, "./anim/" + name + "%03d"%i)
            #print("saved\n")
        else:
            save_extension(screen, name)
            display(screen)

    if num_frames > 1:
        make_animation(name)

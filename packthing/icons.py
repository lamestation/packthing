import os, util

#REQUIRE['imagemagick'] = ['convert']

def imagemagick(icon, target, size, fmt):
    if os.path.exists(icon):
        util.mkdir(os.path.dirname(target))
        util.command(['convert',icon,
            '-resize',str(size)+"x"+str(size),
                target])
    else:
        util.error("Icon does not exist:",os.path.join(os.getcwd(),icon))

def pillow(icon, target, size, fmt):
    if os.path.exists(icon):
        print "Generate icon:", icon, target, "("+size+"x"+size, fmt+")"
        img = Image.open(icon)
        img.thumbnail((size, size), Image.ANTIALIAS)
        img.save(target)
    else:
        util.error("Icon does not exist:", icon)


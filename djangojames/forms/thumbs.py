# -*- encoding: utf-8 -*-
# 
# Initial django-thumbs by Antonio Melé
# http://django.es
# 
# Authors:
# 
# - Antonio Melé
# - Atizo AG (atizo.com)

from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import ImageChops
import cStringIO
import os
import re
import math

TOP_CENTER = 'tc'
MIDDLE_CENTER = 'mc'
BOTTOM_CENTER = 'bc'
BOTTOM_LEFT = 'bl'

DEFAULT_EXTENSION = 'png'

def _image_entropy(im):
    """
    Calculate the entropy of an image. Used for "smart cropping".
    """
    hist = im.histogram()
    hist_size = float(sum(hist))
    hist = [h / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])


def _compare_entropy(start_slice, end_slice, slice, difference):
    """
    Calculate the entropy of two slices (from the start and end of an axis),
    returning a tuple containing the amount that should be added to the start
    and removed from the end of the axis.

    """
    start_entropy = _image_entropy(start_slice)
    end_entropy = _image_entropy(end_slice)
    if end_entropy and abs(start_entropy / end_entropy - 1) < 0.01:
        # Less than 1% difference, remove from both sides.
        if difference >= slice * 2:
            return slice, slice
        half_slice = slice // 2
        return half_slice, slice - half_slice
    if start_entropy > end_entropy:
        return 0, slice
    else:
        return slice, 0

def _scale_and_crop(im, size, crop=False, upscale=False, **kwargs):
    """
    Handle scaling and cropping the source image.

    Images can be scaled / cropped against a single dimension by using zero
    as the placeholder in the size. For example, ``size=(100, 0)`` will cause
    the image to be resized to 100 pixels wide, keeping the aspect ratio of
    the source image.

    crop
        Crop the source image height or width to exactly match the requested
        thumbnail size (the default is to proportionally resize the source
        image to fit within the requested thumbnail size).

        By default, the image is centered before being cropped. To crop from
        the edges, pass a comma separated string containing the ``x`` and ``y``
        percentage offsets (negative values go from the right/bottom). Some
        examples follow:

        * ``crop="0,0"`` will crop from the left and top edges.

        * ``crop="-10,-0"`` will crop from the right edge (with a 10% offset)
          and the bottom edge.

        * ``crop=",0"`` will keep the default behavior for the x axis
          (horizontally centering the image) and crop from the top edge.

        The image can also be "smart cropped" by using ``crop="smart"``. The
        image is incrementally cropped down to the requested size by removing
        slices from edges with the least entropy.

        Finally, you can use ``crop="scale"`` to simply scale the image so that
        at least one dimension fits within the size dimensions given (you may
        want to use the upscale option too).

    upscale
        Allow upscaling of the source image during scaling.

    """
    source_x, source_y = [float(v) for v in im.size]
    target_x, target_y = [float(v) for v in size]

    if crop or not target_x or not target_y:
        scale = max(target_x / source_x, target_y / source_y)
    else:
        scale = min(target_x / source_x, target_y / source_y)

    # Handle one-dimensional targets.
    if not target_x:
        target_x = source_x * scale
    elif not target_y:
        target_y = source_y * scale

    if scale < 1.0 or (scale > 1.0 and upscale):
        # Resize the image to the target size boundary. Round the scaled
        # boundary sizes to avoid floating point errors.
        im = im.resize((int(round(source_x * scale)),
                        int(round(source_y * scale))),
                       resample=Image.ANTIALIAS)

    if crop:
        # Use integer values now.
        source_x, source_y = im.size
        # Difference between new image size and requested size.
        diff_x = int(source_x - min(source_x, target_x))
        diff_y = int(source_y - min(source_y, target_y))
        if diff_x or diff_y:
            # Center cropping (default).
            halfdiff_x, halfdiff_y = diff_x // 2, diff_y // 2
            box = [halfdiff_x, halfdiff_y,
                   min(source_x, int(target_x) + halfdiff_x),
                   min(source_y, int(target_y) + halfdiff_y)]
            # See if an edge cropping argument was provided.
            edge_crop = (isinstance(crop, basestring) and
                         re.match(r'(?:(-?)(\d+))?,(?:(-?)(\d+))?$', crop))
            if edge_crop and filter(None, edge_crop.groups()):
                x_right, x_crop, y_bottom, y_crop = edge_crop.groups()
                if x_crop:
                    offset = min(int(target_x) * int(x_crop) // 100, diff_x)
                    if x_right:
                        box[0] = diff_x - offset
                        box[2] = source_x - offset
                    else:
                        box[0] = offset
                        box[2] = source_x - (diff_x - offset)
                if y_crop:
                    offset = min(int(target_y) * int(y_crop) // 100, diff_y)
                    if y_bottom:
                        box[1] = diff_y - offset
                        box[3] = source_y - offset
                    else:
                        box[1] = offset
                        box[3] = source_y - (diff_y - offset)
            # See if the image should be "smart cropped".
            elif crop == 'smart':
                left = top = 0
                right, bottom = source_x, source_y
                while diff_x:
                    slice = min(diff_x, max(diff_x // 5, 10))
                    start = im.crop((left, 0, left + slice, source_y))
                    end = im.crop((right - slice, 0, right, source_y))
                    add, remove = _compare_entropy(start, end, slice, diff_x)
                    left += add
                    right -= remove
                    diff_x = diff_x - add - remove
                while diff_y:
                    slice = min(diff_y, max(diff_y // 5, 10))
                    start = im.crop((0, top, source_x, top + slice))
                    end = im.crop((0, bottom - slice, source_x, bottom))
                    add, remove = _compare_entropy(start, end, slice, diff_y)
                    top += add
                    bottom -= remove
                    diff_y = diff_y - add - remove
                box = (left, top, right, bottom)
            # Finally, crop the image!
            if crop != 'scale':
                im = im.crop(box)
    return im

def generate_thumb_square_generic(img, thumb_size, format, position=MIDDLE_CENTER):
    try:
        img.seek(0)
        image = Image.open(img)
        
        back = Image.new('RGBA', thumb_size, (255, 255, 255, 0))
        
        if image.mode != 'RGBA':
            image = image.convert("RGBA")
        
        image.thumbnail(thumb_size, Image.ANTIALIAS)
        s = image.size
        if position == TOP_CENTER:
            left = thumb_size[0] / 2 - s[0] / 2
            top = 0
        elif position == MIDDLE_CENTER:
            left = thumb_size[0] / 2 - s[0] / 2
            top = thumb_size[1] / 2 - s[1] / 2
        elif position == BOTTOM_CENTER:
            left = thumb_size[0] / 2 - s[0] / 2
            top = thumb_size[1] - s[1]
        elif position == BOTTOM_LEFT:
            left = 0
            top = thumb_size[1] - s[1]        
        else:
            raise AttributeError("Unknown position. Has to be one of %s" % ", ".join([TOP_CENTER, MIDDLE_CENTER, BOTTOM_CENTER,BOTTOM_LEFT]))
            
        back.paste(image, (left, top), image)
        
        io = cStringIO.StringIO()
        
        # PNG and GIF are the same, JPG is JPEG
        if format.upper()=='JPG':
            format = 'JPEG'
        
        back.save(io, format, quality=90)
        return ContentFile(io.getvalue())
    except Exception, e:
        raise IOError(e)

def generate_thumb_square_bottom(img, thumb_size, format):
    return generate_thumb_square_generic(img, thumb_size, format, BOTTOM_CENTER)

def generate_thumb_square_middle(img, thumb_size, format):
    return generate_thumb_square_generic(img, thumb_size, format, MIDDLE_CENTER)

def generate_thumb_square_top(img, thumb_size, format):
    return generate_thumb_square_generic(img, thumb_size, format, TOP_CENTER)

def generate_thumb_bottom_left(img, thumb_size, format):
    return generate_thumb_square_generic(img, thumb_size, format, BOTTOM_LEFT)

def generate_thumb_button100(img, thumb_size, format):
    button_size = (100, 110)
    img.seek(0)
    image = Image.open(img)
    back = Image.new('RGBA', button_size, (255, 255, 255, 255))
    
    if image.mode != 'RGBA':
        image = image.convert("RGBA")
        
    image.thumbnail((90,90), Image.ANTIALIAS)
    s = image.size
    left = button_size[0] / 2 - s[0] / 2
    top = button_size[1] / 2 - s[1] / 2 - 5
    back.paste(image, (left, top), image)
        
    button = ImageChops.multiply(back, Image.open(os.path.join(settings.MEDIA_ROOT, 'images/start-logo-button.png')))

    io = cStringIO.StringIO()
    button.save(io, 'PNG')

    return ContentFile(io.getvalue())

def generate_thumb_cropped(img, thumb_size, format):
    img.seek(0)
    image = Image.open(img)

    if image.mode != 'RGBA':
        image = image.convert("RGBA")

    image = _scale_and_crop(image, thumb_size, crop=True, upscale=True)

    # PNG and GIF are the same, JPG is JPEG
    if format.upper()=='JPG':
        format = 'JPEG'

    # fix for 'unsupported operand type' within PIL
    if isinstance(image.size[0], float):
        image.size = (int(image.size[0]), int(image.size[1]))

    io = cStringIO.StringIO()
    image.save(io, format, quality=90)

    return ContentFile(io.getvalue())

def generate_thumb_simple(img, thumb_size, format):
    img.seek(0)
    image = Image.open(img)
    s = image.size
    
    if image.mode != 'RGBA':
        image = image.convert("RGBA")
    
    max_side = float(max(s[0], s[1]))
    if max_side > float(thumb_size[0]):
        zoom_factor = max_side / thumb_size[0] * 1.0
        image.thumbnail((s[0] / zoom_factor, s[1] / zoom_factor), Image.ANTIALIAS)

    # PNG and GIF are the same, JPG is JPEG
    if format.upper()=='JPG':
        format = 'JPEG'
    
    # fix for 'unsupported operand type' within PIL
    if isinstance(image.size[0], float):
        image.size = (int(image.size[0]), int(image.size[1]))

    io = cStringIO.StringIO()
    image.save(io, format, quality=90)

    return ContentFile(io.getvalue())

def generate_thumb_std(img, thumb_size, format):
    """
    Generates a thumbnail image and returns a ContentFile object with the thumbnail

    Parameters:
    ===========
    img         File object

    thumb_size  desired thumbnail size, ie: (200,120)

    format      format of the original image ('jpeg','gif','png',...)
                (this format will be used for the generated thumbnail, too)
    """

    img.seek(0) # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(img)

    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')

    # get size
    thumb_w, thumb_h = thumb_size
    # If you want to generate a square thumbnail
    if thumb_w == thumb_h:
        # quad
        xsize, ysize = image.size
        # get minimum size
        minsize = min(xsize,ysize)
        # largest square possible in the image
        xnewsize = (xsize-minsize)/2
        ynewsize = (ysize-minsize)/2
        # crop it
        image2 = image.crop((xnewsize, ynewsize, xsize-xnewsize, ysize-ynewsize))
        # load is necessary after crop                
        image2.load()
        # thumbnail of the cropped image (with ANTIALIAS to make it look better)
        image2.thumbnail(thumb_size, Image.ANTIALIAS)
    else:
        # not quad
        image2 = image
        image2.thumbnail(thumb_size, Image.ANTIALIAS)

    io = cStringIO.StringIO()
    # PNG and GIF are the same, JPG is JPEG
    if format.upper()=='JPG':
        format = 'JPEG'
    
    image2.save(io, format)
    return ContentFile(io.getvalue())

class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    See ImageWithThumbsField for usage example
    """
    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)
        if self.field.styles:
            def get_size(self, style, use_path=False):
                if not self:
                    return ''
                else:
                    if not use_path:
                        split = self.url.rsplit('.',1)
                    else:
                        split = self.path.rsplit('.',1)
                                   
                    if style.has_key('extension'):
                        extension = style['extension']
                    else:
                        #Standard extension if missing
                        if len(split) < 2:
                            extension = DEFAULT_EXTENSION
                        else:
                            extension = split[1]
                            
                    if style.has_key('name'):
                        return '%s.%s.%s' % (split[0], style['name'], extension)
                    return '%s.%sx%s.%s' % (split[0], style['w'], style['h'], extension)
                    
            for style in self.field.styles:
                if style.has_key('name'):
                    setattr(self, 'url_%s' % style['name'], get_size(self, style))
                    setattr(self, 'path_%s' % style['name'], get_size(self, style, True))
                else:
                    setattr(self, 'url_%sx%s' % (style['w'], style['h']), get_size(self, style))
                    setattr(self, 'path_%sx%s' % (style['w'], style['h']), get_size(self, style, True))
                
    def save(self, name, content, save=True):
        super(ImageWithThumbsFieldFile, self).save(name, content, save)
        if self.field.styles:
            for style in self.field.styles:
                size = (style['w'], style['h'])
                
                split = self.name.rsplit('.',1)
                name = split[0]
                
                if style.has_key('extension'):
                    extension = style['extension']
                else:
                    #Standard extension if missing
                    if len(split) < 2:
                        extension = DEFAULT_EXTENSION
                    else:
                        extension = split[1]
                        
                if style.has_key('name'):
                    thumb_name = '%s.%s.%s' % (name, style['name'], extension)
                else:
                    thumb_name = '%s.%sx%s.%s' % (name, size[0], size[1], extension)
                    
                if style.has_key('method'):
                    thumb_content = style['method'](content, size, extension)  
                else:
                    thumb_content = self.field.thumb_method(content, size, extension)
                
                thumb_name_ = self.storage.save(thumb_name, thumb_content)        
                
                if not thumb_name == thumb_name_:
                    raise ValueError('There is already a file named %s' % thumb_name)

    def delete(self, save=True):
        name=self.name
        super(ImageWithThumbsFieldFile, self).delete(save)
        if self.field.styles:
            for style in self.field.styles:
                split = name.rsplit('.',1)
                
                if style.has_key('extension'):
                    extension = style['extension']
                else:
                    #Standard extension if missing
                    if len(split) < 2:
                        extension = DEFAULT_EXTENSION
                    else:
                        extension = split[1]
                
                if style.has_key('name'):
                    thumb_name = '%s.%s.%s' % (split[0], style['name'], extension)
                else:
                    thumb_name = '%s.%sx%s.%s' % (split[0], style['w'], style['h'], extension)
                
                try:
                    self.storage.delete(thumb_name)
                except:
                    pass

class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile
    """
    Usage example:
    ==============
    logo = ImageWithThumbsField(upload_to='uploads/containers/logos', 
                                help_text="Image: 165px * 107px", 
                                styles=({'w': 165, 'h':107},
                                        {'w': 40, 'h':40, 'method': generate_thumb_square_middle},
                                        {'w': 100, 'h':110, 'method': generate_thumb_square_middle, 'name': 'button', 'extension': 'png'}
                                       ), 
                                thumb_method=generate_thumb_bottom_left)
    
    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_165x165
        my_object.photo.url_40x40
        my_object.photo.url_button
    
    Note: The 'styles' attribute is not required. If you don't provide it, 
    ImageWithThumbsField will act as a normal ImageField
        
    How it works:
    =============
    For each style in the 'styles' atribute of the field it generates a 
    thumbnail with that size and stores it following this format:
    
    available_filename.[width]x[height].extension
    or
    available_filename.[name].extension

    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.
    
    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)
    photo.button.png  (second thumbnail)
    
    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg
    photo_.button.png
    
    Note: django-thumbs assumes that if filename "any_filename.jpg" is available 
    filenames with this format "any_filename.[widht]x[height].jpg", "any_filename.[name].jpg" or "any_filename.[name].png" will be available, too.
    
    To do:
    ======
    Add method to regenerate thubmnails
    
    """
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, styles=None, thumb_method=generate_thumb_std,  **kwargs):
        self.verbose_name=verbose_name
        self.name=name
        self.width_field=width_field
        self.height_field=height_field
        self.styles = styles
        self.thumb_method = thumb_method
        super(ImageWithThumbsField, self).__init__(verbose_name=self.verbose_name, **kwargs)

from django import template
from io import BytesIO
import barcode

register = template.Library()

@register.simple_tag
def barcode_generate(uid):
    rv = BytesIO()
    #code = barcode.get('code128', b, writer=SVGWriter())
    code =  barcode.get('code128', uid, writer=barcode.writer.SVGWriter())
    code.write(rv)
    rv.seek(0)
    # get rid of the first bit of boilerplate
    rv.readline()
    rv.readline()
    rv.readline()
    rv.readline()
    # read the svg tag into a string
    svg = rv.read()
    return svg.decode("utf-8")
# PyAVM - Simple pure-python AVM meta-data handling
# Copyright (c) 2011 Thomas P. Robitaille
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from StringIO import StringIO
import xml.etree.ElementTree as et

def register_namespace(tag, uri):
    try:
        et.register_namespace(tag, uri)
    except:
        et._namespace_map[uri] = tag

try:
    import pywcs
    pywcs_installed = True
except:
    pywcs_installed = False

try:
    import pyfits
    pyfits_installed = True
except:
    pyfits_installed = False

from pyavm.embed import embed_xmp

# Define acceptable tags to avoid reading in non-AVM meta-data

tags = {}

tags['photoshop'] = {}
tags['xapRights'] = {}
tags['Iptc4xmpCore'] = {}
tags['dc'] = {}
tags['avm'] = {}

# Metadata Tag Definitions

# Creator Metadata

tags['photoshop']['Source'] = 'Creator'
tags['Iptc4xmpCore']['CiUrlWork'] = 'CreatorURL'
tags['dc']['creator'] = 'Contact.Name'
tags['Iptc4xmpCore']['CiEmailWork'] = 'Contact.Email'
tags['Iptc4xmpCore']['CiTelWork'] = 'Contact.Telephone'
tags['Iptc4xmpCore']['CiAdrExtadr'] = 'Contact.Address'
tags['Iptc4xmpCore']['CiAdrCity'] = 'Contact.City'
tags['Iptc4xmpCore']['CiAdrRegion'] = 'Contact.StateProvince'
tags['Iptc4xmpCore']['CiAdrPcode'] = 'Contact.PostalCode'
tags['Iptc4xmpCore']['CiAdrCtry'] = 'Contact.Country'
tags['xapRights']['UsageTerms'] = 'Rights'

# Content Metadata

tags['dc']['title'] = 'Title'
tags['photoshop']['Headline'] = 'Headline'
tags['dc']['description'] = 'Description'
tags['avm']['Subject.Category'] = 'Subject.Category'
tags['dc']['subject'] = 'Subject.Name'
tags['avm']['Distance'] = 'Distance'
tags['avm']['Distance.Notes'] = 'Distance.Notes'
tags['avm']['ReferenceURL'] = 'ReferenceURL'
tags['photoshop']['Credit'] = 'Credit'
tags['photoshop']['DateCreated'] = 'Date'
tags['avm']['ID'] = 'ID'
tags['avm']['Type'] = 'Type'
tags['avm']['Image.ProductQuality'] = 'Image.ProductQuality'

# Observation Metadata

tags['avm']['Facility'] = 'Facility'
tags['avm']['Instrument'] = 'Instrument'
tags['avm']['Spectral.ColorAssignment'] = 'Spectral.ColorAssignment'
tags['avm']['Spectral.Band'] = 'Spectral.Band'
tags['avm']['Spectral.Bandpass'] = 'Spectral.Bandpass'
tags['avm']['Spectral.CentralWavelength'] = 'Spectral.CentralWavelength'
tags['avm']['Spectral.Notes'] = 'Spectral.Notes'
tags['avm']['Temporal.StartTime'] = 'Temporal.StartTime'
tags['avm']['Temporal.IntegrationTime'] = 'Temporal.IntegrationTime'
tags['avm']['DatasetID'] = 'DatasetID'

# Coordinate Metadata

tags['avm']['Spatial.CoordinateFrame'] = 'Spatial.CoordinateFrame'
tags['avm']['Spatial.Equinox'] = 'Spatial.Equinox'
tags['avm']['Spatial.ReferenceValue'] = 'Spatial.ReferenceValue'
tags['avm']['Spatial.ReferenceDimension'] = 'Spatial.ReferenceDimension'
tags['avm']['Spatial.ReferencePixel'] = 'Spatial.ReferencePixel'
tags['avm']['Spatial.Scale'] = 'Spatial.Scale'
tags['avm']['Spatial.Rotation'] = 'Spatial.Rotation'
tags['avm']['Spatial.CoordsystemProjection'] = 'Spatial.CoordsystemProjection'
tags['avm']['Spatial.Quality'] = 'Spatial.Quality'
tags['avm']['Spatial.Notes'] = 'Spatial.Notes'
tags['avm']['Spatial.FITSheader'] = 'Spatial.FITSheader'
tags['avm']['Spatial.CDMatrix'] = 'Spatial.CDMatrix'

# Published Metadata

tags['avm']['Publisher'] = 'Publisher'
tags['avm']['PublisherID'] = 'PublisherID'
tags['avm']['ResourceID'] = 'ResourceID'
tags['avm']['ResourceURL'] = 'ResourceURL'
tags['avm']['RelatedResources'] = 'RelatedResources'
tags['avm']['MetadataDate'] = 'MetadataDate'
tags['avm']['MetadataVersion'] = 'MetadataVersion'

# Define reverse dictionary for above tags

reverse_tags = {}
for tag in tags:
    for name in tags[tag]:
        reverse_tags[tags[tag][name]] = (tag, name)

# Define namespace to tag mapping

namespaces = {}
namespaces['http://www.communicatingastronomy.org/avm/1.0/'] = 'avm'
namespaces['http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/'] = 'Iptc4xmpCore'
namespaces['http://purl.org/dc/elements/1.1/'] = 'dc'
namespaces['http://ns.adobe.com/photoshop/1.0/'] = 'photoshop'
namespaces['http://ns.adobe.com/xap/1.0/rights/'] = 'xapRights'

reverse_namespaces = {}
for key in namespaces:
    reverse_namespaces[namespaces[key]] = key


class NoAVMPresent(Exception):
    pass


def capitalize(string):
    return string[0].upper() + string[1:]


def auto_type(string):
    '''Try and convert a string to an integer or float'''
    try:
        return int(string)
    except:
        try:
            return float(string)
        except:
            return string


def format_rdf_seq(parent, seq):

    element = et.SubElement(parent, "rdf:Seq")

    for item in seq:
        li = et.SubElement(element, "rdf:li")
        if type(item) is float:
            li.text = "%.16f" % item
        else:
            li.text = "%s" % unicode(item)

    return element


def format_object(parent, avm_name, content):

    tag, name = reverse_tags[avm_name]
    uri = reverse_namespaces[tag]

    element = et.SubElement(parent, "{%s}%s" % (uri, name))

    if type(content) in [list, tuple]:
        format_rdf_seq(element, content)
    else:
        if type(content) is float:
            element.text = "%.16f" % content
        else:
            element.text = "%s" % unicode(content)

    return element


class AVMContainer(object):

    def __init__(self, allow_value=False):
        if allow_value:
            self.__dict__["_value"] = None

    def __str__(self, indent=0):

        string = ""
        for family in self.__dict__:

            if family.startswith('_'):
                continue

            if type(self.__dict__[family]) is AVMContainer:
                substring = self.__dict__[family].__str__(indent + 3)
                if substring != "":
                    if hasattr(self.__dict__[family], '_value'):
                        string += indent * " " + "%s: %s\n" % (family, unicode(self.__dict__[family]._value))
                    else:
                        string += indent * " " + "%s:\n" % family
                    string += substring
            else:
                if type(self.__dict__[family]) is list:
                    string += indent * " " + "%s:\n" % family
                    for elem in self.__dict__[family]:
                        if elem is not None:
                            string += indent * " " + "   * %s\n" % unicode(elem)
                else:
                    if self.__dict__[family] is not None:
                        string += indent * " " + \
                                  "%s: %s\n" % (family, unicode(self.__dict__[family]))

        return string.encode('utf-8')

    def __repr__(self):
        return self.__str__()

    def __setattr__(self, attribute, value):
        if attribute not in self.__dict__:
            raise Exception("%s is not a valid AVM tag" % attribute)
        else:
            object.__setattr__(self, attribute, value)


def parse_avm_content(rdf):

    avm_content = {}

    for item in rdf.attrib:

        # Find URI
        uri, tag = item[1:].split('}')

        if uri in namespaces:
            avm_content[(namespaces[uri], tag)] = auto_type(rdf.attrib[item])

    for item in rdf:

        # Find URI
        uri, tag = item.tag[1:].split('}')

        if uri == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#':
            sub_avm_content = parse_avm_content(item)
            for key in sub_avm_content:
                avm_content[key] = sub_avm_content[key]
        elif uri in namespaces:
            if len(item) == 0:
                avm_content[(namespaces[uri], tag)] = auto_type(item.text)
            elif len(item) == 1:
                c_uri, c_tag = item[0].tag[1:].split('}')
                if c_uri == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#' and c_tag in ['Bag', 'Seq', 'Alt']:
                    avm_content[(namespaces[uri], tag)] = [auto_type(x.text) for x in item[0]]
                else:
                    raise Exception("Unexpected tag %s:%s" % (c_uri, c_tag))
            elif len(item) > 1:
                sub_avm_content = parse_avm_content(item)
                for key in sub_avm_content:
                    avm_content[key] = sub_avm_content[key]

    return avm_content


class AVM(AVMContainer):
    '''
    To parse AVM meta-data from an existing file, simply create an instance of this class using the filename of the image (or any file-like object):

        >>> avm = AVM('myexample.jpg')

    Then, you can view the contents by using

        >>> print avm

    or

        >>> avm

    The AVM meta-data can be accessed using the attribute notation:

        >>> avm.Spatial.Equinox
        'J2000'

        >>> avm.Publisher
        'Chandra X-ray Observatory'

    It is also possible to initialize an AVM object using a pywcs.WCS instance:

        >>> import pyfits
        >>> import pywcs
        >>> from pyavm import AVM
        >>> wcs = pywcs.WCS(pyfits.getheader('image.fits'))
        >>> avm = AVM(wcs)

    Finally, it is possible to embed AVM meta-data into an image file:

        >>> avm.embed('original_image.jpg', 'tagged_image.jpg')

    At this time, only JPG and PNG files are supported for embedding.
    '''

    def __init__(self, *args):

        for avm_name in reverse_tags:

            if "Distance" in avm_name:
                if not "Distance" in self.__dict__:
                    self.__dict__["Distance"] = AVMContainer(allow_value=True)

            if "." in avm_name:
                family, key = avm_name.split('.')
                if not family in self.__dict__:
                    self.__dict__[family] = AVMContainer()
                self.__dict__[family].__dict__[key] = None
            else:
                if avm_name in self.__dict__ and hasattr(self.__dict__[avm_name], '_value'):
                    self.__dict__[avm_name]._value = None
                else:
                    self.__dict__[avm_name] = None

        if len(args) == 1:
            if type(args[0]) is str:
                self.from_file(args[0])
            elif pyfits_installed and isinstance(args[0], pyfits.Header):
                self.from_header(args[0])
            elif pywcs_installed and isinstance(args[0], pywcs.WCS):
                self.from_wcs(args[0])
            else:
                raise Exception("Unknown arguemnt type: %s" % type(args[0]))
        elif len(args) > 1:
            raise Exception("Too many arguments")

    def __setattr__(self, attribute, value):
        if attribute not in self.__dict__:
            raise Exception("%s is not a valid AVM group or tag" % attribute)
        elif isinstance(self.__dict__[attribute], AVMContainer):
            if hasattr(self.__dict__[attribute], "_value"):
                self.__dict__[attribute]._value = value
            else:
                raise Exception("%s is an AVM group, not a tag" % attribute)
        else:
            object.__setattr__(self, attribute, value)

    def from_file(self, filename):

        # Read in image
        if hasattr(filename, 'read'):
            contents = filename.read()
        else:
            contents = file(filename, 'rb').read()

        # Look for XMP packets
        start = contents.find("<?xpacket begin=")
        if start < 0:
            raise NoAVMPresent("No XMP packet found")
        start = contents.index("?>", start) + 2
        end = contents.index("</x:xmpmeta>") + 12
        print "Found XMP packet with %i bytes" % (end - start)

        # Extract XMP packet
        xml = contents[start:end]

        # Parse XML
        tree = et.parse(StringIO(xml))
        root = tree.getroot()
        avm_content = parse_avm_content(root)

        for tag, name in avm_content:

            content = avm_content[(tag, name)]

            if name in tags[tag]:

                avm_name = tags[tag][name]

                # Add to AVM dictionary
                if "." in avm_name:
                    family, key = avm_name.split('.')
                    self.__dict__[family].__dict__[key] = content
                else:
                    if hasattr(self.__dict__[avm_name], '_value'):
                        self.__dict__[avm_name]._value = content
                    else:
                        self.__dict__[avm_name] = content

            else:

                print "WARNING: ignoring tag %s:%s" % (tag, name)

    def to_wcs(self, use_full_header=False):
        '''
        Convert AVM projection information into a pywcs.WCS object
        '''

        if not pywcs_installed:
            raise Exception("PyWCS is required to use to_wcs()")

        if use_full_header and self.Spatial.FITSheader is not None:
            print "Using full FITS header from Spatial.FITSheader"
            header = pyfits.Header(txtfile=StringIO(self.Spatial.FITSheader))
            return pywcs.WCS(header)

        # Initializing WCS object
        wcs = pywcs.WCS(naxis=2)

        # Find the coordinate type
        if self.Spatial.CoordinateFrame is not None:
            ctype = self.Spatial.CoordinateFrame
        else:
            print "WARNING: Spatial.CoordinateFrame not found, assuming ICRS"
            ctype = 'ICRS'

        wcs.wcs.radesys = ctype

        if ctype in ['ICRS', 'FK5', 'FK4']:
            xcoord = "RA--"
            ycoord = "DEC-"
        elif ctype in ['ECL']:
            xcoord = "ELON"
            ycoord = "ELAT"
        elif ctype in ['GAL']:
            xcoord = "GLON"
            ycoord = "GLAT"
        elif ctype in ['SGAL']:
            xcoord = "SLON"
            ycoord = "SLAT"
        else:
            raise Exception("Unknown coordinate system: %s" % ctype)

        # Find the projection type
        cproj = ('%+4s' % self.Spatial.CoordsystemProjection).replace(' ', '-')

        wcs.wcs.ctype[0] = xcoord + cproj
        wcs.wcs.ctype[1] = ycoord + cproj

        # Find the equinox
        equinox = self.Spatial.Equinox

        if type(equinox) is str:
            if equinox == "J2000":
                wcs.wcs.equinox = 2000.
            elif equinox == "B1950":
                wcs.wcs.equinox = 1950.
            else:
                raise Exception("Unknown equinox: %s" % equinox)
        else:
            wcs.wcs.equinox = float(equinox)

        # Set standard WCS parameters
        wcs.naxis1, wcs.naxis2 = self.Spatial.ReferenceDimension
        wcs.wcs.crval = self.Spatial.ReferenceValue
        wcs.wcs.crpix = self.Spatial.ReferencePixel

        if self.Spatial.CDMatrix is not None:
            wcs.wcs.cd = [self.Spatial.CDMatrix[0:2],
                          self.Spatial.CDMatrix[2:4]]
        elif self.Spatial.Scale is not None:
            wcs.wcs.cdelt = self.Spatial.Scale
            if self.Spatial.Rotation is not None:
                wcs.wcs.crota = self.Spatial.Rotation, self.Spatial.Rotation

        return wcs

    def from_header(self, header, include_full_header=True):
        '''
        Convert a FITS header into AVM information
        '''

        if not pyfits_installed:
            raise Exception("PyWCS is required to use from_wcs()")

        if include_full_header:
            self.Spatial.FITSheader = unicode(header)

        if pywcs_installed:
            wcs = pywcs.WCS(header)
            self.from_wcs(wcs)

    def from_wcs(self, wcs):
        '''
        Convert a pywcs.WCS object into AVM information
        '''

        if not pywcs_installed:
            raise Exception("PyWCS is required to use from_wcs()")

        # Equinox

        self.Spatial.Equinox = wcs.wcs.equinox

        # Projection

        proj1 = wcs.wcs.ctype[0][-3:]
        proj2 = wcs.wcs.ctype[1][-3:]
        if proj1 == proj2:
            self.Spatial.CoordsystemProjection = proj1
        else:
            raise Exception("Projections do not agree: %s / %s" % (proj1, proj2))

        self.Spatial.ReferenceDimension = [wcs.naxis1, wcs.naxis2]
        self.Spatial.ReferenceValue = wcs.wcs.crval.tolist()
        self.Spatial.ReferencePixel = wcs.wcs.crpix.tolist()
        self.Spatial.Scale = wcs.wcs.cdelt.tolist()
        try:
            self.Spatial.Rotation, wcs.wcs.crota[1]
        except:
            pass

        self.Spatial.Quality = "Full"

    def to_xmp(self):

        # Register namespaces
        register_namespace('x', "adobe:ns:meta/")
        register_namespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        for namespace in namespaces:
            register_namespace(namespaces[namespace], namespace)

        # Initialize XMP packet
        packet = u'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'

        # Create containing structure
        root = et.Element("{adobe:ns:meta/}xmpmeta")
        trunk = et.SubElement(root, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
        branch = et.SubElement(trunk, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")

        # Write meta-data version
        format_object(branch, "MetadataVersion", "1.1")

        # Write all the elements
        for name in self.__dict__:
            if isinstance(self.__dict__[name], AVMContainer):
                for key in self.__dict__[name].__dict__:
                    if self.__dict__[name].__dict__[key] is not None:
                        if key == "_value":
                            format_object(branch, '%s' % name, self.__dict__[name]._value)
                        else:
                            format_object(branch, '%s.%s' % (name, key), self.__dict__[name].__dict__[key])
            else:
                if self.__dict__[name] is not None:
                    format_object(branch, name, self.__dict__[name])

        # Create XML Tree
        tree = et.ElementTree(root)

        # Need to create a StringIO object to write to
        s = StringIO()
        tree.write(s)

        # Rewind and read the contents
        s.seek(0)
        packet += s.read().encode('utf-8')

        # Close the XMP packet
        packet += '<?xpacket end="w"?>\n'

        return packet

    def embed(self, filename_in, filename_out, verify=False):

        # Embed XMP packet into file
        embed_xmp(filename_in, filename_out, self.to_xmp())

        # Verify file if needed
        if verify:
            import Image
            image = Image.open(filename_out)
            image.verify()

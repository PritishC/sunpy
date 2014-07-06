"""
SunPy's built-in coordinate frames.
Part of the proposed Coordinates API.
@author: Pritish C. (VaticanCameos)
"""

# NumPy import
import numpy as np

# Astropy imports
from astropy import units as u
from astropy.coordinates.representation import (SphericalRepresentation, CylindricalRepresentation,
                                                CartesianRepresentation, BaseRepresentation)
from astropy.coordinates.baseframe import (BaseCoordinateFrame, frame_transform_graph,
                                           RepresentationMapping)
from astropy.coordinates.transformations import FunctionTransform
from astropy.coordinates import FrameAttribute, TimeFrameAttribute

# SunPy imports
from sunpy import sun as s # For Carrington rotation number
from representation import SphericalWrap180Representation

from datetime import datetime

RSUN_METERS = s.constants.constant('radius').si.value
DSUN_METERS = s.constants.constant('mean distance').si.value

__all__ = ['HelioGraphicStonyhurst', 'HelioGraphicCarrington',
           'HelioCentric', 'HelioProjective']

class HelioGraphicStonyhurst(BaseCoordinateFrame):
    """
    A coordinate or frame in the Stonyhurst Heliographic
    system.
    This system is known to remain fixed with respect to
    the center of the Earth, and its quantities, the
    latitude and longitude, are specified in degrees.

    Parameters
    ----------
    representation: `~astropy.coordinates.BaseRepresentation` or None
        A representation object or None to have no data.
    hlon: `Angle` object.
        The longitude for this object (``lat`` must also be given and ``representation``
        must be None).
    hlat: `Angle` object.
        The latitude for this object (``lon`` must also be given and ``representation``
        must be None).
    rad: `astropy.units.Quantity` object.
        This quantity holds the radial distance. If not specified, it is, by default,
        the solar radius. Optional, must be keyword
    """

    default_representation = SphericalWrap180Representation

    _frame_specific_representation_info = {
        'sphericalwrap180': [RepresentationMapping('lon', 'hlon', 'recommended'),
                             RepresentationMapping('lat', 'hlat', 'recommended'),
                             RepresentationMapping('distance', 'rad', 'recommended')],
        }

    #rad = FrameAttribute(default=((RSUN_METERS/1000)*u.km))
    dateobs = TimeFrameAttribute()

    def __init__(self, *args, **kwargs):
        if args or kwargs: # Non-empty frame use case.
            if args and kwargs: # Mixed use case.
                if not isinstance(args[0], BaseRepresentation):
                    if len(args) == 1 and 'rad' not in kwargs:
                    # If one of hlon/hlat are in args
                        kwargs['rad'] = (RSUN_METERS/1000)*u.km
                if 'dateobs' not in kwargs:
                    kwargs['dateobs'] = datetime.now()
            elif not args: # kwargs-only use case.
                if not isinstance(args[0], BaseRepresentation):
                    if 'rad' not in kwargs: # This default is required by definition.
                        kwargs['rad'] = (RSUN_METERS/1000)*u.km
                if 'dateobs' not in kwargs:
                    kwargs['dateobs'] = datetime.now()
            elif not kwargs: # args-only use case.
                if len(args) == 2:
                    args = list(args)
                    args.append((RSUN_METERS/1000)*u.km)
                    args = tuple(args)
                kwargs['dateobs'] = datetime.now()
        super(HelioGraphicStonyhurst, self).__init__(*args, **kwargs)

def _carrington_offset():
    # This method is to return the Carrington offset.
    return s.heliographic_solar_center()[0]

class HelioGraphicCarrington(HelioGraphicStonyhurst):
    """
    A coordinate or frame in the Carrington Heliographic
    system.
    This frame differs from the Stonyhurst version in the
    definition of the longitude, which is defined using
    an offset which is a time-dependent scalar value.
    representation: `~astropy.coordinates.BaseRepresentation` or None.
        A representation object. If specified, other parameters must
        be in keyword form.
    hlon: `Angle` object.
        The longitude for this object (``lat`` must also be given and ``representation``
        must be None).
    hlat: `Angle` object.
        The latitude for this object (``lon`` must also be given and ``representation``
        must be None).
    rad: `astropy.units.Quantity` object, optional, must be keyword.
        This quantity holds the radial distance. If not specified, it is, by default,
        the solar radius. Optional, must be keyword.
    """

    default_representation = SphericalWrap180Representation

    _frame_specific_representation_info = {
        'sphericalwrap180': [RepresentationMapping('lon', 'hlon', 'recommended'),
                             RepresentationMapping('lat', 'hlat', 'recommended'),
                             RepresentationMapping('distance', 'rad', 'recommended')]
        }

    #rad = FrameAttribute(default=((RSUN_METERS/1000)*u.km))

    def __init__(self, *args, **kwargs):
        super(HelioGraphicCarrington, self).__init__(*args, **kwargs)

class HelioCentric(BaseCoordinateFrame):
    """
    A coordinate or frame in the Heliocentric system.
    This frame may either be specified in Cartesian
    or cylindrical representation.
    Cylindrical representation replaces (x, y) with
    (rho, psi) where rho is the impact parameter and
    psi is the position angle in degrees.

    Parameters
    ----------
    representation: `~astropy.coordinates.BaseRepresentation` or None.
        A representation object. If specified, other parameters must
        be in keyword form and if x, y and z are specified, it must
        be None.
    x: `Quantity` object.
        X-axis coordinate, optional, must be keyword.
    y: `Quantity` object.
        Y-axis coordinate, optional, must be keyword.
    z: `Quantity` object. Shared by both representations.
        Z-axis coordinate, optional, must be keyword.
    D0: `Quantity` object.
        Represents the distance between the observer and the Sun center.
        Defaults to 1AU.
    """

    default_representation = CartesianRepresentation

    _frame_specific_representation_info = {
        'cylindrical': [RepresentationMapping('phi', 'psi', u.deg)]}

   # d = FrameAttribute(default=(1*u.au).to(u.km))
    D0 = FrameAttribute(default=(1*u.au).to(u.km))

class HelioProjective(BaseCoordinateFrame):
    """
    A coordinate or frame in the Helioprojective
    system.
    This is the projected equivalent of the Heliocentric
    coordinate system. As such, the Cartesian representation
    has degrees for each of the units, and the cylindrical
    representation has the rho parameter replaced by Trho,
    or theta_rho.

    Parameters
    ----------
    representation: `~astropy.coordinates.BaseRepresentation` or None.
        A representation object. If specified, other parameters must
        be in keyword form.
    Tx: `Angle` object.
        X-axis coordinate, specified in degrees.
    Ty: `Angle` object.
        Y-axis coordinate, specified in degrees.
    distance: Z-axis coordinate.
        Represents the radial distance between the solar center
        and the observer.
        Defaults to 1AU.
    zeta: `Quantity` object.
        Represents the distance between observer and feature/point.
        Defaults to 0.
    D0: `Quantity` object.
        Represents the distance between observer and solar center.
        Defaults to 1AU.
    """

    default_representation = SphericalWrap180Representation

    _frame_specific_representation_info = {
        'sphericalwrap180': [RepresentationMapping('lon', 'Tx', u.arcsec),
                             RepresentationMapping('lat', 'Ty', u.arcsec),
                             RepresentationMapping('distance', 'distance', u.km)],
        'cylindrical': [RepresentationMapping('rho', 'Trho', u.arcsec),
                        RepresentationMapping('phi', 'psi', u.arcsec),
                        RepresentationMapping('distance', 'distance', u.km)]}

    #d = FrameAttribute(default=(1*u.au).to(u.km))
    D0 = FrameAttribute(default=(1*u.au).to(u.km))

    @property
    def zeta(self):
        """zeta is defined as a property."""
        return self.D0 - self.distance

    def __init__(self, *args, **kwargs):
        """
        This is the custom constructor method for HelioProjective frames.
        It is required as we wish to default 'distance' to 1AU when it
        itself is not present and there are no supporting arguments.
        'zeta' is a supporting argument that must be specified as a kwarg.
        If 'zeta' is present, 'distance' can be calculated as given.
        Both 'zeta' and 'distance' cannot be present at the same time.
        """
        if args or (kwargs and len(kwargs) != 1):
            # Non-empty frame use case.
            if args and kwargs:
                # If we have both args and kwargs.
                if isinstance(args[0], BaseRepresentation):
                    # The case when first arg is a representation.
                    if 'zeta' in kwargs:
                        # zeta cannot be provided as SphericalRep takes three arguments.
                        raise TypeError("zeta cannot be specified with a representation "
                                        "for the {0} frame.".format(self.__class__))
                elif len(args) < 3:
                    # If we have either args(Tx) and rest kwargs, or args(Tx, Ty) and rest kwargs.
                    if 'distance' not in kwargs and 'zeta' in kwargs:
                        kwargs['distance'] = kwargs.get('D0', self.D0) - kwargs['zeta']
                        kwargs.pop('zeta')
                    elif 'distance' not in kwargs and 'zeta' not in kwargs:
                        kwargs['distance'] = (1*u.au).to(u.km)
                    elif 'distance' in kwargs and 'zeta' in kwargs:
                        raise TypeError("zeta and distance cannot both be "
                                        "specified in the {0} frame.".format(self.__class__))
                elif len(args) == 3:
                    # If we have args(Tx, Ty, distance).
                    if 'zeta' in kwargs:
                        raise TypeError("zeta and distance cannot both "
                                        "be specified here for the {0} frame.".format(self.__class__))
            elif not kwargs:
                # The case when kwargs are not present.
                if len(args) == 2:
                    # args(Tx, Ty) provided.
                    args = list(args)
                    args.append((1*u.au).to(u.km))
                    args = tuple(args)
            elif not args:
                # The case when args are not present.
                if 'distance' not in kwargs and 'zeta' in kwargs:
                    kwargs['distance'] = kwargs.get('D0', self.D0) - kwargs['zeta']
                    kwargs.pop('zeta')
                elif 'distance' not in kwargs and 'zeta' not in kwargs:
                    if 'Tx' in kwargs and 'Ty' in kwargs or 'lon' in kwargs and 'lat' in kwargs:
                        # This if clause was added to deal with a frame
                        # which does not have Tx, Ty, distance but may
                        # have other kwargs (FrameAttributes).
                        kwargs['distance'] = (1*u.au).to(u.km)
                elif 'distance' in kwargs and 'zeta' in kwargs:
                    raise TypeError("zeta and distance cannot both be "
                                    "specified here for the {0} frame.".format(self.__class__))
        # Finally, make a call to the super constructor.
        super(HelioProjective, self).__init__(*args, **kwargs)
           
    # Note that Trho = Drho + 90, and Drho is the declination parameter.
    # According to Thompson, we use Trho internally and Drho as part of
    # the (Drho, psi) pair when defining a coordinate in this system.

# ------------------ Transformation Framework -------------------------
# This portion is reserved for the implementation of transformations
# as defined by Thompson.

@frame_transform_graph.transform(FunctionTransform, HelioGraphicStonyhurst, HelioGraphicCarrington)
def hcs_to_hcg(hcscoord, hcgframe):
    c_lon = hcscoord.spherical.lon + _carrington_offset() * u.deg
    representation = SphericalRepresentation(c_lon, hcscoord.hlat, hcscoord.rad)
    return HelioGraphicCarrington(representation)

@frame_transform_graph.transform(FunctionTransform, HelioGraphicCarrington, HelioGraphicStonyhurst)
def hcg_to_hcs(hcgcoord, hcsframe):
    s_lon = hcgcoord.spherical.lon - _carrington_offset() * u.deg
    representation = SphericalRepresentation(s_lon, hcgcoord.hlat, hcgcoord.rad)
    return HelioGraphicStonyhurst(representation)

@frame_transform_graph.transform(FunctionTransform, HelioCentric, HelioProjective)
def helioc_to_heliop(helioccoord, heliopframe):
    x = helioccoord.x.to(u.m)
    y = helioccoord.y.to(u.m)
    z = helioccoord.z.to(u.m)

    # d is calculated as the distance between the points
    # (x,y,z) and (0,0,D0).
    distance = np.sqrt(x**2 + y**2 + (helioccoord.D0.to(u.m) - z)**2)

    hpcx = np.rad2deg(np.arctan2(x, helioccoord.D0 - z))
    hpcy = np.rad2deg(np.arcsin(y / distance))

    representation = SphericalRepresentation(hpcx, hpcy, distance.to(u.km))
    return HelioProjective(representation)

@frame_transform_graph.transform(FunctionTransform, HelioProjective, HelioCentric)
def heliop_to_helioc(heliopcoord, heliocframe):
    x = np.deg2rad(heliopcoord.Tx)
    y = np.deg2rad(heliopcoord.Ty)

    cosx = np.cos(x)
    sinx = np.sin(x)
    cosy = np.cos(y)
    siny = np.sin(y)

    rx = (heliopcoord.distance.to(u.m)) * cosy * sinx
    ry = (heliopcoord.distance.to(u.m)) * siny
    rz = (heliopcoord.D0.to(u.m)) - (heliopcoord.distance.to(u.m)) * cosy * cosx

    representation = CartesianRepresentation(rx.to(u.km), ry.to(u.km), rz.to(u.km))
    return HelioCentric(representation)

@frame_transform_graph.transform(FunctionTransform, HelioCentric, HelioGraphicStonyhurst)
def hcc_to_hgs(helioccoord, heliogframe):
    x = helioccoord.x.to(u.m)
    y = helioccoord.y.to(u.m)
    z = helioccoord.z.to(u.m)

    l0_deg = _carrington_offset() * u.deg
    b0_deg = s.heliographic_solar_center()[1] * u.deg

    cosb = np.cos(np.deg2rad(b0_deg))
    sinb = np.sin(np.deg2rad(b0_deg))

    hecr = np.sqrt(x**2 + y**2 + z**2)
    hgln = np.arctan2(x, z * cosb - y * sinb) + np.deg2rad(l0_deg)
    hglt = np.arcsin((y * cosb + z * sinb) / hecr)

    representation = SphericalRepresentation(np.rad2deg(hgln),
                                             np.rad2deg(hglt),
                                             hecr.to(u.km))
    return HelioGraphicStonyhurst(representation)

@frame_transform_graph.transform(FunctionTransform, HelioGraphicStonyhurst, HelioCentric)
def hgs_to_hcc(heliogcoord, heliopframe):
    hglon = heliogcoord.hlon
    hglat = heliogcoord.hlat
    r = heliogcoord.rad.to(u.m)

    l0_deg = _carrington_offset() * u.deg
    b0_deg = s.heliographic_solar_center()[1] * u.deg

    lon = np.deg2rad(hglon)
    lat = np.deg2rad(hglat)

    cosb = np.cos(np.deg2rad(b0_deg))
    sinb = np.sin(np.deg2rad(b0_deg))

    lon = lon - np.deg2rad(l0_deg)

    cosx = np.cos(lon)
    sinx = np.sin(lon)
    cosy = np.cos(lat)
    siny = np.sin(lat)

    x = r * cosy * sinx
    y = r * (siny * cosb - cosy * cosx * sinb)
    zz = r * (siny * sinb + cosy * cosx * cosb)

    representation = CartesianRepresentation(x.to(u.km), y.to(u.km), zz.to(u.km))
    return HelioCentric(representation)
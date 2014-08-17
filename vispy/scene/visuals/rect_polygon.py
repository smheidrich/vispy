# -*- coding: utf-8 -*-
# Copradiusight (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple ellipse visual based on PolygonVisual
"""

from __future__ import division

import numpy as np
from ... import gloo
from ...color import Color
from .polygon import Polygon, Mesh, Line


class RectPolygon(Polygon):
    """
Displays a 2D rectangle
pos = center of rectangle
height = length of the rectangle along y-axis
width = length of the rectangle along x-axis
radius = radii of curvatures of corners in anti-clockwise order from top-right
"""
    def __init__(self, pos=None, color='black', border_color=None,
                 height=1.0, width=1.0, radius=[0., 0., 0., 0.], **kwds):
        super(RectPolygon, self).__init__()
        self._vertices = None
        self._pos = pos
        self._color = Color(color)
        self._border_color = Color(border_color)
        self._radius = radius
        self._height = height
        self._width = width
        self._update()

    def _generate_vertices(self, pos, radius, height, width):

        hw = min(height/2., width/2.)

        if isinstance(radius, (list, tuple)):
            if len(radius) != 4:
                raise ValueError("radius must be float or 4 value tuple/list"
                                 " (got %s of length %d)" % (type(radius),
                                                             len(radius)))

            if (radius > np.full(4, hw)).all():
                raise ValueError('Radius of curvature cannot be greater than\
                                  half of min(width, height)')
            radius = np.array(radius, dtype=np.float32)

        else:
            if radius > hw:
                raise ValueError('Radius of curvature cannot be greater than\
                                  half of min(width, height)')
            radius = np.full(4, radius)

        num_segments = (radius/hw * 500.).astype(int)

        bias1 = np.full(4, width / 2.) - radius
        bias2 = np.full(4, height / 2.) - radius

        corner1 = np.empty([num_segments[0]+1, 3], dtype=np.float32)
        corner2 = np.empty([num_segments[1]+1, 3], dtype=np.float32)
        corner3 = np.empty([num_segments[2]+1, 3], dtype=np.float32)
        corner4 = np.empty([num_segments[3]+1, 3], dtype=np.float32)

        start_angle = 0.
        end_angle = np.pi / 2.

        theta = np.linspace(start_angle, end_angle, num_segments[0]+1)

        corner1[:, 0] = pos[0] + bias1[0] + radius[0] * np.cos(theta)
        corner1[:, 1] = pos[1] - bias2[0] - radius[0] * np.sin(theta)
        corner1[:, 2] = 0

        theta = np.linspace(end_angle, start_angle, num_segments[1]+1)

        corner2[:, 0] = pos[0] - bias1[1] - radius[1] * np.cos(theta)
        corner2[:, 1] = pos[1] - bias2[1] - radius[1] * np.sin(theta)
        corner2[:, 2] = 0

        theta = np.linspace(start_angle, end_angle, num_segments[2]+1)

        corner3[:, 0] = pos[0] - bias1[2] - radius[2] * np.cos(theta)
        corner3[:, 1] = pos[1] + bias2[2] + radius[2] * np.sin(theta)
        corner3[:, 2] = 0

        theta = np.linspace(end_angle, start_angle, num_segments[3]+1)

        corner4[:, 0] = pos[0] + bias1[3] + radius[3] * np.cos(theta)
        corner4[:, 1] = pos[1] + bias2[3] + radius[3] * np.sin(theta)
        corner4[:, 2] = 0

        output = np.concatenate(([[pos[0], pos[1], 0.], 
                                  [pos[0] + width / 2., pos[1], 0.]],
                                 corner1, [[pos[0], pos[1] - height / 2., 0.]],
                                 corner2, [[pos[0] - width / 2., pos[1], 0.]],
                                 corner3, [[pos[0], pos[1] + height / 2., 0.]],
                                 corner4, [[pos[0] + width / 2., pos[1], 0.]]))

        self._vertices = np.array(output, dtype=np.float32)

    @property
    def radius(self):
        """ The radius of curvature of rounded corners.
        """
        return self._radius

    @radius.setter
    def radius(self, radius):
        self._radius = radius
        self._update()
    
    def _update(self):
        if self._pos is not None:
            self._generate_vertices(pos=self._pos, radius=self._radius,
                                    height=self._height, width=self._width,
                                    )
            self.mesh = Mesh(pos=self._vertices, color=self._color.rgba)
            self.mesh._primitive = gloo.gl.GL_TRIANGLE_FAN
            if not self._border_color.is_blank():
                self.border = Line(pos=self._vertices[1:],
                                   color=self._border_color.rgba)
        #self.update()

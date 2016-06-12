#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of pymanoid.
#
# pymanoid is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymanoid is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# pymanoid. If not, see <http://www.gnu.org/licenses/>.


from cdd import Matrix, Polyhedron, RepType
from numpy import array, hstack, zeros


NUMBER_TYPE = 'float'  # 'float' or 'fraction'


class ConeException(Exception):

    def __init__(self, M):
        self.M = M


class NotConeFace(ConeException):

    def __str__(self):
        return "Matrix is not a cone face"


class NotConeSpan(ConeException):

    def __str__(self):
        return "Matrix is not a cone span"


def face_of_span(S):
    """

    Returns the face matrix S^F of the span matrix S,
    that is, a matrix such that

        {x = S z, z >= 0} if and only if {S^F x <= 0}.

    """
    V = hstack([zeros((S.shape[1], 1)), S.T])
    # V-representation: first column is 0 for rays
    V_cdd = Matrix(V, number_type=NUMBER_TYPE)
    V_cdd.rep_type = RepType.GENERATOR
    P = Polyhedron(V_cdd)
    H = array(P.get_inequalities())
    b, A = H[:, 0], H[:, 1:]
    for i in xrange(H.shape[0]):
        if b[i] != 0:
            raise NotConeSpan(S)
    return -A


def span_of_face(F):
    """

    Compute the span matrix F^S of the face matrix F,
    that is, a matrix such that

        {F x <= 0} if and only if {x = F^S z, z >= 0}.

    """
    b, A = zeros((F.shape[0], 1)), -F
    # H-representation: A x + b >= 0
    F_cdd = Matrix(hstack([b, A]), number_type=NUMBER_TYPE)
    F_cdd.rep_type = RepType.INEQUALITY
    P = Polyhedron(F_cdd)
    V = array(P.get_generators())
    for i in xrange(V.shape[0]):
        if V[i, 0] != 0:  # 1 = vertex, 0 = ray
            raise NotConeFace(F)
    return V[:, 1:]

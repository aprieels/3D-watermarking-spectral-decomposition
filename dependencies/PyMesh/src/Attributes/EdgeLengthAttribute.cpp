/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#include "EdgeLengthAttribute.h"

#include <Mesh.h>

using namespace PyMesh;

void EdgeLengthAttribute::compute_from_mesh(Mesh& mesh) {
    if (!mesh.has_attribute("edge_squared_length")) {
        mesh.add_attribute("edge_squared_length");
    }

    VectorF& edge_len = m_values;
    const auto& sq_len = mesh.get_attribute("edge_squared_length");
    edge_len.resize(sq_len.rows(), sq_len.cols());
    edge_len = sq_len.array().sqrt();
}

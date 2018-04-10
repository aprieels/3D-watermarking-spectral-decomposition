/* This file is part of PyMesh. Copyright (c) 2017 by Qingnan Zhou */
#pragma once

#include "MeshAttribute.h"

namespace PyMesh {

class VoxelIncenterAttribute : public MeshAttribute {
    public:
        VoxelIncenterAttribute(const std::string& name) : MeshAttribute(name) {}
        virtual ~VoxelIncenterAttribute() = default;

    public:
        virtual void compute_from_mesh(Mesh& mesh);
};

}

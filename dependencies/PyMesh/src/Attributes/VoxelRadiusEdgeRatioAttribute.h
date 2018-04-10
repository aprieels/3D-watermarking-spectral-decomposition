/* This file is part of PyMesh. Copyright (c) 2017 by Qingnan Zhou */
#pragma once

#include "MeshAttribute.h"

namespace PyMesh {

class Mesh;

class VoxelRadiusEdgeRatioAttribute : public MeshAttribute {
    public:
        VoxelRadiusEdgeRatioAttribute(const std::string& name)
            : MeshAttribute(name) {}
        virtual ~VoxelRadiusEdgeRatioAttribute()=default;

    public:
        virtual void compute_from_mesh(Mesh& mesh);
};

}

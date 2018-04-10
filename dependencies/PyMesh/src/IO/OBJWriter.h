/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once

#include <Mesh.h>
#include "MeshWriter.h"

namespace PyMesh {

class OBJWriter : public MeshWriter {
    public:
        virtual ~OBJWriter() = default;

    public:
        virtual void with_attribute(const std::string& attr_name) override;
        virtual void write_mesh(Mesh& mesh) override;
        virtual void write(
                const VectorF& vertices,
                const VectorI& faces,
                const VectorI& voxels,
                size_t dim,
                size_t vertex_per_face,
                size_t vertex_per_voxel) override;
};

}

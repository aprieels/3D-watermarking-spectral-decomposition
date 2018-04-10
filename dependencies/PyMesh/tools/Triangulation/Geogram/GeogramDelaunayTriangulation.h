/* This file is part of PyMesh. Copyright (c) 2016 by Qingnan Zhou */
#pragma once

#include "Triangulation.h"
#include <Geogram/GeogramBase.h>

namespace PyMesh {
    class GeogramDelaunayTriangulation : public Triangulation,
                                         public GeogramBase {
        public:
            GeogramDelaunayTriangulation() = default;
            virtual ~GeogramDelaunayTriangulation() = default;

        public:
            virtual void run();
    };
}

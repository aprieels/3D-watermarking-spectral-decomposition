/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once

#include "../BooleanEngineTest.h"

class IGLEngineTest : public BooleanEngineTest {
    protected:
        BooleanPtr get_disjoint_setting(MeshPtr mesh) {
            BooleanPtr igl_engine = BooleanEngine::create("igl");

            MatrixFr vertices_1 = extract_vertices(mesh);
            MatrixIr faces_1    = extract_faces(mesh);

            VectorF bbox_min = vertices_1.colwise().minCoeff();
            VectorF bbox_max = vertices_1.colwise().maxCoeff();
            VectorF bbox_size = bbox_max - bbox_min;

            MatrixFr vertices_2 = vertices_1;
            translate(vertices_2, bbox_size * 2);

            igl_engine->set_mesh_1(vertices_1, faces_1);
            igl_engine->set_mesh_2(vertices_2, faces_1);
            return igl_engine;
        }

        BooleanPtr get_overlap_setting(MeshPtr mesh) {
            BooleanPtr igl_engine = BooleanEngine::create("igl");

            MatrixFr vertices_1 = extract_vertices(mesh);
            MatrixIr faces_1    = extract_faces(mesh);

            VectorF bbox_min = vertices_1.colwise().minCoeff();
            VectorF bbox_max = vertices_1.colwise().maxCoeff();
            VectorF bbox_size = bbox_max - bbox_min;

            MatrixFr vertices_2 = vertices_1;
            translate(vertices_2, bbox_size * 0.5);

            igl_engine->set_mesh_1(vertices_1, faces_1);
            igl_engine->set_mesh_2(vertices_2, faces_1);
            return igl_engine;
        }

        BooleanPtr get_epsilon_box_setting(
                const MatrixFr& vertices, const MatrixIr& faces,
                const VectorF& p, const Float EPS=0.1) {
            MatrixFr box_vertices;
            MatrixIr box_faces;
            generate_epsilon_box(p, box_vertices, box_faces, EPS);

            BooleanPtr igl_engine = BooleanEngine::create("igl");
            igl_engine->set_mesh_1(vertices, faces);
            igl_engine->set_mesh_2(box_vertices, box_faces);
            igl_engine->compute_intersection();
            return igl_engine;
        }

        void assert_interior(const MatrixFr& vertices, const MatrixIr& faces,
                const VectorF& p) {
            const Float EPS = 0.1;
            BooleanPtr igl_engine = get_epsilon_box_setting(vertices, faces, p, EPS);

            const MatrixFr& vts = igl_engine->get_vertices();
            VectorF bbox_max = vts.colwise().maxCoeff();
            VectorF bbox_min = vts.colwise().minCoeff();
            VectorF bbox_size = bbox_max - bbox_min;

            ASSERT_FLOAT_EQ(EPS*2, bbox_size.maxCoeff());
            ASSERT_FLOAT_EQ(EPS*2, bbox_size.minCoeff());
        }

        void assert_on_boundary(const MatrixFr& vertices, const MatrixIr& faces,
                const VectorF& p) {
            const Float EPS = 0.1;
            BooleanPtr igl_engine = get_epsilon_box_setting(vertices, faces, p, EPS);

            const MatrixFr& vts = igl_engine->get_vertices();
            VectorF bbox_max = vts.colwise().maxCoeff();
            VectorF bbox_min = vts.colwise().minCoeff();
            VectorF bbox_size = bbox_max - bbox_min;

            // The intersection of epsilon box with the given shape would
            // 1. cut off one or more corners of the epsilon box, in which case
            //    the number of verticing should be > 8.
            // 2. if the number of vertices <= 8, then the bbox of the
            //    intersection must be smaller than the epsilon box.
            ASSERT_TRUE(vts.rows() > 8 || EPS*2 > bbox_size.minCoeff());
        }

        void assert_exterior(const MatrixFr& vertices, const MatrixIr& faces,
                const VectorF& p) {
            const Float EPS = 0.1;
            BooleanPtr igl_engine = get_epsilon_box_setting(vertices, faces, p, EPS);
            ASSERT_EQ(0, igl_engine->get_vertices().rows());
        }

        void generate_epsilon_box(const VectorF& p,
                MatrixFr& vertices, MatrixIr& faces, Float epsilon) {
            const size_t dim = p.size();
            if (dim == 3) {
                vertices.resize(8, dim);
                vertices << p[0]-epsilon, p[1]-epsilon, p[2]-epsilon,
                            p[0]+epsilon, p[1]-epsilon, p[2]-epsilon,
                            p[0]+epsilon, p[1]+epsilon, p[2]-epsilon,
                            p[0]-epsilon, p[1]+epsilon, p[2]-epsilon,
                            p[0]-epsilon, p[1]-epsilon, p[2]+epsilon,
                            p[0]+epsilon, p[1]-epsilon, p[2]+epsilon,
                            p[0]+epsilon, p[1]+epsilon, p[2]+epsilon,
                            p[0]-epsilon, p[1]+epsilon, p[2]+epsilon;
                faces.resize(12, 3);
                faces << 0, 3, 1,
                         1, 3, 2,
                         4, 5, 7,
                         7, 5, 6,
                         5, 1, 2,
                         5, 2, 6,
                         4, 7, 3,
                         4, 3, 0,
                         0, 1, 5,
                         0, 5, 4,
                         2, 3, 6,
                         3, 7, 6;
            } else {
                throw NotImplementedError("Only 3D epsilon box is supported.");
            }
        }
};

TEST_F(IGLEngineTest, disjoint_union) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_disjoint_setting(mesh);
    igl_engine->compute_union();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    const size_t num_vertices = mesh->get_num_vertices();
    const size_t num_faces = mesh->get_num_faces();
    ASSERT_EQ(num_vertices * 2, vertices.rows());
    ASSERT_EQ(num_faces * 2, faces.rows());
}

TEST_F(IGLEngineTest, disjoint_intersection) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_disjoint_setting(mesh);
    igl_engine->compute_intersection();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    ASSERT_EQ(0, vertices.rows());
    ASSERT_EQ(0, faces.rows());
}

TEST_F(IGLEngineTest, disjoint_difference) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_disjoint_setting(mesh);
    igl_engine->compute_difference();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    const size_t num_vertices = mesh->get_num_vertices();
    const size_t num_faces = mesh->get_num_faces();
    ASSERT_EQ(num_vertices, vertices.rows());
    ASSERT_EQ(num_faces, faces.rows());
}

TEST_F(IGLEngineTest, disjoint_symmetric_difference) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_disjoint_setting(mesh);
    igl_engine->compute_symmetric_difference();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    const size_t num_vertices = mesh->get_num_vertices();
    const size_t num_faces = mesh->get_num_faces();
    ASSERT_EQ(num_vertices * 2, vertices.rows());
    ASSERT_EQ(num_faces * 2, faces.rows());
}

TEST_F(IGLEngineTest, overlap_union) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_overlap_setting(mesh);
    igl_engine->compute_union();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    VectorF origin = VectorF::Zero(3);
    VectorF corner = VectorF::Ones(3);
    assert_interior(vertices, faces, origin);
    assert_interior(vertices, faces, corner);
    assert_on_boundary(vertices, faces, -corner);
}

TEST_F(IGLEngineTest, overlap_intersection) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_overlap_setting(mesh);
    igl_engine->compute_intersection();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    VectorF origin = VectorF::Zero(3);
    VectorF corner = VectorF::Ones(3);
    assert_on_boundary(vertices, faces, origin);
    assert_on_boundary(vertices, faces, corner);
    assert_exterior(vertices, faces, -corner);
}

TEST_F(IGLEngineTest, overlap_difference) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_overlap_setting(mesh);
    igl_engine->compute_difference();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    VectorF origin = VectorF::Zero(3);
    VectorF corner = VectorF::Ones(3);
    assert_on_boundary(vertices, faces, origin);
    assert_exterior(vertices, faces, corner);
    assert_on_boundary(vertices, faces, -corner);
}

TEST_F(IGLEngineTest, overlap_symmetric_difference) {
    MeshPtr mesh = load_mesh("cube.obj");

    BooleanPtr igl_engine = get_overlap_setting(mesh);
    igl_engine->compute_symmetric_difference();

    const MatrixFr& vertices = igl_engine->get_vertices();
    const MatrixIr& faces = igl_engine->get_faces();

    VectorF origin = VectorF::Zero(3);
    VectorF corner = VectorF::Ones(3);
    assert_on_boundary(vertices, faces, origin);
    assert_on_boundary(vertices, faces, corner);
    assert_on_boundary(vertices, faces, -corner);
}

TEST_F(IGLEngineTest, open_surface) {
    MeshPtr mesh = load_mesh("cube.obj");
    MatrixFr box_vertices = extract_vertices(mesh);
    MatrixIr box_faces = extract_faces(mesh);

    MatrixFr tri_vertices(3, 3);
    MatrixIr tri_faces(1, 3);
    tri_vertices << 0.0, 0.0, 0.0,
                    9.0, 0.0, 0.0,
                    0.0, 9.0, 0.0;
    tri_faces << 0, 1, 2;

    BooleanPtr igl_engine = BooleanEngine::create("igl");
    igl_engine->set_mesh_1(box_vertices, box_faces);
    igl_engine->set_mesh_2(tri_vertices, tri_faces);
    //igl_engine->compute_intersection();

    // LIBIGL does not handle open surface.
}

TEST_F(IGLEngineTest, face_source) {
    MeshPtr mesh = load_mesh("cube.obj");
    BooleanPtr igl_engine = get_disjoint_setting(mesh);
    igl_engine->compute_union();
    VectorI face_sources = igl_engine->get_face_sources();
    const MatrixIr& faces = igl_engine->get_faces();

    ASSERT_EQ(faces.rows(), face_sources.size());
    ASSERT_TRUE(face_sources.maxCoeff() < mesh->get_num_faces() * 2);
}

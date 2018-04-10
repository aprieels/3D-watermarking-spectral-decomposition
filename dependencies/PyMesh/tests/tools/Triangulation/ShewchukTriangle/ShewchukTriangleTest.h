/* This file is part of PyMesh. Copyright (c) 2016 by Qingnan Zhou */
#pragma once

#include "../TriangulationTest.h"

class ShewchukTriangulationTest : public TriangulationTest {
};

TEST_F(ShewchukTriangulationTest, simple) {
    MatrixFr points(3, 2);
    points << 0.0, 0.0,
              1.0, 0.0,
              0.0, 1.0;

    Triangulation::Ptr t = Triangulation::create("shewchuk_triangle");
    t->set_vertices(points);
    t->run();
    MatrixIr faces = t->get_faces();
    ASSERT_EQ(1, faces.rows());
    ASSERT_TRUE(
            (faces(0, 0) == 0 && faces(0, 1) == 1 && faces(0, 2) == 2) ||
            (faces(0, 0) == 1 && faces(0, 1) == 2 && faces(0, 2) == 0) ||
            (faces(0, 0) == 2 && faces(0, 1) == 0 && faces(0, 2) == 1));
    assert_valid_triangulation(points, faces);
}

TEST_F(ShewchukTriangulationTest, simple2) {
    MatrixFr points(4, 2);
    points << 0.0, 0.0,
              0.5, 0.0,
              1.0, 0.0,
              0.0, 1.0;

    Triangulation::Ptr t = Triangulation::create("shewchuk_triangle");
    t->set_vertices(points);
    t->run();
    MatrixIr faces = t->get_faces();
    ASSERT_EQ(2, faces.rows());
    assert_valid_triangulation(points, faces);
}

TEST_F(ShewchukTriangulationTest, simple3) {
    MatrixFr points(4, 2);
    points << 0.0, 0.0,
              1.0, 0.0,
              1.0, 1.0,
              0.0, 1.0;

    Triangulation::Ptr t = Triangulation::create("shewchuk_triangle");
    t->set_vertices(points);
    t->run();
    MatrixIr faces = t->get_faces();
    ASSERT_EQ(2, faces.rows());
    assert_valid_triangulation(points, faces);
}

TEST_F(ShewchukTriangulationTest, degenerate) {
    MatrixFr points(3, 2);
    points << 0.0, 0.0,
              0.5, 0.0,
              1.0, 0.0;

    Triangulation::Ptr t = Triangulation::create("shewchuk_triangle");
    t->set_vertices(points);
    t->run();
    MatrixIr faces = t->get_faces();
    ASSERT_EQ(0, faces.rows());
}


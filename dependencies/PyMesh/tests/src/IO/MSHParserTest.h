/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once
#include <string>
#include <memory>
#include <IO/MeshParser.h>

#include <TestBase.h>

class MSHParserTest : public TestBase {
    protected:
        void parse(const std::string& mesh_file) {
            m_parser = std::shared_ptr<MeshParser>(MeshParser::create_parser(mesh_file));
            bool result = m_parser->parse(mesh_file);
            ASSERT_TRUE(result);
        }

    protected:
        std::shared_ptr<MeshParser> m_parser;
};

TEST_F(MSHParserTest, ParseCube) {
    std::string mesh_file = m_data_dir + "cube.msh";
    parse(mesh_file);
    ASSERT_EQ(8, m_parser->num_vertices());
    ASSERT_EQ(12, m_parser->num_faces());
    ASSERT_EQ(6, m_parser->num_voxels());
    ASSERT_EQ(4, m_parser->vertex_per_voxel());
    ASSERT_EQ(3, m_parser->vertex_per_face());
    ASSERT_EQ(3, m_parser->dim());
}

TEST_F(MSHParserTest, ParseTet) {
    std::string mesh_file = m_data_dir + "tet.msh";
    parse(mesh_file);
    ASSERT_EQ(4, m_parser->num_vertices());
    ASSERT_EQ(4, m_parser->num_faces());
    ASSERT_EQ(1, m_parser->num_voxels());
    ASSERT_EQ(4, m_parser->vertex_per_voxel());
    ASSERT_EQ(3, m_parser->vertex_per_face());
    ASSERT_EQ(3, m_parser->dim());
}

TEST_F(MSHParserTest, ParseHex) {
    std::string mesh_file = m_data_dir + "hex.msh";
    parse(mesh_file);
    ASSERT_EQ(8, m_parser->num_vertices());
    ASSERT_EQ(6, m_parser->num_faces());
    ASSERT_EQ(1, m_parser->num_voxels());
    ASSERT_EQ(8, m_parser->vertex_per_voxel());
    ASSERT_EQ(4, m_parser->vertex_per_face());
    ASSERT_EQ(3, m_parser->dim());
}

TEST_F(MSHParserTest, TetCentroid) {
    std::string mesh_file = m_data_dir + "tet.msh";
    parse(mesh_file);

    const size_t num_vertices = m_parser->num_vertices();
    const size_t dim = m_parser->dim();

    VectorF vertices(num_vertices * dim);
    m_parser->export_vertices(vertices.data());
    Float coord_sum = vertices.sum();
    ASSERT_NEAR(0.0, coord_sum, 1e-6);
}

TEST_F(MSHParserTest, HexCentroid) {
    std::string mesh_file = m_data_dir + "hex.msh";
    parse(mesh_file);

    const size_t num_vertices = m_parser->num_vertices();
    const size_t dim = m_parser->dim();

    VectorF vertices(num_vertices * dim);
    m_parser->export_vertices(vertices.data());
    Float coord_sum = vertices.sum();
    ASSERT_NEAR(0.0, coord_sum, 1e-6);
}

TEST_F(MSHParserTest, Empty) {
    std::string mesh_file = m_data_dir + "empty.msh";
    parse(mesh_file);

    ASSERT_EQ(0, m_parser->num_vertices());
    ASSERT_EQ(0, m_parser->num_faces());
}

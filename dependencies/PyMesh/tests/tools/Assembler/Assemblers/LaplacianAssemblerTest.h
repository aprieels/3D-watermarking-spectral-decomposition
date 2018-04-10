/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once
#include "AssemblerTest.h"

#include <Assembler/Assemblers/LaplacianAssembler.h>

class LaplacianAssemblerTest : public AssemblerTest {
    protected:
        virtual void init_assembler() {
            m_assembler = Assembler::Ptr(new LaplacianAssembler());
        }
};

TEST_F(LaplacianAssemblerTest, TetSize) {
    FESettingPtr setting = load_setting("tet.msh");
    ZSparseMatrix L = m_assembler->assemble(setting);
    ASSERT_EQ(4, L.rows());
    ASSERT_EQ(4, L.cols());
}

TEST_F(LaplacianAssemblerTest, SquareSize) {
    FESettingPtr setting = load_setting("square_2D.obj");
    ZSparseMatrix L = m_assembler->assemble(setting);
    ASSERT_EQ(4, L.rows());
    ASSERT_EQ(4, L.cols());
}

TEST_F(LaplacianAssemblerTest, TetPositiveDiagonal) {
    FESettingPtr setting = load_setting("tet.msh");
    ZSparseMatrix L = m_assembler->assemble(setting);
    for (size_t i=0; i<L.rows(); i++) {
        ASSERT_GT(L.coeff(i, i), 0.0);
    }
}

TEST_F(LaplacianAssemblerTest, SquarePositiveDiagonal) {
    FESettingPtr setting = load_setting("square_2D.obj");
    ZSparseMatrix L = m_assembler->assemble(setting);
    for (size_t i=0; i<L.rows(); i++) {
        ASSERT_GT(L.coeff(i, i), 0.0);
    }
}

TEST_F(LaplacianAssemblerTest, LaplacianBeltrami) {
    FESettingPtr setting = load_setting("ball.msh");
    auto mesh = setting->get_mesh();
    ZSparseMatrix L = m_assembler->assemble(setting);
    ASSERT_EQ(mesh->getNbrNodes(), L.rows());
    for (size_t i=0; i<L.rows(); i++) {
        ASSERT_GT(L.coeff(i, i), 0.0);
    }

    VectorF v(mesh->getNbrNodes());
    v.setConstant(1.1);
    VectorF r = L * v;
    ASSERT_NEAR(0.0, r.minCoeff(), 1e-12);
    ASSERT_NEAR(0.0, r.maxCoeff(), 1e-12);
}

add_library(chessplusplus
    ../../src/chessplusplus.cpp
    ../../src/private_utils/chess_utils.cpp
    ../../src/private_utils/fen_utils.cpp
    chessplusplus.h
    ../../private/internal/chess_utils.h
    ../../private/internal/def.h
    ../../private/internal/fen_utils.h)

target_include_directories(chessplusplus
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../>
        $<INSTALL_INTERFACE:..>
    PRIVATE ../../private)

add_library(chessplusplus
    ../../src/chessplusplus.cpp
    ../../src/public_utils/chess.cpp
    ../../src/private_utils/fen_utils.cpp
    chessplusplus.h
    public_utils/definitions.h
    public_utils/chess.h
    ../../private/internal/fen_utils.h
    ../../private/internal/other_utils.h
)

target_include_directories(chessplusplus
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../>
        $<INSTALL_INTERFACE:..>
    PRIVATE
        ../../private)

add_executable(chessplusplus_unit_tests test.cpp
    testutils/randomfengenerator.h
    fen.cpp)
target_link_libraries(
  chessplusplus_unit_tests PRIVATE
  GTest::gtest_main
)
target_link_libraries(chessplusplus_unit_tests PRIVATE chessplusplus)

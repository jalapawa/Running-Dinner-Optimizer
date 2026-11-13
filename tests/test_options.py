from logic.options import haversine


# Coords are (lon, lat), the order Photon returns
AACHEN_DOM = (6.0839, 50.7747)


def test_haversine_one_degree_north_is_about_111_km():
    north = (AACHEN_DOM[0], AACHEN_DOM[1] + 1)
    assert abs(haversine(AACHEN_DOM, north) - 111.2) < 0.5


def test_haversine_one_degree_east_shrinks_with_latitude():
    # At ~50.8° N a degree of longitude is only 111.2 km * cos(50.8°) ≈ 70.3 km
    east = (AACHEN_DOM[0] + 1, AACHEN_DOM[1])
    assert abs(haversine(AACHEN_DOM, east) - 70.3) < 0.5

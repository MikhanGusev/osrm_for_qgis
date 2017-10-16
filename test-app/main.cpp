// based on https://github.com/Project-OSRM/osrm-backend/blob/master/example/example.cpp

#include "osrm/match_parameters.hpp"
#include "osrm/nearest_parameters.hpp"
#include "osrm/route_parameters.hpp"
#include "osrm/table_parameters.hpp"
#include "osrm/trip_parameters.hpp"

#include "osrm/coordinate.hpp"
#include "osrm/engine_config.hpp"
#include "osrm/json_container.hpp"
#include "osrm/util/json_renderer.hpp"

#include "osrm/osrm.hpp"
#include "osrm/status.hpp"

#include <exception>
#include <iostream>
#include <string>
#include <utility>

#include <cstdlib>


int main(int argc, const char *argv[])
{
    if (argc < 7)
    {
        std::cerr << "Usage: " << argv[0] << "lon_start lat_start lon_end lat_end in.osrm out.geojson\n";
        return EXIT_FAILURE;
    }

    using namespace osrm;

    util::FloatLongitude fLonStart {std::stod(argv[1])};
    util::FloatLatitude fLatStart {std::stod(argv[2])};
    util::FloatLongitude fLonEnd {std::stod(argv[3])};
    util::FloatLatitude fLatEnd {std::stod(argv[4])};

    std::string sOutPath = argv[6];

    // Configure based on a .osrm base path, and no datasets in shared mem from osrm-datastore
    EngineConfig config;
    config.storage_config = {argv[5]};
    config.use_shared_memory = false;

    // Routing machine with several services (such as Route, Table, Nearest, Trip, Match)
    const OSRM osrm{config};

    // The following shows how to use the Route service; configure this service
    RouteParameters params;

    params.geometries = RouteParameters::GeometriesType::GeoJSON;
    params.overview = RouteParameters::OverviewType::Simplified;

    // Route
    params.coordinates.push_back({fLonStart, fLatStart});
    params.coordinates.push_back({fLonEnd, fLatEnd});

    // Response is in JSON format
    json::Object result;

    // Execute routing request, this does the heavy lifting
    const auto status = osrm.Route(params, result);

    if (status == Status::Ok)
    {
        auto &routes = result.values["routes"].get<json::Array>();

        // Let's just use the first route
        auto &route = routes.values.at(0).get<json::Object>();
        const auto distance = route.values["distance"].get<json::Number>().value;
        const auto duration = route.values["duration"].get<json::Number>().value;

        std::filebuf fb;
        fb.open(sOutPath, std::ios::out);
        std::ostream os(&fb);
        json::Object jGeom = route.values["geometry"].get<json::Object>();
        osrm::util::json::render(os, jGeom);
        fb.close();

        // Warn users if extract does not contain the default coordinates from above
        if (distance == 0 || duration == 0)
        {
            std::cout << "Note: distance or duration is zero. ";
            std::cout << "You are probably doing a query outside of the OSM extract.\n\n";
        }

        std::cout << "Distance: " << distance << " meter\n";
        std::cout << "Duration: " << duration << " seconds\n";
        return EXIT_SUCCESS;
    }
    else if (status == Status::Error)
    {
        const auto code = result.values["code"].get<json::String>().value;
        const auto message = result.values["message"].get<json::String>().value;

        std::cout << "Code: " << code << "\n";
        std::cout << "Message: " << code << "\n";
        return EXIT_FAILURE;
    }
}




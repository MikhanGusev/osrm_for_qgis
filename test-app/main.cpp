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


void renderJsonObject (std::string sOutPath, osrm::json::Object jObj)
{
    std::filebuf fb;
    fb.open(sOutPath, std::ios::out);
    std::ostream os(&fb);
    osrm::util::json::render(os, jObj);
    fb.close();
}

void renderJsonArray (std::string sOutPath, osrm::json::Array jArray)
{
    std::vector<char> out;
    osrm::util::json::render(out, jArray);
    std::ofstream file(sOutPath, std::ios::out);
    std::copy(out.begin(), out.end(), std::ostreambuf_iterator<char>(file));
}


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

    std::string sOutDirPath = argv[6];

    // Configure based on a .osrm base path, and no datasets in shared mem from osrm-datastore
    EngineConfig config;
    config.storage_config = {argv[5]};
    config.use_shared_memory = false;
    config.algorithm = EngineConfig::Algorithm::MLD;

    // Routing machine with several services (such as Route, Table, Nearest, Trip, Match)
    const OSRM osrm{config};

    // The following shows how to use the Route service; configure this service
    RouteParameters params;
    params.geometries = RouteParameters::GeometriesType::GeoJSON;
    params.overview = RouteParameters::OverviewType::Full;
    params.coordinates.push_back({fLonStart, fLatStart});
    params.coordinates.push_back({fLonEnd, fLatEnd});
    params.steps = true;
    params.annotations = true;

    // Response is in JSON format
    json::Object result;

    // Execute routing request, this does the heavy lifting
    const auto status = osrm.Route(params, result);

    if (status == Status::Ok)
    {
        auto &routes = result.values["routes"].get<json::Array>();
        auto &route = routes.values.at(0).get<json::Object>(); // the first route
        const auto distance = route.values["distance"].get<json::Number>().value;
        const auto duration = route.values["duration"].get<json::Number>().value;
        const auto weight = route.values["weight"].get<json::Number>().value;
        const auto weight_name = route.values["weight_name"].get<json::String>().value;
        //auto &waypoints = result.values["waypoints"].get<json::Array>();

        renderJsonObject(sOutDirPath + "/path.geojson", route.values["geometry"].get<json::Object>());
        renderJsonArray(sOutDirPath + "/path_legs.geojson", route.values["legs"].get<json::Array>());
        //renderJson(sOutDirPath + "/path_waypoints.json", waypoints);

        // Warn users if extract does not contain the default coordinates from above.
        if (distance == 0 || duration == 0)
        {
            std::cout << "Note: distance or duration is zero. ";
            std::cout << "You are probably doing a query outside of the OSM extract.\n\n";
        }

        std::cout << "Distance: " << distance << " meter\n";
        std::cout << "Duration: " << duration << " seconds\n";
        std::cout << "Weight: " << weight << "\n";
        std::cout << "Weight name: " << weight_name << "\n";

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




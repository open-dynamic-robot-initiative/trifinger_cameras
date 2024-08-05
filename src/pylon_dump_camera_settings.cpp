/**
 * @file
 * @brief Connect to Pylon camera and print its settings to stdout.
 * @copyright 2020 Max Planck Gesellschaft.  All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/pylon_driver.hpp>

#include <iostream>

#include <cli_utils/program_options.hpp>

class Args : public cli_utils::ProgramOptions
{
public:
    std::string device_user_id = "";

    std::string help() const override
    {
        return R"(Connect to Pylon camera and print its settings to stdout.

        If no device name is specified, uses the first camera that is found (so make
        sure only one camera is connected in that case).

Usage:  pylon_dump_camera_settings [<device_user_id>]

)";
    }

    // in add_options the arguments are defined
    void add_options(boost::program_options::options_description &options,
                     boost::program_options::positional_options_description
                         &positional) override
    {
        namespace po = boost::program_options;

        // The chaining of parentheses calls does not go well with clang-format,
        // so better disable auto-formatting for this block.

        // clang-format off
        options.add_options()
            ("device_user_id",
             po::value<std::string>(&device_user_id),
             "'DeviceUserID' of the camera.")
            ;
        // clang-format on

        // mark 'message' as positional argument
        positional.add("device_user_id", 1);
    }
};

int main(int argc, char *argv[])
{
    Args args;
    if (!args.parse_args(argc, argv))
    {
        return 1;
    }

    // need braces so that Pylon::CInstantCamera instance is destructed before
    // the end (otherwise segfaults)
    {
        Pylon::CInstantCamera camera;
        try
        {
            trifinger_cameras::pylon_connect(args.device_user_id, &camera);
        }
        catch (const Pylon::GenericException &e)
        {
            std::cerr << "ERROR: " << e.what() << std::endl;
            return 1;
        }
        catch (const std::exception &e)
        {
            std::cerr << "ERROR: " << e.what() << std::endl;
            return 1;
        }

        Pylon::String_t output;
        Pylon::CFeaturePersistence::SaveToString(output, &camera.GetNodeMap());
        std::cout << output << std::endl;

        camera.Close();
    }

    // Releases all pylon resources.
    Pylon::PylonTerminate();

    return 0;
}

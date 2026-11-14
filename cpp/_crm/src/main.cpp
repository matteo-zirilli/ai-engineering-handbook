// main.cpp — load the data, run the user interface, save. Kept deliberately small.
//
// Usage: crm [DATA_FOLDER] [--echo]
//   DATA_FOLDER  folder with customers.csv and interactions.csv (default: "data")
//   --echo       repeat every input line on the output (useful when input comes from a file)
// Exit status: 0 = normal end, 1 = the data could not be saved, 2 = wrong usage.
#include <iostream>
#include <string>

#include "crm/console_ui.hpp"
#include "crm/crm.hpp"
#include "crm/storage.hpp"

int main(int argc, char** argv) {
    std::string folder = "data";
    bool echo = false;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--echo") echo = true;
        else if (!arg.empty() && arg[0] != '-') folder = arg;
        else { std::cerr << "usage: crm [DATA_FOLDER] [--echo]\n"; return 2; }
    }

    crm::Crm crm;
    crm::CsvStorage storage(folder);
    const crm::LoadReport report = storage.load(crm);
    for (const auto& w : report.warnings) std::cerr << "WARNING: " << w << '\n';
    if (!report.warnings.empty())
        std::cerr << "The original files will be kept as *.bak at the first save.\n";
    std::cout << (report.first_run ? "No data files yet: starting with an empty CRM.\n" : "")
              << "Loaded " << report.customers << " customer(s) and " << report.interactions
              << " interaction(s) from '" << folder << "'.\n";

    crm::ConsoleUi ui(crm, storage, std::cin, std::cout, echo);
    const int status = ui.run();

    try {
        storage.save(crm);                       // always save on the way out
        std::cout << "Data saved in '" << folder << "'.\n";
    } catch (const std::exception& e) {
        std::cerr << "ERROR: could not save the data: " << e.what() << '\n';
        return 1;
    }
    return status;
}

// storage.hpp — the only component that knows the format of the data files.
#pragma once

#include <filesystem>
#include <string>
#include <vector>

#include "crm/crm.hpp"

namespace crm {

struct LoadReport {
    bool first_run = false;                 // no data files yet
    std::size_t customers = 0, interactions = 0;
    std::vector<std::string> warnings;      // one per skipped line, with its line number
};

// Two CSV files in one folder: customers.csv and interactions.csv.
class CsvStorage {
public:
    explicit CsvStorage(std::filesystem::path folder);

    // Load into an EMPTY crm. Invalid lines are skipped and reported; never throws for bad data.
    LoadReport load(Crm& crm);
    // Save atomically (temporary file + rename). If the last load skipped lines, the original
    // files are first copied to *.bak, so that no data is lost. Throws std::runtime_error.
    void save(const Crm& crm);

    const std::filesystem::path& folder() const { return folder_; }

private:
    std::filesystem::path folder_;
    bool keep_backup_ = false;
};

}  // namespace crm

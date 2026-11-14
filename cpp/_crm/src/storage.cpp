// storage.cpp — CSV persistence of customers and interactions.
#include "crm/storage.hpp"

#include <fstream>
#include <stdexcept>

#include "crm/text.hpp"

namespace crm {

namespace fs = std::filesystem;

namespace {

const std::vector<std::string> customer_columns = {"id", "first_name", "last_name", "phone", "email", "city"};
const std::vector<std::string> interaction_columns = {
    "id", "customer_id", "kind", "date", "time", "agent", "place",
    "policy_number", "product", "premium_cents", "end_date", "notes"};

// Read a CSV file with the expected header; call on_record(record, line_no) for each data line.
// Returns false if the file does not exist.
template <typename F>
bool read_csv(const fs::path& path, const std::vector<std::string>& columns, LoadReport& report, F on_record) {
    std::ifstream in(path);
    if (!in) return false;
    std::string line;
    std::vector<std::string> fields;
    if (!std::getline(in, line) || !csv_split(line, fields) || fields != columns) {
        report.warnings.push_back(path.filename().string() + ": unexpected header, file ignored");
        return true;
    }
    for (int line_no = 2; std::getline(in, line); ++line_no) {
        if (trim(line).empty()) continue;
        const std::string where = path.filename().string() + " line " + std::to_string(line_no) + ": ";
        if (!csv_split(line, fields)) {
            report.warnings.push_back(where + "unterminated quote, skipped");
            continue;
        }
        if (fields.size() != columns.size()) {
            report.warnings.push_back(where + "expected " + std::to_string(columns.size()) + " fields, found " +
                                      std::to_string(fields.size()) + ", skipped");
            continue;
        }
        Record record;
        for (std::size_t i = 0; i < columns.size(); ++i) record[columns[i]] = fields[i];
        try {
            on_record(record);
        } catch (const std::exception& e) {      // invalid values: skip this line only
            report.warnings.push_back(where + e.what() + ", skipped");
        }
    }
    return true;
}

// Write all lines to a temporary file, then rename it over the target (atomic on POSIX).
void write_atomically(const fs::path& target, const std::vector<std::string>& lines) {
    const fs::path tmp = target.string() + ".tmp";
    {
        std::ofstream out(tmp, std::ios::binary);           // binary: "\n" line ends on every platform
        if (!out) throw std::runtime_error("cannot write " + tmp.string());
        for (const auto& l : lines) out << l << '\n';
        out.flush();
        if (!out) throw std::runtime_error("error while writing " + tmp.string());
    }                                                         // closed here
    fs::rename(tmp, target);                                  // replaces the old file
}

std::uint32_t to_id(const std::string& text, const char* what) {
    const auto v = parse_int(text, 1, UINT32_MAX);
    if (!v) throw std::invalid_argument(std::string("invalid ") + what + " '" + text + "'");
    return static_cast<std::uint32_t>(*v);
}

}  // namespace

CsvStorage::CsvStorage(fs::path folder) : folder_(std::move(folder)) {}

LoadReport CsvStorage::load(Crm& crm) {
    LoadReport report;
    const bool had_customers = read_csv(folder_ / "customers.csv", customer_columns, report,
        [&](const Record& r) {
            crm.insert_customer(Customer(to_id(r.at("id"), "id"),
                {r.at("first_name"), r.at("last_name"), r.at("phone"), r.at("email"), r.at("city")}));
            ++report.customers;
        });
    const bool had_interactions = read_csv(folder_ / "interactions.csv", interaction_columns, report,
        [&](const Record& r) {
            Customer* owner = crm.find(to_id(r.at("customer_id"), "customer id"));
            if (!owner) throw std::invalid_argument("unknown customer " + r.at("customer_id"));
            auto interaction = interaction_from_record(r);
            for (const auto& i : owner->interactions())
                if (i->id() == interaction->id()) throw std::invalid_argument("duplicate interaction id");
            crm.reserve_interaction_id(interaction->id());
            owner->add_interaction(std::move(interaction));
            ++report.interactions;
        });
    report.first_run = !had_customers && !had_interactions;
    keep_backup_ = !report.warnings.empty();
    return report;
}

void CsvStorage::save(const Crm& crm) {
    fs::create_directories(folder_);
    if (keep_backup_) {                       // keep the files exactly as they were found
        for (const char* name : {"customers.csv", "interactions.csv"})
            if (fs::exists(folder_ / name))
                fs::copy_file(folder_ / name, folder_ / (std::string(name) + ".bak"),
                              fs::copy_options::overwrite_existing);
        keep_backup_ = false;
    }
    std::vector<std::string> customers{csv_join(customer_columns)};
    std::vector<std::string> interactions{csv_join(interaction_columns)};
    for (const Customer* c : crm.by_id()) {
        const CustomerData& d = c->data();
        customers.push_back(csv_join({std::to_string(c->id()), d.first_name, d.last_name, d.phone, d.email, d.city}));
        for (const auto& i : c->interactions()) {
            Record r = i->to_record();
            r["customer_id"] = std::to_string(c->id());
            std::vector<std::string> fields;
            for (const auto& col : interaction_columns) fields.push_back(r[col]);   // missing -> ""
            interactions.push_back(csv_join(fields));
        }
    }
    write_atomically(folder_ / "customers.csv", customers);
    write_atomically(folder_ / "interactions.csv", interactions);
}

}  // namespace crm

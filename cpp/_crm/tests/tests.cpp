// tests.cpp — automated checks of the domain, the CSV format, the storage and the UI.
// A minimal test harness (no external library): CHECK records failures and the program
// returns a non-zero exit status if any check failed, so that ctest / CI notice it.
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

#include "crm/console_ui.hpp"
#include "crm/crm.hpp"
#include "crm/storage.hpp"
#include "crm/text.hpp"

namespace fs = std::filesystem;
using namespace crm;          // acceptable in a test .cpp file, never in a header

static int checks = 0, failures = 0;
#define CHECK(cond)                                                                   \
    do {                                                                              \
        ++checks;                                                                     \
        if (!(cond)) { ++failures; std::cout << "FAIL line " << __LINE__ << ": " #cond "\n"; } \
    } while (0)

template <typename F>
bool throws_invalid(F f) {
    try { f(); } catch (const std::invalid_argument&) { return true; }
    return false;
}

static Date D(const char* s) { return *Date::parse(s); }

static fs::path fresh_folder(const std::string& name) {
    const fs::path p = fs::temp_directory_path() / ("crm_tests_" + name);
    fs::remove_all(p);
    fs::create_directories(p);
    return p;
}

static void test_text() {
    CHECK(trim("  a b \t") == "a b");
    CHECK(contains_ci("Ferrari", "ERR") && !contains_ci("Russo", "x"));
    CHECK(parse_int(" 42 ", 0, 100) == 42);
    CHECK(!parse_int("42abc", 0, 100) && !parse_int("", 0, 100) && !parse_int("101", 0, 100));
    CHECK(parse_money("480") == 48000 && parse_money("480.5") == 48050 && parse_money("0,07") == 7);
    CHECK(!parse_money("-5") && !parse_money("1.234") && !parse_money("abc") && !parse_money(""));
    CHECK(format_money(48050) == "480.50" && format_money(7) == "0.07");
    const std::vector<std::string> fields{"a,b", "say \"hi\"", "", "plain"};
    std::vector<std::string> back;
    CHECK(csv_split(csv_join(fields), back) && back == fields);       // round trip
    CHECK(!csv_split("1,\"open", back));                              // unterminated quote
}

static void test_dates() {
    CHECK(Date::parse("2028-02-29").has_value());                     // leap year
    CHECK(!Date::parse("2026-02-29") && !Date::parse("2026-13-01") && !Date::parse("20-11-2026"));
    CHECK(D("2026-01-31") < D("2026-02-01"));
    CHECK(TimeOfDay::parse("09:30")->str() == "09:30" && !TimeOfDay::parse("24:00"));
}

static void test_domain() {
    CHECK(throws_invalid([] { Customer(1, {"", "Rossi", "", "", ""}); }));          // empty first name
    CHECK(throws_invalid([] { Customer(1, {"Ada", "Rossi", "12ab", "", ""}); }));   // bad phone
    CHECK(throws_invalid([] { Customer(1, {"Ada", "Rossi", "", "ada@", ""}); }));   // bad e-mail
    CHECK(throws_invalid([] { Customer(1, {"Ada\nX", "Rossi", "", "", ""}); }));    // line break
    CHECK(throws_invalid([] { Contract(1, D("2026-01-01"), "P1", Product::Car, 0, D("2027-01-01"), ""); }));
    CHECK(throws_invalid([] { Contract(1, D("2026-01-01"), "P1", Product::Car, 100, D("2025-01-01"), ""); }));

    Crm crm;
    const auto rossi = crm.add_customer({"mario", "Rossi", "", "", ""});
    const auto bianchi = crm.add_customer({"Anna", "bianchi", "", "", ""});
    crm.add_customer({"Mario", "Rossi", "333 1234567", "", ""});                       // homonym: allowed
    CHECK(crm.size() == 3 && rossi == 1 && bianchi == 2);
    CHECK(crm.customers().front()->id() == bianchi);                                   // case-insensitive order
    CHECK(crm.search("ROSS").size() == 2 && crm.search("zzz").empty());
    const bool rejected = throws_invalid([&] { crm.add_customer({"", "X", "", "", ""}); });
    CHECK(rejected && crm.size() == 3);                                                // nothing added

    Customer* c = crm.find(rossi);
    c->add_interaction(std::make_unique<Contract>(crm.new_interaction_id(), D("2026-05-01"), "CAR-1",
                                                  Product::Car, 48000, D("2027-04-30"), "theft cover"));
    c->add_interaction(std::make_unique<Appointment>(crm.new_interaction_id(), D("2026-03-10"),
                                                     *TimeOfDay::parse("10:00"), "S. Conti", "", ""));
    CHECK(c->interactions().front()->kind() == "appointment");                          // sorted by date
    CHECK(c->find_interactions("theft").size() == 1 && c->find_interactions("conti").size() == 1);
    CHECK(crm.policy_exists("car-1") && !crm.policy_exists("CAR-2"));
    CHECK(crm.remove_customer(rossi) && crm.find(rossi) == nullptr && crm.interaction_count() == 0);
}

static void test_storage() {
    const fs::path dir = fresh_folder("storage");
    {
        Crm crm;
        CsvStorage s(dir);
        const auto report = s.load(crm);
        CHECK(report.first_run && crm.size() == 0);                                    // missing files
        const auto id = crm.add_customer({"Lucia", "Neri", "", "", "Reggio, Emilia"});  // comma in a field
        crm.find(id)->add_interaction(std::make_unique<Appointment>(
            crm.new_interaction_id(), D("2026-11-20"), *TimeOfDay::parse("15:00"), "P. Greco", "",
            "said \"call me back\""));
        s.save(crm);
    }
    {
        Crm crm;
        CsvStorage s(dir);
        const auto report = s.load(crm);
        CHECK(!report.first_run && report.warnings.empty() && crm.size() == 1 && crm.interaction_count() == 1);
        const Customer* c = crm.customers().front();
        CHECK(c->data().city == "Reggio, Emilia");
        CHECK(c->interactions().front()->notes() == "said \"call me back\"");
        CHECK(crm.new_interaction_id() == 2);                                          // ids continue
    }
    {   // damaged lines are skipped, the rest is kept, and a backup is made at the first save
        std::ofstream(dir / "customers.csv", std::ios::app) << "9,OnlyTwoFields\n10,,Empty,,,\n";
        Crm crm;
        CsvStorage s(dir);
        const auto report = s.load(crm);
        CHECK(crm.size() == 1 && report.warnings.size() == 2);
        s.save(crm);
        CHECK(fs::exists(dir / "customers.csv.bak"));
    }
}

static void test_ui() {
    const fs::path dir = fresh_folder("ui");
    Crm crm;
    CsvStorage s(dir);
    s.load(crm);
    std::istringstream in("x\n9\n2\nAda\n\nLovelace\n12ab\n+44 20 7946 0000\nnot-an-email\n\nLondon\n"
                          "6\n1\n3\nPOL-1\ncar\n2026-02-30\n2026-01-15\n2026-01-01\n2027-01-14\nabc\n480,50\n\n"
                          "1\n0\n0\n");
    std::ostringstream out;
    ConsoleUi ui(crm, s, in, out);
    CHECK(ui.run() == 0);
    CHECK(crm.size() == 1 && crm.interaction_count() == 1);
    const Customer* c = crm.customers().front();
    CHECK(c->data().last_name == "Lovelace" && c->data().email.empty() && c->data().city == "London");
    const auto* k = dynamic_cast<const Contract*>(c->interactions().front().get());
    CHECK(k && k->annual_premium_cents() == 48050);
    CHECK(out.str().find("Please type a number from 0 to 6") != std::string::npos);
    std::istringstream eof_in("2\nGrace\n");                                           // input ends mid-form
    ConsoleUi ui2(crm, s, eof_in, out);
    CHECK(ui2.run() == 0 && crm.size() == 1);                                          // no crash, nothing half-added
}

int main() {
    test_text();
    test_dates();
    test_domain();
    test_storage();
    test_ui();
    std::cout << (checks - failures) << "/" << checks << " checks passed\n";
    return failures == 0 ? 0 : 1;
}

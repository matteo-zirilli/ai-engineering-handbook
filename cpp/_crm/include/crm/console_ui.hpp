// console_ui.hpp — the text user interface: menus, validated input, messages.
// It works on any pair of streams, so tests can drive it with scripted input.
#pragma once

#include <cstdint>
#include <functional>
#include <iosfwd>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

#include "crm/crm.hpp"
#include "crm/date.hpp"
#include "crm/storage.hpp"

namespace crm {

// Thrown when the input ends (Ctrl+D, Ctrl+Z, end of a script): the UI saves and quits.
class InputClosed : public std::runtime_error {
public:
    InputClosed() : std::runtime_error("input closed") {}
};

class ConsoleUi {
public:
    ConsoleUi(Crm& crm, CsvStorage& storage, std::istream& in, std::ostream& out, bool echo = false);
    int run();                                   // returns the exit status for main()

private:
    // ---- validated input (each function asks again until the answer is valid) ----
    std::string read_line(const std::string& prompt);
    int ask_choice(const std::string& prompt, int lo, int hi);
    std::string ask_text(const std::string& prompt, const std::string& current,
                         const std::function<void(const std::string&)>& check);
    Date ask_date(const std::string& prompt);
    TimeOfDay ask_time(const std::string& prompt);
    std::int64_t ask_money(const std::string& prompt);
    Product ask_product();
    bool ask_yes_no(const std::string& prompt);
    std::optional<std::uint32_t> ask_customer_id();          // nullopt = cancelled
    CustomerData ask_customer_data(const CustomerData& current);

    // ---- features ----
    void list_customers();
    void add_customer();
    void search_customers();
    void edit_customer();
    void delete_customer();
    void interactions_menu();
    void list_interactions(const Customer& c);
    void add_appointment(Customer& c);
    void add_contract(Customer& c);
    void search_interactions(const Customer& c);
    void delete_interaction(Customer& c);

    void print_customers(const std::vector<const Customer*>& list);
    void save();                                 // after every change

    Crm& crm_;
    CsvStorage& storage_;
    std::istream& in_;
    std::ostream& out_;
    bool echo_;                                  // repeat the input (for transcripts of scripted runs)
};

}  // namespace crm

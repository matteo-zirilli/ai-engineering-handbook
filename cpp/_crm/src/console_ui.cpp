// console_ui.cpp — menus and dialogues. All interaction with the user lives here.
#include "crm/console_ui.hpp"

#include <iomanip>
#include <iostream>

#include "crm/text.hpp"

namespace crm {

ConsoleUi::ConsoleUi(Crm& crm, CsvStorage& storage, std::istream& in, std::ostream& out, bool echo)
    : crm_(crm), storage_(storage), in_(in), out_(out), echo_(echo) {}

// ======================================================================= main loop
int ConsoleUi::run() {
    try {
        while (true) {
            out_ << "\n==== CRM: " << crm_.size() << " customer(s), " << crm_.interaction_count()
                 << " interaction(s) ====\n"
                 << " 1) List customers\n 2) Add a customer\n 3) Search customers by name\n"
                 << " 4) Edit a customer\n 5) Delete a customer\n 6) Interactions of a customer\n"
                 << " 0) Save and exit\n";
            try {
                switch (ask_choice("Choice: ", 0, 6)) {
                case 1: list_customers(); break;
                case 2: add_customer(); break;
                case 3: search_customers(); break;
                case 4: edit_customer(); break;
                case 5: delete_customer(); break;
                case 6: interactions_menu(); break;
                case 0: out_ << "Goodbye.\n"; return 0;
                }
            } catch (const std::invalid_argument& e) {   // a rule of the domain was violated
                out_ << "  Operation cancelled: " << e.what() << ".\n";
            }
        }
    } catch (const InputClosed&) {
        out_ << "\nEnd of input: leaving the program.\n";
        return 0;                                // main() saves before exiting
    }
}

// ======================================================================= input
std::string ConsoleUi::read_line(const std::string& prompt) {
    out_ << prompt << std::flush;
    std::string line;
    if (!std::getline(in_, line)) throw InputClosed();
    if (echo_) out_ << line << '\n';
    return line;
}

int ConsoleUi::ask_choice(const std::string& prompt, int lo, int hi) {
    while (true) {
        const std::string line = read_line(prompt);
        if (const auto v = parse_int(line, lo, hi)) return static_cast<int>(*v);
        out_ << "  Please type a number from " << lo << " to " << hi << ".\n";
    }
}

std::string ConsoleUi::ask_text(const std::string& prompt, const std::string& current,
                                const std::function<void(const std::string&)>& check) {
    while (true) {
        std::string text = trim(read_line(current.empty() ? prompt : prompt + "[" + current + "] "));
        if (text.empty() && !current.empty()) return current;     // Enter keeps the current value
        if (text == "-" && !current.empty()) text.clear();         // "-" clears an optional field
        try {
            check(text);
            return text;
        } catch (const std::invalid_argument& e) {
            out_ << "  " << e.what() << ". Please try again.\n";
        }
    }
}

Date ConsoleUi::ask_date(const std::string& prompt) {
    while (true) {
        if (const auto d = Date::parse(read_line(prompt + "(YYYY-MM-DD) "))) return *d;
        out_ << "  Not a valid date: use the form 2026-11-20.\n";
    }
}

TimeOfDay ConsoleUi::ask_time(const std::string& prompt) {
    while (true) {
        if (const auto t = TimeOfDay::parse(read_line(prompt + "(HH:MM) "))) return *t;
        out_ << "  Not a valid time: use the form 09:30.\n";
    }
}

std::int64_t ConsoleUi::ask_money(const std::string& prompt) {
    while (true) {
        const auto cents = parse_money(read_line(prompt));
        if (cents && *cents > 0) return *cents;
        out_ << "  Please type a positive amount in euros, e.g. 480 or 480.50.\n";
    }
}

Product ConsoleUi::ask_product() {
    while (true) {
        if (const auto p = parse_product(read_line("Product (car/home/life/health/other): "))) return *p;
        out_ << "  Unknown product.\n";
    }
}

bool ConsoleUi::ask_yes_no(const std::string& prompt) {
    while (true) {
        const std::string a = to_lower(trim(read_line(prompt + " [y/n] ")));
        if (a == "y" || a == "yes") return true;
        if (a == "n" || a == "no") return false;
        out_ << "  Please answer y or n.\n";
    }
}

std::optional<std::uint32_t> ConsoleUi::ask_customer_id() {
    while (true) {
        const std::string line = trim(read_line("Customer id (Enter to cancel): "));
        if (line.empty()) return std::nullopt;
        const auto id = parse_int(line, 1, UINT32_MAX);
        if (id && crm_.find(static_cast<std::uint32_t>(*id))) return static_cast<std::uint32_t>(*id);
        out_ << "  No customer with id '" << line << "'. Use option 1 or 3 to see the ids.\n";
    }
}

CustomerData ConsoleUi::ask_customer_data(const CustomerData& cur) {
    // Each field is checked on its own, with the same rules as Customer::validate.
    auto check_field = [](auto setter) {
        return [setter](const std::string& value) {
            CustomerData d{"x", "x", "", "", ""};
            setter(d, value);
            Customer::validate(d);
        };
    };
    if (!cur.first_name.empty()) out_ << "  (Enter keeps the value in brackets; '-' clears an optional field)\n";
    CustomerData d;
    d.first_name = ask_text("First name: ", cur.first_name, check_field([](CustomerData& x, const std::string& v) { x.first_name = v; }));
    d.last_name  = ask_text("Last name: ", cur.last_name, check_field([](CustomerData& x, const std::string& v) { x.last_name = v; }));
    d.phone      = ask_text("Phone (optional): ", cur.phone, check_field([](CustomerData& x, const std::string& v) { x.phone = v; }));
    d.email      = ask_text("E-mail (optional): ", cur.email, check_field([](CustomerData& x, const std::string& v) { x.email = v; }));
    d.city       = ask_text("City (optional): ", cur.city, check_field([](CustomerData& x, const std::string& v) { x.city = v; }));
    return d;
}

// ======================================================================= customers
void ConsoleUi::print_customers(const std::vector<const Customer*>& list) {
    if (list.empty()) { out_ << "  (no customers)\n"; return; }
    // Fixed-width columns; std::setw pads but never truncates, so a space separates every column.
    // (Widths count bytes: names with accented letters, two bytes in UTF-8, may shift by one.)
    out_ << std::left << "  " << std::setw(4) << "id" << ' ' << std::setw(24) << "name" << ' '
         << std::setw(17) << "phone" << ' ' << std::setw(28) << "e-mail" << ' ' << std::setw(10) << "city"
         << " interactions\n";
    for (const Customer* c : list) {
        const CustomerData& d = c->data();
        out_ << "  " << std::setw(4) << c->id() << ' ' << std::setw(24) << (d.last_name + ", " + d.first_name)
             << ' ' << std::setw(17) << d.phone << ' ' << std::setw(28) << d.email << ' ' << std::setw(10)
             << d.city << ' ' << c->interactions().size() << '\n';
    }
    out_ << std::right;
}

void ConsoleUi::list_customers() { print_customers(crm_.customers()); }

void ConsoleUi::add_customer() {
    out_ << "-- New customer --\n";
    const std::uint32_t id = crm_.add_customer(ask_customer_data({}));
    save();
    out_ << "  Customer #" << id << " added.\n";
}

void ConsoleUi::search_customers() {
    const std::string text = trim(read_line("Text to search in first or last name: "));
    const auto found = crm_.search(text);
    out_ << "  " << found.size() << " customer(s) found.\n";
    print_customers(found);
}

void ConsoleUi::edit_customer() {
    const auto id = ask_customer_id();
    if (!id) return;
    Customer* c = crm_.find(*id);
    c->update(ask_customer_data(c->data()));
    save();
    out_ << "  Customer #" << *id << " updated.\n";
}

void ConsoleUi::delete_customer() {
    const auto id = ask_customer_id();
    if (!id) return;
    const Customer* c = crm_.find(*id);
    if (!ask_yes_no("Delete " + c->full_name() + " and " + std::to_string(c->interactions().size()) +
                    " interaction(s)?")) {
        out_ << "  Nothing deleted.\n";
        return;
    }
    crm_.remove_customer(*id);                   // c dangles from here on: not used again
    save();
    out_ << "  Customer #" << *id << " deleted.\n";
}

// ======================================================================= interactions
void ConsoleUi::interactions_menu() {
    const auto id = ask_customer_id();
    if (!id) return;
    while (true) {
        Customer& c = *crm_.find(*id);
        out_ << "\n---- Interactions of " << c.full_name() << " (#" << c.id() << ") ----\n"
             << " 1) List interactions\n 2) Add an appointment\n 3) Add a contract\n"
             << " 4) Search interactions\n 5) Delete an interaction\n 0) Back to the main menu\n";
        switch (ask_choice("Choice: ", 0, 5)) {
        case 1: list_interactions(c); break;
        case 2: add_appointment(c); break;
        case 3: add_contract(c); break;
        case 4: search_interactions(c); break;
        case 5: delete_interaction(c); break;
        case 0: return;
        }
    }
}

void ConsoleUi::list_interactions(const Customer& c) {
    if (c.interactions().empty()) { out_ << "  (no interactions)\n"; return; }
    for (const auto& i : c.interactions()) {           // polymorphic: kind() and details() are virtual
        out_ << "  [" << i->id() << "] " << std::left << std::setw(12) << i->kind() << std::right << i->details() << '\n';
        if (!i->notes().empty()) out_ << "        notes: " << i->notes() << '\n';
    }
}

void ConsoleUi::add_appointment(Customer& c) {
    out_ << "-- New appointment --\n";
    const Date date = ask_date("Date ");
    const TimeOfDay time = ask_time("Time ");
    const auto required = [](const std::string& v) { check_text(v, "the agent", true); };
    const auto optional = [](const std::string& v) { check_text(v, "this field", false, 120); };
    const std::string agent = ask_text("Agent: ", "", required);
    const std::string place = ask_text("Place (optional): ", "", optional);
    const std::string notes = ask_text("Notes (optional): ", "", [](const std::string& v) { check_text(v, "notes", false, 300); });
    c.add_interaction(std::make_unique<Appointment>(crm_.new_interaction_id(), date, time, agent, place, notes));
    save();
    out_ << "  Appointment added.\n";
}

void ConsoleUi::add_contract(Customer& c) {
    out_ << "-- New contract --\n";
    const std::string policy = ask_text("Policy number: ", "", [this](const std::string& v) {
        check_text(v, "the policy number", true, 40);
        if (crm_.policy_exists(v)) throw std::invalid_argument("policy " + v + " already exists");
    });
    const Product product = ask_product();
    const Date signed_on = ask_date("Signing date ");
    Date end = ask_date("End date ");
    while (end <= signed_on) {
        out_ << "  The end date must follow the signing date.\n";
        end = ask_date("End date ");
    }
    const std::int64_t premium = ask_money("Annual premium in EUR: ");
    const std::string notes = ask_text("Notes (optional): ", "", [](const std::string& v) { check_text(v, "notes", false, 300); });
    c.add_interaction(std::make_unique<Contract>(crm_.new_interaction_id(), signed_on, policy, product,
                                                 premium, end, notes));
    save();
    out_ << "  Contract added.\n";
}

void ConsoleUi::search_interactions(const Customer& c) {
    const std::string text = trim(read_line("Text to search (agent, policy, product, date, notes...): "));
    const auto found = c.find_interactions(text);
    out_ << "  " << found.size() << " interaction(s) found.\n";
    for (const Interaction* i : found)
        out_ << "  [" << i->id() << "] " << i->kind() << ": " << i->details() << '\n';
}

void ConsoleUi::delete_interaction(Customer& c) {
    const int id = ask_choice("Interaction id to delete (0 to cancel): ", 0, INT32_MAX);
    if (id == 0) return;
    if (c.remove_interaction(static_cast<std::uint32_t>(id))) {
        save();
        out_ << "  Interaction deleted.\n";
    } else {
        out_ << "  This customer has no interaction with id " << id << ".\n";
    }
}

// ======================================================================= persistence
void ConsoleUi::save() {
    try {
        storage_.save(crm_);
    } catch (const std::exception& e) {
        std::cerr << "WARNING: could not save the data: " << e.what() << '\n';
    }
}

}  // namespace crm

// interaction.cpp — appointments, contracts and their (de)serialisation.
#include "crm/interaction.hpp"

#include <stdexcept>

#include "crm/text.hpp"

namespace crm {

void check_text(const std::string& value, const char* field, bool required, std::size_t max_len) {
    if (required && trim(value).empty())
        throw std::invalid_argument(std::string(field) + " must not be empty");
    if (value.size() > max_len)
        throw std::invalid_argument(std::string(field) + " is too long (max " + std::to_string(max_len) + " characters)");
    if (has_control_chars(value))
        throw std::invalid_argument(std::string(field) + " must not contain line breaks or control characters");
}

std::string product_name(Product p) {
    switch (p) {
    case Product::Car:    return "car";
    case Product::Home:   return "home";
    case Product::Life:   return "life";
    case Product::Health: return "health";
    case Product::Other:  return "other";
    }
    return "other";                              // unreachable; keeps compilers quiet
}

std::optional<Product> parse_product(std::string_view text) {
    const std::string t = to_lower(trim(text));
    for (Product p : {Product::Car, Product::Home, Product::Life, Product::Health, Product::Other})
        if (t == product_name(p)) return p;
    return std::nullopt;
}

// ---- Interaction ------------------------------------------------------------------------
Interaction::Interaction(std::uint32_t id, Date date, std::string notes)
    : id_(id), date_(date), notes_(trim(notes)) {
    check_text(notes_, "notes", false, 300);
}

bool Interaction::matches(std::string_view text) const {
    return contains_ci(kind(), text) || contains_ci(details(), text) || contains_ci(notes_, text);
}

Record Interaction::to_record() const {
    Record r{{"id", std::to_string(id_)}, {"kind", kind()}, {"date", date_.str()}, {"notes", notes_}};
    add_fields(r);                               // the derived class adds its own columns
    return r;
}

// ---- Appointment ------------------------------------------------------------------------
Appointment::Appointment(std::uint32_t id, Date date, TimeOfDay time, std::string agent,
                         std::string place, std::string notes)
    : Interaction(id, date, std::move(notes)), time_(time), agent_(trim(agent)), place_(trim(place)) {
    check_text(agent_, "agent", true);
    check_text(place_, "place", false);
}

std::string Appointment::details() const {
    return date().str() + " " + time_.str() + ", agent " + agent_ + (place_.empty() ? "" : ", at " + place_);
}

void Appointment::add_fields(Record& r) const {
    r["time"] = time_.str();
    r["agent"] = agent_;
    r["place"] = place_;
}

// ---- Contract ---------------------------------------------------------------------------
Contract::Contract(std::uint32_t id, Date signed_on, std::string policy_number, Product product,
                   std::int64_t annual_premium_cents, Date end_date, std::string notes)
    : Interaction(id, signed_on, std::move(notes)), policy_number_(trim(policy_number)),
      product_(product), premium_cents_(annual_premium_cents), end_date_(end_date) {
    check_text(policy_number_, "policy number", true, 40);
    if (premium_cents_ <= 0) throw std::invalid_argument("the annual premium must be positive");
    if (end_date_ <= date()) throw std::invalid_argument("the end date must follow the signing date");
}

std::string Contract::details() const {
    return "policy " + policy_number_ + " (" + product_name(product_) + "), signed " + date().str() +
           ", premium " + format_money(premium_cents_) + " EUR/year, until " + end_date_.str();
}

void Contract::add_fields(Record& r) const {
    r["policy_number"] = policy_number_;
    r["product"] = product_name(product_);
    r["premium_cents"] = std::to_string(premium_cents_);
    r["end_date"] = end_date_.str();
}

// ---- factory ----------------------------------------------------------------------------
namespace {
const std::string& field(const Record& r, const std::string& name) {
    static const std::string empty;
    const auto it = r.find(name);
    return it == r.end() ? empty : it->second;
}
Date date_field(const Record& r, const std::string& name) {
    const auto d = Date::parse(field(r, name));
    if (!d) throw std::invalid_argument("invalid " + name + " '" + field(r, name) + "'");
    return *d;
}
}  // namespace

std::unique_ptr<Interaction> interaction_from_record(const Record& r) {
    const auto id = parse_int(field(r, "id"), 1, UINT32_MAX);
    if (!id) throw std::invalid_argument("invalid id '" + field(r, "id") + "'");
    const auto uid = static_cast<std::uint32_t>(*id);
    const std::string kind = field(r, "kind");
    if (kind == "appointment") {
        const auto time = TimeOfDay::parse(field(r, "time"));
        if (!time) throw std::invalid_argument("invalid time '" + field(r, "time") + "'");
        return std::make_unique<Appointment>(uid, date_field(r, "date"), *time, field(r, "agent"),
                                             field(r, "place"), field(r, "notes"));
    }
    if (kind == "contract") {
        const auto product = parse_product(field(r, "product"));
        const auto premium = parse_int(field(r, "premium_cents"), 1, INT64_MAX);
        if (!product) throw std::invalid_argument("invalid product '" + field(r, "product") + "'");
        if (!premium) throw std::invalid_argument("invalid premium '" + field(r, "premium_cents") + "'");
        return std::make_unique<Contract>(uid, date_field(r, "date"), field(r, "policy_number"), *product,
                                          *premium, date_field(r, "end_date"), field(r, "notes"));
    }
    throw std::invalid_argument("unknown interaction kind '" + kind + "'");
}

}  // namespace crm

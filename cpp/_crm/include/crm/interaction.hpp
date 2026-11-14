// interaction.hpp — what happens between the company and a customer.
// Interaction is an abstract base class; Appointment and Contract are the two
// concrete kinds. A new kind is added by deriving a new class and extending
// interaction_from_record(): no other part of the program changes.
#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

#include "crm/date.hpp"

namespace crm {

// One row of a data file: column name -> text.
using Record = std::map<std::string, std::string>;

enum class Product { Car, Home, Life, Health, Other };
std::string product_name(Product p);
std::optional<Product> parse_product(std::string_view text);

class Interaction {
public:
    virtual ~Interaction() = default;            // deleted through Interaction* (unique_ptr)

    std::uint32_t id() const { return id_; }
    const Date& date() const { return date_; }
    const std::string& notes() const { return notes_; }

    virtual std::string kind() const = 0;        // "appointment", "contract", ...
    virtual std::string details() const = 0;     // one line for the user
    virtual bool matches(std::string_view text) const;   // used by the search
    Record to_record() const;                    // for saving: common fields + add_fields()

protected:
    Interaction(std::uint32_t id, Date date, std::string notes);
    virtual void add_fields(Record& record) const = 0;

private:
    std::uint32_t id_;
    Date date_;
    std::string notes_;
};

class Appointment final : public Interaction {
public:
    Appointment(std::uint32_t id, Date date, TimeOfDay time, std::string agent,
                std::string place, std::string notes);
    std::string kind() const override { return "appointment"; }
    std::string details() const override;
    const std::string& agent() const { return agent_; }

private:
    void add_fields(Record& record) const override;
    TimeOfDay time_;
    std::string agent_;
    std::string place_;
};

class Contract final : public Interaction {
public:
    Contract(std::uint32_t id, Date signed_on, std::string policy_number, Product product,
             std::int64_t annual_premium_cents, Date end_date, std::string notes);
    std::string kind() const override { return "contract"; }
    std::string details() const override;
    const std::string& policy_number() const { return policy_number_; }
    std::int64_t annual_premium_cents() const { return premium_cents_; }

private:
    void add_fields(Record& record) const override;
    std::string policy_number_;
    Product product_;
    std::int64_t premium_cents_;
    Date end_date_;
};

// Rebuild an interaction from a saved record; throws std::invalid_argument if invalid.
std::unique_ptr<Interaction> interaction_from_record(const Record& record);

// Validation shared by all classes: throws std::invalid_argument with a clear message.
void check_text(const std::string& value, const char* field, bool required, std::size_t max_len = 120);

}  // namespace crm

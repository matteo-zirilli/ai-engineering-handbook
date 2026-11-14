// customer.hpp — a customer and the interactions it owns.
#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

#include "crm/interaction.hpp"

namespace crm {

// The editable personal data of a customer (a plain struct: no invariant of its own).
struct CustomerData {
    std::string first_name;
    std::string last_name;
    std::string phone;      // optional
    std::string email;      // optional
    std::string city;       // optional
};

class Customer {
public:
    // Throws std::invalid_argument if the data are not valid (see validate()).
    Customer(std::uint32_t id, CustomerData data);

    // Throws std::invalid_argument with a message for the user if the data are invalid.
    static CustomerData validate(CustomerData data);

    std::uint32_t id() const { return id_; }
    const CustomerData& data() const { return data_; }
    std::string full_name() const { return data_.first_name + ' ' + data_.last_name; }

    // Replace the personal data; on invalid data, throws and leaves the customer unchanged.
    void update(CustomerData data);

    const std::vector<std::unique_ptr<Interaction>>& interactions() const { return interactions_; }
    void add_interaction(std::unique_ptr<Interaction> interaction);    // kept sorted by date
    bool remove_interaction(std::uint32_t interaction_id);
    std::vector<const Interaction*> find_interactions(std::string_view text) const;

private:
    std::uint32_t id_;
    CustomerData data_;
    std::vector<std::unique_ptr<Interaction>> interactions_;   // owned: destroyed with the customer
};

}  // namespace crm

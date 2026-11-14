// crm.hpp — the collection of customers: unique ids, lookup, search, listing.
// No input or output here: the user interface and the storage are separate classes.
#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <string_view>
#include <vector>

#include "crm/customer.hpp"

namespace crm {

class Crm {
public:
    // Add a new customer and return its id. Throws std::invalid_argument on invalid data.
    std::uint32_t add_customer(CustomerData data);
    // Insert a customer that already has an id (used when loading). Throws on a duplicate id.
    void insert_customer(Customer customer);
    bool remove_customer(std::uint32_t id);       // also removes its interactions

    Customer* find(std::uint32_t id);
    const Customer* find(std::uint32_t id) const;

    // All customers, or those whose first or last name contains `text` (case-insensitive),
    // sorted by last name, first name (case-insensitive), then id.
    std::vector<const Customer*> customers() const;
    std::vector<const Customer*> search(std::string_view text) const;
    // All customers in increasing id order (the order of the data files).
    std::vector<const Customer*> by_id() const;

    // A fresh interaction id, unique in the whole CRM.
    std::uint32_t new_interaction_id() { return next_interaction_id_++; }
    // Record that an id is in use (when loading), so that new ids never collide.
    void reserve_interaction_id(std::uint32_t id);
    bool policy_exists(std::string_view policy_number) const;

    std::size_t size() const { return customers_.size(); }
    std::size_t interaction_count() const;

private:
    std::map<std::uint32_t, Customer> customers_;   // key = customer id
    std::uint32_t next_customer_id_ = 1;
    std::uint32_t next_interaction_id_ = 1;
};

}  // namespace crm

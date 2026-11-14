// crm.cpp — the customer collection.
#include "crm/crm.hpp"

#include <algorithm>
#include <stdexcept>
#include <tuple>

#include "crm/text.hpp"

namespace crm {

std::uint32_t Crm::add_customer(CustomerData data) {
    const std::uint32_t id = next_customer_id_;
    customers_.emplace(id, Customer(id, std::move(data)));    // Customer validates (may throw)
    ++next_customer_id_;                                       // only after success
    return id;
}

void Crm::insert_customer(Customer customer) {
    const std::uint32_t id = customer.id();
    if (customers_.contains(id)) throw std::invalid_argument("duplicate customer id " + std::to_string(id));
    for (const auto& i : customer.interactions()) reserve_interaction_id(i->id());
    customers_.emplace(id, std::move(customer));
    next_customer_id_ = std::max(next_customer_id_, id + 1);
}

bool Crm::remove_customer(std::uint32_t id) { return customers_.erase(id) == 1; }

Customer* Crm::find(std::uint32_t id) {
    const auto it = customers_.find(id);
    return it == customers_.end() ? nullptr : &it->second;   // map nodes do not move: stable pointer
}

const Customer* Crm::find(std::uint32_t id) const {
    const auto it = customers_.find(id);
    return it == customers_.end() ? nullptr : &it->second;
}

namespace {
// Sort key: a tuple compared lexicographically -> a strict weak order (in fact total, thanks to the id).
auto sort_key(const Customer* c) {
    return std::make_tuple(to_lower(c->data().last_name), to_lower(c->data().first_name), c->id());
}
}  // namespace

std::vector<const Customer*> Crm::search(std::string_view text) const {
    std::vector<const Customer*> out;
    for (const auto& [id, c] : customers_)
        if (contains_ci(c.data().first_name, text) || contains_ci(c.data().last_name, text))
            out.push_back(&c);
    std::sort(out.begin(), out.end(), [](const Customer* a, const Customer* b) { return sort_key(a) < sort_key(b); });
    return out;
}

std::vector<const Customer*> Crm::customers() const { return search(""); }

std::vector<const Customer*> Crm::by_id() const {
    std::vector<const Customer*> out;
    for (const auto& [id, c] : customers_) out.push_back(&c);   // std::map iterates in key order
    return out;
}

void Crm::reserve_interaction_id(std::uint32_t id) {
    next_interaction_id_ = std::max(next_interaction_id_, id + 1);
}

bool Crm::policy_exists(std::string_view policy_number) const {
    for (const auto& [id, c] : customers_)
        for (const auto& i : c.interactions())
            if (const auto* k = dynamic_cast<const Contract*>(i.get()))
                if (to_lower(k->policy_number()) == to_lower(policy_number)) return true;
    return false;
}

std::size_t Crm::interaction_count() const {
    std::size_t n = 0;
    for (const auto& [id, c] : customers_) n += c.interactions().size();
    return n;
}

}  // namespace crm

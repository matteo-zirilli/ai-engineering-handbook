// customer.cpp — validation of personal data and management of interactions.
#include "crm/customer.hpp"

#include <algorithm>
#include <stdexcept>

#include "crm/text.hpp"

namespace crm {

CustomerData Customer::validate(CustomerData d) {
    for (std::string* s : {&d.first_name, &d.last_name, &d.phone, &d.email, &d.city}) *s = trim(*s);
    check_text(d.first_name, "first name", true, 60);
    check_text(d.last_name, "last name", true, 60);
    check_text(d.phone, "phone", false, 30);
    check_text(d.email, "e-mail", false, 100);
    check_text(d.city, "city", false, 60);
    if (!d.phone.empty()) {
        int digits = 0;
        for (char c : d.phone) {
            if (c >= '0' && c <= '9') ++digits;
            else if (c != '+' && c != ' ' && c != '-' && c != '/')
                throw std::invalid_argument("the phone number may contain only digits, spaces, +, - and /");
        }
        if (digits < 6) throw std::invalid_argument("the phone number needs at least 6 digits");
    }
    if (!d.email.empty()) {                       // deliberately simple: one '@', a dot after it, no spaces
        const auto at = d.email.find('@');
        if (at == std::string::npos || at == 0 || d.email.find('@', at + 1) != std::string::npos ||
            d.email.find('.', at) == std::string::npos || d.email.back() == '.' ||
            d.email.find(' ') != std::string::npos)
            throw std::invalid_argument("the e-mail address is not valid");
    }
    return d;
}

Customer::Customer(std::uint32_t id, CustomerData data) : id_(id), data_(validate(std::move(data))) {}

void Customer::update(CustomerData data) {
    data_ = validate(std::move(data));            // validate first: strong exception guarantee
}

void Customer::add_interaction(std::unique_ptr<Interaction> interaction) {
    if (!interaction) throw std::invalid_argument("null interaction");
    // Insert keeping the vector sorted by (date, id): binary search for the position.
    const auto pos = std::upper_bound(
        interactions_.begin(), interactions_.end(), interaction,
        [](const auto& a, const auto& b) {
            return a->date() != b->date() ? a->date() < b->date() : a->id() < b->id();
        });
    interactions_.insert(pos, std::move(interaction));
}

bool Customer::remove_interaction(std::uint32_t interaction_id) {
    const auto it = std::find_if(interactions_.begin(), interactions_.end(),
                                 [&](const auto& i) { return i->id() == interaction_id; });
    if (it == interactions_.end()) return false;
    interactions_.erase(it);                      // unique_ptr deletes the object
    return true;
}

std::vector<const Interaction*> Customer::find_interactions(std::string_view text) const {
    std::vector<const Interaction*> found;
    for (const auto& i : interactions_)
        if (i->matches(text)) found.push_back(i.get());
    return found;
}

}  // namespace crm

// date.cpp — parsing and formatting of dates and times.
#include "crm/date.hpp"

#include <cstdio>

#include "crm/text.hpp"

namespace crm {

bool Date::is_leap(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;   // Gregorian rule
}

int Date::days_in_month(int year, int month) {
    static constexpr int days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    return month == 2 && is_leap(year) ? 29 : days[month - 1];
}

std::optional<Date> Date::parse(std::string_view text) {
    const std::string t = trim(text);
    if (t.size() != 10 || t[4] != '-' || t[7] != '-') return std::nullopt;
    const auto y = parse_int(t.substr(0, 4), 1900, 2200);
    const auto m = parse_int(t.substr(5, 2), 1, 12);
    if (!y || !m) return std::nullopt;
    const auto d = parse_int(t.substr(8, 2), 1, days_in_month(int(*y), int(*m)));
    if (!d) return std::nullopt;
    return Date(int(*y), int(*m), int(*d));
}

std::string Date::str() const {
    char buf[16];
    std::snprintf(buf, sizeof buf, "%04d-%02d-%02d", year_, month_, day_);
    return buf;
}

std::optional<TimeOfDay> TimeOfDay::parse(std::string_view text) {
    const std::string t = trim(text);
    if (t.size() != 5 || t[2] != ':') return std::nullopt;
    const auto h = parse_int(t.substr(0, 2), 0, 23);
    const auto m = parse_int(t.substr(3, 2), 0, 59);
    if (!h || !m) return std::nullopt;
    return TimeOfDay(int(*h * 60 + *m));
}

std::string TimeOfDay::str() const {
    char buf[16];
    std::snprintf(buf, sizeof buf, "%02d:%02d", minutes_ / 60, minutes_ % 60);
    return buf;
}

}  // namespace crm

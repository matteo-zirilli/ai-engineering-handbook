// date.hpp — calendar dates and times of day, always valid once constructed.
#pragma once

#include <compare>
#include <optional>
#include <string>
#include <string_view>

namespace crm {

class Date {
public:
    // Parse "YYYY-MM-DD" (years 1900-2200); std::nullopt if the text is not a valid date.
    static std::optional<Date> parse(std::string_view text);
    static bool is_leap(int year);
    static int days_in_month(int year, int month);

    int year() const { return year_; }
    int month() const { return month_; }
    int day() const { return day_; }
    std::string str() const;                                       // "YYYY-MM-DD"
    friend auto operator<=>(const Date&, const Date&) = default;    // chronological order

private:
    Date(int y, int m, int d) : year_(y), month_(m), day_(d) {}
    int year_, month_, day_;                                       // declaration order = comparison order
};

class TimeOfDay {
public:
    static std::optional<TimeOfDay> parse(std::string_view text);   // "HH:MM", 00:00-23:59
    std::string str() const;
    friend auto operator<=>(const TimeOfDay&, const TimeOfDay&) = default;

private:
    explicit TimeOfDay(int minutes) : minutes_(minutes) {}
    int minutes_;                                                  // minutes since midnight
};

}  // namespace crm

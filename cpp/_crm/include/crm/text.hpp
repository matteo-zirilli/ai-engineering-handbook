// text.hpp — small text utilities: trimming, case-insensitive matching,
// number parsing and the CSV encoding used by the data files.
#pragma once

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace crm {

// Remove spaces, tabs and carriage returns at both ends.
std::string trim(std::string_view s);

// ASCII lower-case copy (bytes >= 128, e.g. UTF-8 accented letters, are kept as they are).
std::string to_lower(std::string_view s);

// Case-insensitive substring test; an empty needle matches everything.
bool contains_ci(std::string_view haystack, std::string_view needle);

// True if the text contains a control character (line break, tab, ...).
bool has_control_chars(std::string_view s);

// The whole (trimmed) text must be an integer in [lo, hi].
std::optional<long long> parse_int(std::string_view text, long long lo, long long hi);

// Money in euros with at most two decimals ("480", "480.5", "480,50") -> cents.
std::optional<std::int64_t> parse_money(std::string_view text);

// Cents -> "480.50".
std::string format_money(std::int64_t cents);

// CSV (RFC 4180): quote a field if it contains a comma, a quote or a line break.
std::string csv_escape(std::string_view field);
std::string csv_join(const std::vector<std::string>& fields);
// Split one line into fields; false if a quoted field is not terminated.
bool csv_split(std::string_view line, std::vector<std::string>& fields);

}  // namespace crm

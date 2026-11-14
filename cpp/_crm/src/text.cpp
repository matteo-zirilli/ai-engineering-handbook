// text.cpp — implementation of the text utilities.
#include "crm/text.hpp"

#include <charconv>
#include <limits>

namespace crm {

std::string trim(std::string_view s) {
    const auto first = s.find_first_not_of(" \t\r\n");
    if (first == std::string_view::npos) return {};
    const auto last = s.find_last_not_of(" \t\r\n");
    return std::string(s.substr(first, last - first + 1));
}

std::string to_lower(std::string_view s) {
    std::string out(s);
    for (char& c : out)
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
    return out;
}

bool contains_ci(std::string_view haystack, std::string_view needle) {
    return to_lower(haystack).find(to_lower(needle)) != std::string::npos;
}

bool has_control_chars(std::string_view s) {
    for (unsigned char c : s)
        if (c < 32 || c == 127) return true;
    return false;
}

std::optional<long long> parse_int(std::string_view text, long long lo, long long hi) {
    const std::string t = trim(text);
    if (t.empty()) return std::nullopt;
    long long value = 0;
    const auto [ptr, ec] = std::from_chars(t.data(), t.data() + t.size(), value);
    if (ec != std::errc{} || ptr != t.data() + t.size()) return std::nullopt;
    if (value < lo || value > hi) return std::nullopt;
    return value;
}

std::optional<std::int64_t> parse_money(std::string_view text) {
    const std::string t = trim(text);
    const auto sep = t.find_first_of(".,");
    const std::string whole = t.substr(0, sep);
    const std::string frac = sep == std::string::npos ? "" : t.substr(sep + 1);
    if (whole.empty() || frac.size() > 2) return std::nullopt;
    for (char c : whole + frac)
        if (c < '0' || c > '9') return std::nullopt;            // also rejects a sign
    constexpr std::int64_t max_euros = 1'000'000'000;          // a sanity limit, far from overflow
    const auto euros = parse_int(whole, 0, max_euros);
    if (!euros) return std::nullopt;
    std::int64_t cents = 0;
    if (frac.size() == 1) cents = (frac[0] - '0') * 10;
    if (frac.size() == 2) cents = (frac[0] - '0') * 10 + (frac[1] - '0');
    return *euros * 100 + cents;
}

std::string format_money(std::int64_t cents) {
    const std::int64_t euros = cents / 100, rest = cents % 100;
    return std::to_string(euros) + '.' + (rest < 10 ? "0" : "") + std::to_string(rest);
}

std::string csv_escape(std::string_view field) {
    if (field.find_first_of(",\"\r\n") == std::string_view::npos) return std::string(field);
    std::string out = "\"";
    for (char c : field) {
        if (c == '"') out += '"';                // a quote is written twice
        out += c;
    }
    out += '"';
    return out;
}

std::string csv_join(const std::vector<std::string>& fields) {
    std::string line;
    for (std::size_t i = 0; i < fields.size(); ++i) {
        if (i > 0) line += ',';
        line += csv_escape(fields[i]);
    }
    return line;
}

bool csv_split(std::string_view line, std::vector<std::string>& fields) {
    if (!line.empty() && line.back() == '\r') line.remove_suffix(1);   // files edited on Windows
    fields.assign(1, "");
    bool quoted = false;
    for (std::size_t i = 0; i < line.size(); ++i) {
        const char c = line[i];
        if (quoted) {
            if (c == '"' && i + 1 < line.size() && line[i + 1] == '"') {
                fields.back() += '"';
                ++i;
            } else if (c == '"') {
                quoted = false;                  // closing quote
            } else {
                fields.back() += c;
            }
        } else if (c == '"' && fields.back().empty()) {
            quoted = true;                       // opening quote at the start of a field
        } else if (c == ',') {
            fields.emplace_back();
        } else {
            fields.back() += c;
        }
    }
    return !quoted;
}

}  // namespace crm

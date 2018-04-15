#include <string>
#include <sstream>
#include "benefit.h"

std::string Benefit::GetString() const {
  std::stringstream ss;
  ss << sum_;
  return ss.str();
}

std::ostream& operator<<(std::ostream& os, const Benefit& obj) {
  return os << obj.GetString();
}

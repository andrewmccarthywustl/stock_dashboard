// src/components/Header/Header.jsx
import { NavLink } from "react-router-dom";

const Header = () => {
  return (
    <header className="bg-gray-800 text-white">
      <nav className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `hover:text-gray-300 ${
                  isActive ? "text-white font-bold" : "text-gray-300"
                }`
              }
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/treemap"
              className={({ isActive }) =>
                `hover:text-gray-300 ${
                  isActive ? "text-white font-bold" : "text-gray-300"
                }`
              }
            >
              Treemap
            </NavLink>
            <NavLink
              to="/transactions"
              className={({ isActive }) =>
                `hover:text-gray-300 ${
                  isActive ? "text-white font-bold" : "text-gray-300"
                }`
              }
            >
              Transactions
            </NavLink>
            <NavLink
              to="/trade"
              className={({ isActive }) =>
                `hover:text-gray-300 ${
                  isActive ? "text-white font-bold" : "text-gray-300"
                }`
              }
            >
              Trade
            </NavLink>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;

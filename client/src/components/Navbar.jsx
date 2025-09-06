import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/Auth";
import { FaBars, FaTimes } from "react-icons/fa";
import ThemeToggle from "./ThemeToggle";

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <div>
      <nav className="glass-dark flex justify-between items-center p-6 shadow-lg border-b border-gray-700/30 w-full md:w-[85%] mx-auto rounded-b-2xl backdrop-blur-xl">
        <Link
          to="/"
          className="text-3xl font-bold text-gradient font-poppins animate-fade-in-up"
        >
          EchoSQL
        </Link>
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          <div className="md:hidden">
            <button 
              onClick={toggleMenu} 
              className="text-white text-2xl hover:text-cyan-400 transition-colors duration-300 p-2 rounded-lg hover:bg-gray-800/50"
            >
              {menuOpen ? <FaTimes /> : <FaBars />}
            </button>
          </div>
        </div>
        <div
          className={`${
            menuOpen ? "flex" : "hidden"
          } flex-col md:flex md:flex-row gap-4 fixed md:static top-0 right-0 h-screen md:h-auto w-2/3 md:w-auto md:bg-transparent z-50 md:z-auto p-6 md:p-0 shadow-xl md:shadow-none rounded-l-2xl md:rounded-none`}
        >
          <button
            onClick={toggleMenu}
            className="self-end text-white text-2xl mb-4 md:hidden hover:text-cyan-400 transition-colors duration-300 p-2 rounded-lg hover:bg-gray-800/50"
          >
            <FaTimes />
          </button>
          <Link
            to={isAuthenticated ? "/dashboard" : "/auth/login"}
            className="btn-primary text-sm md:text-base font-jetbrains w-[90%] md:w-36 h-12 rounded-full flex justify-center items-center mt-4 md:mt-0 animate-slide-in-right"
          >
            {isAuthenticated ? "Dashboard" : "Login"}
          </Link>
          {isAuthenticated && (
            <button
              onClick={logout}
              className="btn-secondary text-sm md:text-base font-jetbrains w-[90%] md:w-36 h-12 rounded-full flex justify-center items-center mt-4 md:mt-0 animate-slide-in-right"
            >
              Logout
            </button>
          )}
        </div>
      </nav>
    </div>
  );
}

export default Navbar;

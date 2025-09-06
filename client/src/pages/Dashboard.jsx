import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { getDatabases } from "../redux/slices/database";
import Modal from "../components/Modal";
import { FaDatabase, FaPlus, FaSpinner } from "react-icons/fa";
import { BiLogoPostgresql } from "react-icons/bi";
import { GrMysql } from "react-icons/gr";
import { SiNeo4J } from "react-icons/si";
import { useAuth } from "../context/Auth";
import { createQuerySession } from "../redux/slices/querySession";
import { HiOutlineLogout } from "react-icons/hi";
import ThemeToggle from "../components/ThemeToggle";

function Dashboard() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { databases, loading, error } = useSelector((state) => state.database);
  const [selectedDatabase, setSelectedDatabase] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    dispatch(getDatabases());
  }, [dispatch]);

  const handleClick = async (database) => {
    try {
      // Create a new session for the selected database
      const sessionData = {
        user: user._id,
        database: database._id,
        title: `${database.database} - ${new Date().toLocaleDateString()}`,
        description: `New ${database.dbType.toUpperCase()} session`,
      };

      const response = await dispatch(createQuerySession(sessionData)).unwrap();
      navigate(`/chat/${response._id}`);
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  const handleVoiceDB = async (id) => {
    try {
      const sessionData = {
        user: user._id,
        database: id,
        title: `Session ${new Date().toLocaleDateString()}`,
        description: "Voice query session",
      };
      const response = await dispatch(createQuerySession(sessionData)).unwrap();
      navigate(`/chat/${response._id}`);
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  if (loading.fetch) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <FaSpinner className="animate-spin text-4xl text-cyan-400" />
      </div>
    );
  }

  if (error.fetch) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500 bg-red-500/10 px-4 py-2 rounded-lg">
          {error.fetch}
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: "var(--bg-primary)" }}
    >
      {/* Header - Fixed height */}
      <div className="glass-dark p-6 border-b border-gray-700/30 backdrop-blur-xl">
        <div className="container mx-auto flex justify-between items-center px-6">
          <Link
            to="/"
            className="text-3xl font-bold text-gradient font-poppins animate-fade-in-up"
          >
            EchoSQL
          </Link>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <Link to="/profile" className="flex items-center space-x-4 group">
              <div className="text-gray-300 max-sm:hidden font-inter group-hover:text-cyan-400 transition-colors duration-300">
                {user?.email}
              </div>
              <img
                src={
                  user?.profileImage
                    ? (import.meta.env.VITE_API_URL || "").replace(
                        "/api/v1",
                        ""
                      ) +
                      "/" +
                      user?.profileImage
                    : "/user.jpg"
                }
                alt="Profile"
                className="w-10 h-10 rounded-full border-2 border-cyan-400/30 hover:border-cyan-400 transition-all duration-300 hover:scale-110"
              />
            </Link>
            <button
              onClick={logout}
              className="text-gray-300 hover:text-cyan-400 transition-colors duration-300 rounded-xl p-2 hover:bg-gray-800/50"
            >
              <HiOutlineLogout size={24} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - Scrollable */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 text-gradient font-poppins animate-fade-in-up">
              Your Databases
            </h1>
            <p className="text-gray-400 font-inter text-lg animate-fade-in-up">
              Manage and interact with your database connections
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {databases.map((db, index) => (
              <div
                key={db._id}
                onClick={() => handleClick(db)}
                className={`card card-hover group cursor-pointer px-8 py-10 
                  flex flex-col items-center text-center animate-scale-in
                  ${
                    selectedDatabase === db._id
                      ? "border-cyan-400/60 glass-cyan shadow-glow"
                      : "border-gray-700/50 hover:border-cyan-400/40 glass-dark"
                  }`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {/* Icon - large */}
                <div className="text-7xl text-cyan-400 mb-6 group-hover:scale-110 transition-transform duration-300">
                  {db.dbType === "mysql" ? (
                    <GrMysql />
                  ) : db.dbType === "postgresql" ? (
                    <BiLogoPostgresql />
                  ) : db.dbType === "neo4j" ? (
                    <SiNeo4J />
                  ) : (
                    <BiLogoPostgresql />
                  )}
                </div>

                {/* DB Name */}
                <h3 className="text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors mb-3 font-jetbrains">
                  {db.database.toUpperCase()}
                </h3>

                {/* Created Date */}
                <div className="text-gray-400 text-sm flex items-center justify-center mb-6 font-inter">
                  <FaDatabase className="mr-2 text-cyan-400" />
                  {new Date(db.createdAt).toLocaleDateString()}
                </div>

                {/* Drop-down button */}
                <div
                  className={`overflow-hidden transition-all duration-500 ease-in-out w-full ${
                    selectedDatabase === db._id
                      ? "max-h-32 opacity-100"
                      : "max-h-0 opacity-0"
                  }`}
                >
                  <button
                    onClick={() => handleVoiceDB(db._id)}
                    className="btn-primary w-full font-jetbrains text-sm py-3 mt-4 animate-scale-in"
                  >
                    VoiceDB
                  </button>
                </div>
              </div>
            ))}

            {/* Create New DB Button */}
            <button
              onClick={() => setIsModalOpen(true)}
              className="card card-hover group
                flex flex-col items-center justify-center min-h-[280px]
                border-dashed border-2 border-gray-600/50 hover:border-cyan-400/50
                animate-scale-in"
            >
              <FaPlus className="text-5xl text-gray-500 group-hover:text-cyan-400 transition-colors mb-4 group-hover:scale-110" />
              <span className="text-gray-500 group-hover:text-cyan-400 transition-colors font-inter text-lg">
                Create New Database
              </span>
            </button>
          </div>
        </div>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}

export default Dashboard;

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom"; // Add Link import
import { useAuth } from "../context/Auth";

function Login() {
  const navigate = useNavigate();
  const { login, loading, errors } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await login({
      email: formData.email,
      password: formData.password,
    });

    if (!errors?.login) {
      navigate("/dashboard");
    }
  };

  return (
    <div className="bg-black min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8 bg-[#131313] p-8 rounded-xl border border-gray-800">
        <div className="text-center">
          <h2 className="text-3xl font-bold">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-cyan-400">
              Welcome Back
            </span>
          </h2>
          <p className="mt-2 text-gray-400">
            Login to continue visualizing data
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {(error || errors?.login) && (
            <div className="text-red-500 text-sm text-center bg-red-500/10 py-2 rounded">
              {error || errors.login}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="text-gray-300 text-sm">
                Email
              </label>
              <input
                type="email"
                name="email"
                id="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full bg-[#1a1a1a] border border-gray-800 rounded-lg px-4 py-2 mt-1 focus:outline-none focus:border-cyan-400 text-white"
              />
            </div>

            <div>
              <label htmlFor="password" className="text-gray-300 text-sm">
                Password
              </label>
              <input
                type="password"
                name="password"
                id="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full bg-[#1a1a1a] border border-gray-800 rounded-lg px-4 py-2 mt-1 focus:outline-none focus:border-cyan-400 text-white"
              />
            </div>
          </div>

          {/* Add Forgot Password link before the submit button */}
          <div className="flex justify-end">
            <Link
              to="/auth/forgot-password"
              className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              Forgot Password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading.login}
            className="w-full bg-gradient-to-r cursor-pointer from-green-400 to-cyan-400 text-white rounded-lg px-4 py-2 hover:opacity-90 transition-opacity flex items-center justify-center"
          >
            {loading.login ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Logging in...
              </>
            ) : (
              "Log In"
            )}
          </button>

          {/* Add the "Don't have an account?" section */}
          <div className="text-center text-gray-400">
            <p>
              Don't have an account?{" "}
              <Link
                to="/auth/signup"
                className="text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;

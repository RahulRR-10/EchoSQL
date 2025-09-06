/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState, useRef, useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { getDatabaseById } from "../redux/slices/database";
import { getQuerySessionById } from "../redux/slices/querySession";
import {
  createQueryMessage,
  getSessionMessages,
} from "../redux/slices/queryMessage";
import { fetchSuggestions, fetchCompletions } from "../utils/service";
import { AnimatePresence } from "framer-motion";
import ChatMessage from "../components/ChatMessage";
import VoiceInputBar from "../components/VoiceInputBar";
import PDFDownloadButton from "../components/PDFDownloadButton";
import debounce from "lodash/debounce";
import { useAuth } from "../context/Auth";
import { HiOutlineLogout } from "react-icons/hi";

function Chat() {
  const { sessionId } = useParams();
  const dispatch = useDispatch();
  const { currentDatabase } = useSelector((state) => state.database);
  const { currentSession } = useSelector((state) => state.querySession);
  const { messages: storedMessages } = useSelector(
    (state) => state.queryMessage
  );
  const { logout } = useAuth();
  const [inputText, setInputText] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [completions, setCompletions] = useState([]);
  const [locale, setLocale] = useState("en");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuggestionsLoading, setSuggestionsLoading] = useState(false);
  const [isCompletionsLoading, setCompletionsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  // Fetch session and database on mount
  useEffect(() => {
    if (sessionId) {
      dispatch(getQuerySessionById(sessionId))
        .unwrap()
        .then((session) => {
          if (session?.database) {
            dispatch(getDatabaseById(session.database._id));
          }
        })
        .catch((err) => {
          console.error("Failed to load session:", err);
          setError("Failed to load session. Please refresh the page.");
        });

      dispatch(getSessionMessages(sessionId))
        .unwrap()
        .catch((err) => {
          console.error("Failed to load messages:", err);
          // Don't show error for empty message list (404 is expected)
          if (err?.status !== 404) {
            setError("Failed to load chat history.");
          }
        });
    }
  }, [sessionId, dispatch]);

  // Fetch suggestions when database loads
  useEffect(() => {
    if (currentDatabase) {
      handleFetchSuggestions();
    }
  }, [currentDatabase]);

  const handleFetchSuggestions = async () => {
    if (!currentDatabase) return;

    setSuggestionsLoading(true);
    setError(null);

    const config = {
      dbtype: currentDatabase.dbType,
      host: currentDatabase.host,
      user: currentDatabase.username,
      password: currentDatabase.password,
      dbname: currentDatabase.database,
    };

    try {
      const results = await fetchSuggestions(config);
      const formattedSuggestions = results.map((suggestion) =>
        typeof suggestion === "object" ? suggestion.query : suggestion
      );
      setSuggestions(formattedSuggestions);
    } catch (err) {
      setError("Failed to load suggestions. Please try again.");
      console.error("Suggestion error:", err);
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const fetchCompletionsDebounced = useCallback(
    debounce(async (query) => {
      if (!currentDatabase || !query) return;

      setCompletionsLoading(true);
      setError(null);

      const config = {
        dbtype: currentDatabase.dbType,
        host: currentDatabase.host,
        user: currentDatabase.username,
        password: currentDatabase.password,
        dbname: currentDatabase.database,
      };

      try {
        const results = await fetchCompletions(query, config);
        const formattedCompletions = results.map((completion) =>
          typeof completion === "object" ? completion.query : completion
        );
        setCompletions(formattedCompletions);
      } catch (err) {
        setError("Failed to generate completions. Please try again.");
        console.error("Completion error:", err);
      } finally {
        setCompletionsLoading(false);
      }
    }, 500),
    [currentDatabase]
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [storedMessages]);

  const handleSend = async (text = inputText) => {
    if (!text.trim()) {
      setError("Please enter a message.");
      return;
    }

    if (!currentDatabase) {
      setError("Database configuration not found. Please select a database.");
      return;
    }

    if (!sessionId) {
      setError("Session not found. Please refresh the page.");
      return;
    }

    setIsLoading(true);
    setError(null);

    // Create a temporary user message to display immediately
    const tempUserMessage = {
      _id: Date.now().toString(),
      requestQuery: text,
      user: currentSession?.user,
      createdAt: new Date().toISOString(),
      isTemporary: true,
    };

    // Add temporary message to show user's input immediately
    const currentMessages = storedMessages || [];
    const tempMessages = [...currentMessages, tempUserMessage];

    try {
      await dispatch(
        createQueryMessage({
          sessionId,
          databaseId: currentDatabase._id,
          requestQuery: text,
          user: currentSession?.user,
        })
      ).unwrap();
      await dispatch(getQuerySessionById(sessionId)).unwrap();
      setInputText("");
      setCompletions([]);
    } catch (err) {
      console.error("Send error:", err);

      // Better error handling for different error types
      let errorMessage = "Failed to send message. Please try again.";

      if (err?.error) {
        // Custom error from API
        errorMessage = err.error;
      } else if (err?.message) {
        // JavaScript error
        errorMessage = err.message;
      } else if (err?.status) {
        // HTTP status error
        switch (err.status) {
          case 400:
            errorMessage =
              "I can only help with database-related queries. Please ask something about your database data.";
            break;
          case 404:
            errorMessage = "Database configuration not found.";
            break;
          case 500:
            errorMessage = "Server error. Please try again.";
            break;
          case 503:
            errorMessage =
              "Chat service is unavailable. Please try again later.";
            break;
          default:
            errorMessage = `Error ${err.status}: Please try again.`;
        }
      }

      setError(errorMessage);

      // Refresh messages to remove temporary message
      dispatch(getSessionMessages(sessionId));
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = (text) => {
    setInputText(text);
    fetchCompletionsDebounced(text);
  };

  const handleSuggestionClick = (text) => {
    setInputText(text);
    handleSend(text);
  };

  return (
    <div className="h-screen bg-gradient-to-b from-black to-gray-900 flex flex-col">
      <div className="p-4 bg-[#0a1a1a] border-b border-gray-800 flex justify-between items-center">
        <Link
          to="/"
          className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 ml-12"
        >
          EchoSQL
        </Link>

        {/* Center section with PDF download button */}
        <div className="flex-1 flex justify-center">
          {currentSession && storedMessages?.length > 0 && (
            <PDFDownloadButton
              sessionId={sessionId}
              sessionTitle={currentSession.title}
              className="mx-4"
            />
          )}
        </div>

        <div className="flex items-center space-x-4 mr-12 justify-center">
          <Link to="/profile" className="flex items-center space-x-4">
            <div className="text-gray-300 max-sm:hidden">
              {currentSession?.user?.email}
            </div>
            <img
              src={
                import.meta.env.VITE_APP_BACKEND_URL +
                currentSession?.user?.profileImage
              }
              alt="Profile"
              className="w-8 h-8 rounded-full"
            />
          </Link>
          <button
            onClick={logout}
            className="text-gray-300 hover:text-cyan-400 transition-colors duration-300 rounded-lg cursor-pointer"
          >
            <HiOutlineLogout size={24} />
          </button>
        </div>
      </div>

      {/* Show loading state if session or database not loaded */}
      {(!currentSession || !currentDatabase) && !error && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-300">Loading chat session...</p>
          </div>
        </div>
      )}

      {/* Main chat area - only show when everything is loaded */}
      {currentSession && currentDatabase && (
        <>
          <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
            <AnimatePresence>
              {storedMessages?.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
            </AnimatePresence>

            {/* Loading indicator */}
            {isLoading && (
              <div className="w-full flex justify-start px-4 my-4">
                <div className="max-w-[70%] flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <div className="text-blue-400 w-5 h-5">🤖</div>
                  </div>
                  <div className="px-4 py-3 rounded-2xl text-sm leading-relaxed text-white bg-transparent border border-gray-700">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                      <div
                        className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                      <span className="ml-2 text-gray-400">
                        Processing your query...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Error Display - Fixed at bottom above input */}
          {error && (
            <div className="mx-4 mb-2">
              <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 text-red-100 flex items-center justify-between shadow-lg">
                <span>{error}</span>
                <button
                  onClick={() => setError(null)}
                  className="ml-4 text-red-300 hover:text-red-100 transition-colors text-lg font-bold"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          <div className="mx-4 mb-4 mt-2">
            <VoiceInputBar
              completions={completions}
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
              inputText={inputText}
              setInputText={handleVoiceInput}
              locale={locale}
              setLocale={setLocale}
              isLoading={isLoading}
              isSuggestionsLoading={isSuggestionsLoading}
              isCompletionsLoading={isCompletionsLoading}
              onSend={handleSend}
              disabled={!currentDatabase || !sessionId}
            />
          </div>
        </>
      )}

      {/* Error state when session/database failed to load */}
      {error && (!currentSession || !currentDatabase) && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-4">
            <div className="text-red-400 text-6xl mb-4">⚠️</div>
            <h2 className="text-xl text-gray-300 mb-4">Chat Unavailable</h2>
            <p className="text-gray-400 mb-6">{error}</p>
            <div className="space-x-4">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-cyan-500 text-black rounded-lg hover:bg-cyan-400 transition-colors"
              >
                Refresh Page
              </button>
              <Link
                to="/"
                className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors inline-block"
              >
                Go Home
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;

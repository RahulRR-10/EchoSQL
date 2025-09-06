import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaStar, FaSearch, FaTrash, FaCopy } from 'react-icons/fa';
import { getBookmarks, removeBookmark, searchBookmarks } from '../utils/bookmarks';

const BookmarksDropdown = ({ isOpen, onClose, onSelectQuery }) => {
  const [bookmarks, setBookmarks] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredBookmarks, setFilteredBookmarks] = useState([]);

  useEffect(() => {
    if (isOpen) {
      loadBookmarks();
    }
  }, [isOpen]);

  useEffect(() => {
    setFilteredBookmarks(searchBookmarks(searchTerm));
  }, [searchTerm, bookmarks]);

  const loadBookmarks = () => {
    const allBookmarks = getBookmarks();
    setBookmarks(allBookmarks);
  };

  const handleRemoveBookmark = (id, e) => {
    e.stopPropagation();
    const result = removeBookmark(id);
    if (result.success) {
      loadBookmarks();
    }
  };

  const handleCopyQuery = (query, e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(query);
    // You could add a toast notification here
  };

  const handleSelectQuery = (query) => {
    onSelectQuery(query);
    onClose();
    setSearchTerm('');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="absolute bottom-full left-0 right-0 mb-2 bg-[#1a1a1a] border border-gray-700 rounded-lg shadow-xl z-50 max-h-80 overflow-hidden"
      >
        {/* Header */}
        <div className="p-3 border-b border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <FaStar className="text-yellow-400" />
              Bookmarked Queries
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-xs" />
            <input
              type="text"
              placeholder="Search bookmarks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-2 bg-[#2a2a2a] border border-gray-600 rounded text-sm text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
            />
          </div>
        </div>

        {/* Bookmarks List */}
        <div className="max-h-48 overflow-y-auto">
          {filteredBookmarks.length === 0 ? (
            <div className="p-4 text-center text-gray-400 text-sm">
              {searchTerm ? 'No bookmarks found' : 'No bookmarks yet'}
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {filteredBookmarks.map((bookmark) => (
                <motion.div
                  key={bookmark.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="group p-2 rounded hover:bg-[#2a2a2a] cursor-pointer transition-colors"
                  onClick={() => handleSelectQuery(bookmark.query)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-white font-medium truncate">
                        {bookmark.title}
                      </div>
                      <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                        {bookmark.query}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(bookmark.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                      <button
                        onClick={(e) => handleCopyQuery(bookmark.query, e)}
                        className="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
                        title="Copy query"
                      >
                        <FaCopy size={10} />
                      </button>
                      <button
                        onClick={(e) => handleRemoveBookmark(bookmark.id, e)}
                        className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                        title="Remove bookmark"
                      >
                        <FaTrash size={10} />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default BookmarksDropdown;

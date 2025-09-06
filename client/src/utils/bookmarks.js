/**
 * Query Bookmark Manager
 * Safely manages bookmarked queries using localStorage
 */

const BOOKMARKS_KEY = 'aura_query_bookmarks';

// Get all bookmarks
export const getBookmarks = () => {
  try {
    const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
    return bookmarks ? JSON.parse(bookmarks) : [];
  } catch (error) {
    console.error('Error loading bookmarks:', error);
    return [];
  }
};

// Add a bookmark
export const addBookmark = (query, title = null) => {
  try {
    const bookmarks = getBookmarks();
    const bookmark = {
      id: Date.now().toString(),
      query: query.trim(),
      title: title || query.slice(0, 50) + (query.length > 50 ? '...' : ''),
      createdAt: new Date().toISOString(),
    };
    
    // Check if query already exists
    const exists = bookmarks.some(b => b.query.toLowerCase() === query.toLowerCase().trim());
    if (exists) {
      return { success: false, message: 'Query already bookmarked' };
    }
    
    const updatedBookmarks = [bookmark, ...bookmarks].slice(0, 50); // Keep max 50 bookmarks
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(updatedBookmarks));
    return { success: true, bookmark };
  } catch (error) {
    console.error('Error adding bookmark:', error);
    return { success: false, message: 'Failed to save bookmark' };
  }
};

// Remove a bookmark
export const removeBookmark = (id) => {
  try {
    const bookmarks = getBookmarks();
    const updatedBookmarks = bookmarks.filter(b => b.id !== id);
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(updatedBookmarks));
    return { success: true };
  } catch (error) {
    console.error('Error removing bookmark:', error);
    return { success: false, message: 'Failed to remove bookmark' };
  }
};

// Check if query is bookmarked
export const isBookmarked = (query) => {
  const bookmarks = getBookmarks();
  return bookmarks.some(b => b.query.toLowerCase() === query.toLowerCase().trim());
};

// Search bookmarks
export const searchBookmarks = (searchTerm) => {
  const bookmarks = getBookmarks();
  if (!searchTerm) return bookmarks;
  
  const term = searchTerm.toLowerCase();
  return bookmarks.filter(b => 
    b.query.toLowerCase().includes(term) || 
    b.title.toLowerCase().includes(term)
  );
};

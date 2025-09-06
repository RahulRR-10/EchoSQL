function Footer() {
  return (
    <footer className="py-6 mt-10 w-full border-t-2" style={{ 
      background: 'var(--bg-card)', 
      color: 'var(--text-muted)',
      borderColor: 'var(--border-primary)'
    }}>
      <div className="max-w-4xl mx-auto text-center space-y-4">
        <p className="text-sm sm:text-base">
          © {new Date().getFullYear()} EchoSQL. All rights reserved.
        </p>
        <div className="flex justify-center space-x-6">
          <a href="#" className="transition-colors hover:opacity-80" style={{ color: 'var(--text-muted)' }}>
            Privacy Policy
          </a>
          <a href="#" className="transition-colors hover:opacity-80" style={{ color: 'var(--text-muted)' }}>
            Terms of Service
          </a>
          <a href="#" className="transition-colors hover:opacity-80" style={{ color: 'var(--text-muted)' }}>
            Contact Us
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

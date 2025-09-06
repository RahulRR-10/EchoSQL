import Navbar from "../components/Navbar";
import DemoChat from "../components/DemoChat";
import CardSection from "../components/CardSection";
import Features from "../components/Features";
import Footer from "../components/Footer";

function Home() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <Navbar />
      <DemoChat />
      <CardSection />
      <Features />
      <Footer />
    </div>
  );
}

export default Home;

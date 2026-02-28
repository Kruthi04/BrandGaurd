import { useNavigate } from "react-router-dom";
import Hero from "@/components/ui/animated-shader-hero";

export default function Home() {
  const navigate = useNavigate();

  return (
    <Hero
      trustBadge={{
        text: "AI-Powered Brand Protection",
        icons: ["🛡️"],
      }}
      headline={{
        line1: "Protect Your",
        line2: "Brand Identity",
      }}
      subtitle="Monitor, detect, and correct brand misrepresentations across AI platforms in real-time — powered by intelligent agents and knowledge graphs."
      buttons={{
        primary: {
          text: "Go to Dashboard",
          onClick: () => navigate("/dashboard"),
        },
        secondary: {
          text: "Start Monitoring",
          onClick: () => navigate("/monitoring"),
        },
      }}
    />
  );
}

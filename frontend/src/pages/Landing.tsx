import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { BackgroundPaths } from "@/components/ui/background-paths";
import {
  Shield,
  Radar,
  GitFork,
  AlertTriangle,
  Search,
  Brain,
  Globe,
  Zap,
} from "lucide-react";

const features = [
  {
    icon: Radar,
    title: "Real-Time Monitoring",
    desc: "Yutori scouts continuously track what AI platforms say about your brand across ChatGPT, Claude, Perplexity, and Gemini.",
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Search,
    title: "Source Investigation",
    desc: "Tavily-powered search traces misinformation back to its origin, extracting content from flagged websites.",
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    icon: GitFork,
    title: "Knowledge Graph",
    desc: "Neo4j maps the propagation network: which sources feed which AI platforms, and how claims spread.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  {
    icon: Brain,
    title: "AI Agent Orchestration",
    desc: "Autonomous pipeline detects, investigates, and generates corrections for brand misrepresentations.",
    color: "text-purple-500",
    bg: "bg-purple-500/10",
  },
  {
    icon: AlertTriangle,
    title: "Threat Detection",
    desc: "Severity-ranked alerts surface critical misinformation with accuracy scores and suggested corrections.",
    color: "text-red-500",
    bg: "bg-red-500/10",
  },
  {
    icon: Globe,
    title: "YouTube & Audio Analysis",
    desc: "Modulate-powered video analysis detects brand mentions in podcasts and YouTube content.",
    color: "text-cyan-500",
    bg: "bg-cyan-500/10",
  },
];

const stats = [
  { value: "4", label: "AI Platforms Monitored" },
  { value: "200+", label: "Mentions Tracked" },
  { value: "< 6h", label: "Detection Latency" },
  { value: "3", label: "Brands Protected" },
];

const techStack = [
  { name: "Tavily", role: "Search & Crawl" },
  { name: "Neo4j", role: "Knowledge Graph" },
  { name: "Yutori", role: "AI Monitoring" },
  { name: "Modulate", role: "Audio Analysis" },
  { name: "FastAPI", role: "Backend API" },
  { name: "React", role: "Dashboard" },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="bg-white dark:bg-neutral-950">
      {/* Hero */}
      <BackgroundPaths
        title="BrandGuard"
        subtitle="Autonomous AI reputation monitoring and brand protection. Detect misinformation across ChatGPT, Claude, Perplexity, and Gemini — before it damages your brand."
        buttonText="Open Dashboard"
        onButtonClick={() => navigate("/dashboard")}
      >
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="flex items-center justify-center gap-2 mb-8"
        >
          <Shield className="h-6 w-6 text-neutral-500" />
          <span className="text-sm font-medium text-neutral-500 tracking-wider uppercase">
            AI-Powered Brand Protection
          </span>
        </motion.div>
      </BackgroundPaths>

      {/* Stats bar */}
      <div className="border-y border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900/50">
        <div className="container mx-auto px-4 md:px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold tracking-tight text-neutral-900 dark:text-white">
                  {stat.value}
                </div>
                <div className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <section className="py-24">
        <div className="container mx-auto px-4 md:px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-neutral-900 dark:text-white mb-4">
              Complete Protection Pipeline
            </h2>
            <p className="text-lg text-neutral-500 dark:text-neutral-400 max-w-2xl mx-auto">
              Six integrated capabilities that detect, trace, and correct AI-generated misinformation about your brand.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.5 }}
                className="group relative rounded-2xl border border-neutral-200 dark:border-neutral-800 p-6 
                  hover:border-neutral-300 dark:hover:border-neutral-700 
                  hover:shadow-lg transition-all duration-300 bg-white dark:bg-neutral-900/50"
              >
                <div className={`inline-flex p-3 rounded-xl ${f.bg} mb-4`}>
                  <f.icon className={`h-6 w-6 ${f.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-2">
                  {f.title}
                </h3>
                <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">
                  {f.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900/30">
        <div className="container mx-auto px-4 md:px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-neutral-900 dark:text-white mb-2">
              Built With
            </h2>
            <p className="text-neutral-500 dark:text-neutral-400">
              Hackathon sponsor technologies, seamlessly integrated.
            </p>
          </motion.div>

          <div className="flex flex-wrap justify-center gap-4">
            {techStack.map((tech, i) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05, duration: 0.3 }}
                className="flex items-center gap-3 rounded-xl border border-neutral-200 dark:border-neutral-800 
                  px-5 py-3 bg-white dark:bg-neutral-900/80 hover:shadow-md transition-shadow"
              >
                <Zap className="h-4 w-4 text-amber-500" />
                <div>
                  <div className="text-sm font-semibold text-neutral-900 dark:text-white">{tech.name}</div>
                  <div className="text-xs text-neutral-500">{tech.role}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-24">
        <div className="container mx-auto px-4 md:px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-neutral-900 dark:text-white mb-4">
              Protect Your Brand Today
            </h2>
            <p className="text-neutral-500 dark:text-neutral-400 mb-8 max-w-lg mx-auto">
              See what AI platforms are saying about your brand — and take control of the narrative.
            </p>
            <button
              onClick={() => navigate("/dashboard")}
              className="inline-flex items-center gap-2 rounded-xl bg-neutral-900 dark:bg-white 
                px-8 py-4 text-lg font-semibold text-white dark:text-neutral-900
                hover:bg-neutral-800 dark:hover:bg-neutral-100 
                shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5"
            >
              <Shield className="h-5 w-5" />
              Launch Dashboard
            </button>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

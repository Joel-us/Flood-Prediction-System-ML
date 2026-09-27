import { Link } from "@tanstack/react-router";
import { Menu, Moon, Settings, Sun, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import floodVisionLogo from "@/assets/floodvision-logo.png";

type NavbarProps = {
  dark: boolean;
  onThemeChange: () => void;
  onNavigate: (id: string) => void;
};

export function Navbar({
  dark,
  onThemeChange,
  onNavigate,
}: NavbarProps) {
  const [open, setOpen] = useState(false);

  const links: Array<{ label: string; id: string }> = [
    { label: "Home", id: "home" },
    { label: "Weather", id: "weather" },
    { label: "Flood Risk", id: "risk" },
    { label: "About", id: "about" },
  ];

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-hero-border bg-hero/85 text-hero-foreground backdrop-blur-xl">
      <div className="mx-auto grid h-16 max-w-7xl grid-cols-[minmax(0,1fr)_auto] items-center px-4 sm:px-6 lg:px-8">
        
        {/* FloodVision Logo */}
        <Link
          to="/"
          className="flex min-w-0 items-center gap-2.5"
          aria-label="FloodVision home"
        >
          <img
            src={floodVisionLogo}
            alt="FloodVision logo"
            className="h-10 w-10 shrink-0 object-contain"
          />

          <span className="truncate text-base font-bold">
            FloodVision
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav
          className="hidden items-center gap-1 md:flex"
          aria-label="Main navigation"
        >
          {links.map(({ label, id }) => (
            <Button
              key={id}
              variant="nav"
              size="sm"
              onClick={() => onNavigate(id)}
            >
              {label}
            </Button>
          ))}

          <span className="mx-2 h-5 w-px bg-hero-border" />

          {/* Theme Toggle */}
          <Button
            variant="nav"
            size="icon"
            onClick={onThemeChange}
            aria-label={dark ? "Use light theme" : "Use dark theme"}
            title={dark ? "Light theme" : "Dark theme"}
          >
            {dark ? <Sun /> : <Moon />}
          </Button>

          {/* Settings */}
          <Button
            variant="nav"
            size="icon"
            aria-label="Settings"
            title="Settings"
          >
            <Settings />
          </Button>
        </nav>

        {/* Mobile Menu Button */}
        <Button
          variant="nav"
          size="icon"
          className="md:hidden"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
        >
          {open ? <X /> : <Menu />}
        </Button>
      </div>

      {/* Mobile Navigation */}
      {open && (
        <nav
          className="border-t border-hero-border bg-hero px-4 py-3 md:hidden"
          aria-label="Mobile navigation"
        >
          {links.map(({ label, id }) => (
            <Button
              key={id}
              variant="nav"
              className="w-full justify-start"
              onClick={() => {
                onNavigate(id);
                setOpen(false);
              }}
            >
              {label}
            </Button>
          ))}

          {/* Mobile Theme Toggle */}
          <Button
            variant="nav"
            className="w-full justify-start"
            onClick={onThemeChange}
          >
            {dark ? <Sun /> : <Moon />}
            {dark ? "Light theme" : "Dark theme"}
          </Button>

          {/* Mobile Settings */}
          <Button
            variant="nav"
            className="w-full justify-start"
            onClick={() => setOpen(false)}
          >
            <Settings />
            Settings
          </Button>
        </nav>
      )}
    </header>
  );
}

export function Footer({
  onNavigate,
}: {
  onNavigate: (id: string) => void;
}) {
  return (
    <footer className="border-t border-border bg-surface-strong py-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 px-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        
        {/* Footer Branding */}
        <div className="flex items-center gap-3">
          <img
            src={floodVisionLogo}
            alt="FloodVision logo"
            className="h-10 w-10 object-contain"
          />

          <div>
            <p className="font-bold">FloodVision</p>
            <p className="text-sm text-muted-foreground">
              Stay informed. Stay prepared.
            </p>
          </div>
        </div>

        {/* Footer Navigation */}
        <nav
          className="flex flex-wrap gap-5 text-sm text-muted-foreground"
          aria-label="Footer navigation"
        >
          <button
            onClick={() => onNavigate("about")}
            className="hover:text-foreground"
          >
            About
          </button>

          <button
            onClick={() => onNavigate("privacy")}
            className="hover:text-foreground"
          >
            Privacy
          </button>

          <button
            onClick={() => onNavigate("disclaimer")}
            className="hover:text-foreground"
          >
            Disclaimer
          </button>
        </nav>
      </div>
    </footer>
  );
}